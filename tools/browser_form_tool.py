from agents import function_tool
from playwright.async_api import async_playwright
from configs.env_config import LINKEDIN_EMAIL, LINKEDIN_PASSWORD
from configs.logging_config import get_logger
import asyncio

logger = get_logger(__name__)

async def login_to_linkedin(page, context):
    """Handles LinkedIn login process with appropriate delays"""
    try:
        logger.info("Starting LinkedIn login process...")
        await page.goto("https://www.linkedin.com/login")
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)  # Wait for page to stabilize

        # Fill in credentials with delays
        logger.info("Entering credentials...")
        await page.fill('input[name="session_key"]', LINKEDIN_EMAIL)
        await asyncio.sleep(1)
        await page.fill('input[name="session_password"]', LINKEDIN_PASSWORD)
        await asyncio.sleep(1)

        # Click login button
        logger.info("Submitting login form...")
        await page.click('button[type="submit"]')
        await page.wait_for_load_state('networkidle')
        
        # Wait for verification with 1-second checks up to 15 seconds
        logger.info("Waiting for verification...")
        max_wait_time = 15  # Maximum wait time in seconds
        check_interval = 1  # Check every 1 second
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            if await page.is_visible('nav[aria-label="Main navigation"]'):
                logger.info("Successfully logged in to LinkedIn")

                return True
            await asyncio.sleep(check_interval)
            elapsed_time += check_interval
            logger.info(f"Waiting for verification... ({elapsed_time}s elapsed)")
        
        logger.error("Login verification timeout - navigation not found after 15 seconds")
        logger.debug('Page content: %s', await page.content())
        

        return False

    except Exception as e:
        logger.error(f"Login process failed: {str(e)}")
        return False

async def process_job_application(page, job_url):
    """Handles the job application process"""
    try:
        logger.info(f"Navigating to job: {job_url}")
        await page.goto(job_url)
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(3)  # Wait for job page to load

        if await page.is_visible("button:has-text('Easy Apply')"):
            logger.info("Easy Apply button found, clicking...")
            await page.click("button:has-text('Easy Apply')")
            await asyncio.sleep(2)

            if await page.is_visible('input[aria-label="Phone number"]'):
                logger.info("Filling phone number field...")
                await page.fill('input[aria-label="Phone number"]', '1234567890')
                await asyncio.sleep(1)
                logger.debug('Page content: %s', await page.content())
            else:
                logger.warning("Phone number field not found on the form")

            logger.info("Form partially filled. Stopping before submission.")
            return True
        else:
            logger.warning("Easy Apply button not found on the job posting")
            return False

    except Exception as e:
        logger.error(f"Job application process failed: {str(e)}")
        return False

@function_tool
async def browser_form_tool(job_url: str):
    """Navigates to a LinkedIn job post and fills out the Easy Apply form"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        # await browser.start_tracing(page, path="browser_trace.json")

        try:
            login_success = await login_to_linkedin(page, context)
            if not login_success:
                logger.debug('Page content: %s', await page.content())
                logger.debug('Page content: %s', await context.cookies())

                logger.error("Login failed, aborting job application process")
                await browser.close()
                return "Failed to login to LinkedIn"

            # If login successful, proceed with job application
            application_success = await process_job_application(page, job_url)
            if not application_success:
                logger.error("Job application process failed")
                await browser.close()
                return "Failed to process job application"

            await browser.close()
            return "Successfully processed job application form"

        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            await browser.close()
            raise
