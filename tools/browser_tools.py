from agents import function_tool
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from configs.logging_config import get_logger
import asyncio
from typing import Optional, Callable, Any
import math

logger = get_logger(__name__)

class BrowserManager:
    _instance = None
    _browser = None
    _context = None
    _page = None
    _timeout_manager = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BrowserManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_timeout_manager'):
            self._timeout_manager = TimeoutManager()

    async def initialize(self):
        """Initialize the browser and context"""
        if not self._browser:
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.launch(headless=False)
            self._context = await self._browser.new_context()
            logger.info("Browser initialized successfully")

    async def get_page(self) -> Page:
        """Get or create a new page"""
        if not self._page:
            self._page = await self._context.new_page()
            logger.info("New page created")
        return self._page

    async def close(self):
        """Close the browser and cleanup resources"""
        if self._browser:
            await self._browser.close()
            self._browser = None
            self._context = None
            self._page = None
            logger.info("Browser closed successfully")

class TimeoutManager:
    """Manages timeouts with exponential backoff and dynamic adjustment"""
    
    def __init__(self, base_timeout: int = 30000, max_timeout: int = 120000):
        self.base_timeout = base_timeout
        self.max_timeout = max_timeout
        self.current_timeout = base_timeout
        self.attempts = 0
        self.max_attempts = 3

    def get_timeout(self) -> int:
        """Get current timeout with exponential backoff"""
        if self.attempts == 0:
            return self.base_timeout
        timeout = min(
            self.base_timeout * (2 ** self.attempts),
            self.max_timeout
        )
        return timeout

    def increment_attempt(self) -> None:
        """Increment attempt counter"""
        self.attempts += 1

    def reset(self) -> None:
        """Reset timeout state"""
        self.attempts = 0
        self.current_timeout = self.base_timeout

    async def with_timeout(self, operation: Callable, *args, **kwargs) -> Any:
        """Execute an operation with timeout management"""
        while self.attempts < self.max_attempts:
            try:
                timeout = self.get_timeout()
                logger.debug(f"Attempt {self.attempts + 1} with timeout {timeout}ms")
                return await asyncio.wait_for(operation(*args, **kwargs), timeout=timeout/1000)
            except asyncio.TimeoutError:
                self.increment_attempt()
                if self.attempts >= self.max_attempts:
                    raise
                logger.warning(f"Operation timed out, retrying with increased timeout (attempt {self.attempts})")
            except Exception as e:
                raise
        raise asyncio.TimeoutError(f"Operation failed after {self.max_attempts} attempts")

# Initialize browser manager
browser_manager = BrowserManager()

@function_tool
async def initialize_browser() -> bool:
    """Initialize the browser and context"""
    try:
        await browser_manager.initialize()
        return True
    except Exception as e:
        logger.error(f"Failed to initialize browser: {str(e)}")
        return False

@function_tool
async def get_page() -> Optional[Page]:
    """Get or create a new page"""
    try:
        return await browser_manager.get_page()
    except Exception as e:
        logger.error(f"Failed to get page: {str(e)}")
        return None

@function_tool
async def wait_for_selector(selector: str, state: str = "visible", timeout: Optional[int] = None) -> bool:
    """Wait for a selector with timeout management"""
    try:
        page = await browser_manager.get_page()
        if timeout is None:
            timeout = browser_manager._timeout_manager.get_timeout()
        
        await page.wait_for_selector(selector, state=state, timeout=timeout)
        return True
    except Exception as e:
        logger.error(f"Failed to wait for selector {selector}: {str(e)}")
        return False

@function_tool
async def navigate_to(url: str, wait_for: str = "domcontentloaded") -> bool:
    """Navigate to a URL with appropriate load state waiting"""
    try:
        page = await browser_manager.get_page()
        browser_manager._timeout_manager.reset()
        
        async def navigation_operation():
            await page.goto(url)
            await page.wait_for_load_state(wait_for)
            return True

        success = await browser_manager._timeout_manager.with_timeout(navigation_operation)
        if success:
            logger.info(f"Navigated to {url} with {wait_for} state")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to navigate to {url}: {str(e)}")
        return False

@function_tool
async def fill_field(selector: str, value: str, delay: int = 100) -> bool:
    """Fill a form field with a small delay to simulate human typing"""
    try:
        if await wait_for_selector(selector):
            page = await browser_manager.get_page()
            await page.fill(selector, value)
            await asyncio.sleep(delay/1000)  # Convert ms to seconds
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to fill field {selector}: {str(e)}")
        return False

@function_tool
async def click(selector: str, wait_for: str = "load") -> bool:
    """Click an element and wait for appropriate load state"""
    try:
        if await wait_for_selector(selector):
            page = await browser_manager.get_page()
            await page.click(selector)
            await page.wait_for_load_state(wait_for)
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to click {selector}: {str(e)}")
        return False

@function_tool
async def close_browser() -> bool:
    """Close the browser and cleanup resources"""
    try:
        await browser_manager.close()
        return True
    except Exception as e:
        logger.error(f"Failed to close browser: {str(e)}")
        return False

@function_tool
async def get_page_html() -> Optional[str]:
    """Get the HTML content of the current page"""
    try:
        page = await browser_manager.get_page()
        html = await page.content()
        return html
    except Exception as e:
        logger.error(f"Failed to get page HTML: {str(e)}")
        return None 