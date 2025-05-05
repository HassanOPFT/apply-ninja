from agents import function_tool
from utils.browser_manager import BrowserManager
from utils.cookie_manager import CookieManager
from configs.env_config import LINKEDIN_EMAIL, LINKEDIN_PASSWORD
from configs.logging_config import get_logger
import asyncio

logger = get_logger(__name__)
browser_manager = BrowserManager()
cookie_manager = CookieManager()

@function_tool
async def check_linkedin_login() -> bool:
    """Check if we're already logged in to LinkedIn"""
    try:
        await browser_manager.initialize()
        page = await browser_manager.get_page()
        
        cookies = cookie_manager.load_cookies()

        if cookies:
            logger.info("Found existing cookies, attempting to use them...")
            await page.context.add_cookies(cookies)

            if await browser_manager.navigate_to("https://www.linkedin.com/feed", wait_for="load"):
                if await browser_manager.wait_for_selector('main[aria-label="Main Feed"]'):
                    logger.info("Successfully logged in using saved cookies")
                    return True
                else:
                    logger.info("Saved cookies are invalid, proceeding with normal login")
                    cookie_manager.clear_cookies()
        
        return False
    except Exception as e:
        logger.error(f"Error checking LinkedIn login: {str(e)}")
        return False

@function_tool
async def login_to_linkedin() -> bool:
    """Perform LinkedIn login"""
    try:
        await browser_manager.initialize()
        
        logger.info("Starting LinkedIn login process...")
        
        if not await browser_manager.navigate_to("https://www.linkedin.com/login", wait_for="domcontentloaded"):
            return False
        
        if not await browser_manager.wait_for_selector('input[name="session_key"]'):
            logger.error("Login form not found")
            return False

        logger.info("Entering credentials...")
        if not await browser_manager.fill_field('input[name="session_key"]', LINKEDIN_EMAIL):
            return False
        if not await browser_manager.fill_field('input[name="session_password"]', LINKEDIN_PASSWORD):
            return False

        logger.info("Submitting login form...")
        if not await browser_manager.click('button[type="submit"]', wait_for="load"):
            return False
        
        # Wait for either success or error
        success = await browser_manager.wait_for_selector('main[aria-label="Main Feed"]')
        error = await browser_manager.wait_for_selector('.alert-error')
        
        if success:
            logger.info("Successfully logged in to LinkedIn")
            page = await browser_manager.get_page()
            cookies = await page.context.cookies()
            cookie_manager.save_cookies(cookies)
            return True
            
        if error:
            page = await browser_manager.get_page()
            error_text = await page.text_content('.alert-error')
            logger.error(f"Login failed: {error_text}")
            return False
            
        logger.error("Login verification timeout - neither success nor error detected")
        return False

    except Exception as e:
        logger.error(f"Login process failed: {str(e)}")
        return False

@function_tool
async def navigate_to_job(job_url: str) -> bool:
    """Navigate to a specific job posting"""
    try:
        await browser_manager.initialize()
        return await browser_manager.navigate_to(job_url, wait_for="load")
    except Exception as e:
        logger.error(f"Failed to navigate to job: {str(e)}")
        return False

@function_tool
async def click_easy_apply() -> bool:
    """Click the Easy Apply button on a LinkedIn job posting"""
    try:
        primary_selector = 'button[aria-label^="Easy Apply"][id="jobs-apply-button-id"]'
        
        fallback_selectors = [
            'button.jobs-apply-button.artdeco-button--primary',
            'div.jobs-apply-button--top-card button',
            'button[data-job-id]'
        ]
        
        logger.info("Looking for Easy Apply button...")
        if await browser_manager.wait_for_selector(primary_selector, timeout=5000):
            logger.info("Easy Apply button found with primary selector, clicking...")
            return await browser_manager.click(primary_selector, wait_for="load")
        
        for selector in fallback_selectors:
            logger.info(f"Trying fallback selector: {selector}")
            if await browser_manager.wait_for_selector(selector, timeout=2000):
                logger.info(f"Easy Apply button found with fallback selector: {selector}")
                return await browser_manager.click(selector, wait_for="load")
        
        logger.warning("Easy Apply button not found with any selector")
        return False
        
    except Exception as e:
        logger.error(f"Failed to click Easy Apply: {str(e)}")
        return False

@function_tool
async def fill_phone_number(phone: str) -> bool:
    """Fill in the phone number field in the application form"""
    try:
        if await browser_manager.wait_for_selector('input[aria-label="Phone number"]'):
            logger.info("Filling phone number field...")
            return await browser_manager.fill_field('input[aria-label="Phone number"]', phone)
        else:
            logger.warning("Phone number field not found")
            return False
    except Exception as e:
        logger.error(f"Failed to fill phone number: {str(e)}")
        return False 

@function_tool
async def wait_for_easy_apply_modal() -> bool:
    """Wait for the LinkedIn Easy Apply modal to appear and confirm it's visible"""
    try:
        # Primary selector for the modal container
        modal_selector = 'div[data-test-modal-id="easy-apply-modal"]'
        
        # Wait for the modal to become visible with a reasonable timeout
        logger.info("Waiting for Easy Apply modal to appear...")
        if await browser_manager.wait_for_selector(modal_selector, timeout=8000, visible=True):
            # Additional check to ensure modal is actually visible and not hidden
            is_visible = await browser_manager.evaluate(f"""
                document.querySelector('{modal_selector}').getAttribute('aria-hidden') === 'false'
            """)
            
            if is_visible:
                logger.info("Easy Apply modal is visible and ready for interaction")
                return True
            else:
                logger.warning("Easy Apply modal found but appears to be hidden")
                return False
        else:
            logger.warning("Easy Apply modal did not appear within timeout period")
            return False
            
    except Exception as e:
        logger.error(f"Error waiting for Easy Apply modal: {str(e)}")
        return False

@function_tool
async def close_easy_apply_modal() -> bool:
    """Close the LinkedIn Easy Apply modal by clicking the dismiss button"""
    try:
        # Primary selector for the close button
        close_button_selector = 'button[aria-label="Dismiss"][data-test-modal-close-btn]'
        
        # Fallback selector if the primary one changes
        fallback_selector = 'div[data-test-modal-id="easy-apply-modal"] button.artdeco-modal__dismiss'
        
        # Try primary selector first
        logger.info("Looking for modal close button...")
        if await browser_manager.wait_for_selector(close_button_selector, timeout=3000):
            logger.info("Modal close button found, clicking...")
            return await browser_manager.click(close_button_selector)
        
        # Try fallback if primary fails
        if await browser_manager.wait_for_selector(fallback_selector, timeout=2000):
            logger.info("Modal close button found with fallback selector, clicking...")
            return await browser_manager.click(fallback_selector)
            
        logger.warning("Modal close button not found")
        return False
        
    except Exception as e:
        logger.error(f"Failed to close Easy Apply modal: {str(e)}")
        return False

@function_tool
async def get_application_progress() -> int:
    """Get the current application progress percentage from the progress bar"""
    try:
        # Selector for the progress element
        progress_selector = 'div[data-test-modal-id="easy-apply-modal"] progress'
        
        # Wait for the progress element to be available
        if await browser_manager.wait_for_selector(progress_selector, timeout=3000):
            # Extract the current value and max value to calculate percentage
            progress_value = await browser_manager.evaluate(f"""
                document.querySelector('{progress_selector}').value
            """)
            
            # Return the progress as an integer
            return int(progress_value)
        else:
            logger.warning("Progress bar element not found")
            return 0
            
    except Exception as e:
        logger.error(f"Error getting application progress: {str(e)}")
        return 0
        
@function_tool
async def get_modal_header_text() -> str:
    """Get the header text from the Easy Apply modal"""
    try:
        # Selector for the modal header
        header_selector = 'div[data-test-modal-id="easy-apply-modal"] h2#jobs-apply-header'
        
        # Wait for the header element to be available
        if await browser_manager.wait_for_selector(header_selector, timeout=3000):
            # Extract the text content
            header_text = await browser_manager.evaluate(f"""
                document.querySelector('{header_selector}').textContent.trim()
            """)
            
            return header_text
        else:
            logger.warning("Modal header element not found")
            return ""
            
    except Exception as e:
        logger.error(f"Error getting modal header text: {str(e)}")
        return ""