from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from configs.logging_config import get_logger
import asyncio
from typing import Optional, Callable, Any
import math

logger = get_logger(__name__)

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

class BrowserManager:
    _instance = None
    _browser = None
    _context = None
    _page = None
    _timeout_manager = TimeoutManager()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BrowserManager, cls).__new__(cls)
        return cls._instance

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

    async def wait_for_selector(self, selector: str, state: str = "visible", timeout: Optional[int] = None) -> bool:
        """Wait for a selector with timeout management"""
        try:
            page = await self.get_page()
            if timeout is None:
                timeout = self._timeout_manager.get_timeout()
            
            await page.wait_for_selector(selector, state=state, timeout=timeout)
            return True
        except Exception as e:
            logger.error(f"Failed to wait for selector {selector}: {str(e)}")
            return False

    async def navigate_to(self, url: str, wait_for: str = "domcontentloaded") -> bool:
        """Navigate to a URL with appropriate load state waiting"""
        try:
            page = await self.get_page()
            self._timeout_manager.reset()
            
            async def navigation_operation():
                await page.goto(url)
                await page.wait_for_load_state(wait_for)
                return True

            success = await self._timeout_manager.with_timeout(navigation_operation)
            if success:
                logger.info(f"Navigated to {url} with {wait_for} state")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {str(e)}")
            return False

    async def fill_field(self, selector: str, value: str, delay: int = 100) -> bool:
        """Fill a form field with a small delay to simulate human typing"""
        try:
            if await self.wait_for_selector(selector):
                page = await self.get_page()
                await page.fill(selector, value)
                await asyncio.sleep(delay/1000)  # Convert ms to seconds
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to fill field {selector}: {str(e)}")
            return False

    async def click(self, selector: str, wait_for: str = "load") -> bool:
        """Click an element and wait for appropriate load state"""
        try:
            if await self.wait_for_selector(selector):
                page = await self.get_page()
                await page.click(selector)
                await page.wait_for_load_state(wait_for)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to click {selector}: {str(e)}")
            return False

    async def close(self):
        """Close the browser and cleanup resources"""
        if self._browser:
            await self._browser.close()
            self._browser = None
            self._context = None
            self._page = None
            logger.info("Browser closed successfully") 