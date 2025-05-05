from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from configs.logging_config import get_logger
import asyncio
from typing import Optional, Dict, Any
import json
import os

logger = get_logger(__name__)

class WorkflowBrowserManager:
    _instance = None
    _browser: Optional[Browser] = None
    _context: Optional[BrowserContext] = None
    _page: Optional[Page] = None
    _cookies: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WorkflowBrowserManager, cls).__new__(cls)
        return cls._instance
    
    async def initialize(self) -> bool:
        """Initialize the browser and context"""
        try:
            if not self._browser:
                playwright = await async_playwright().start()
                self._browser = await playwright.chromium.launch(headless=False)
                self._context = await self._browser.new_context()
                logger.info("Browser initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize browser: {str(e)}")
            return False
    
    async def get_page(self) -> Optional[Page]:
        """Get or create a new page"""
        try:
            if not self._page:
                if not self._context:
                    await self.initialize()
                self._page = await self._context.new_page()
                logger.info("New page created")
            return self._page
        except Exception as e:
            logger.error(f"Failed to get page: {str(e)}")
            return None
    
    async def load_cookies(self) -> bool:
        """Load cookies from file if they exist"""
        try:
            cookie_file = "cookies.json"
            if os.path.exists(cookie_file):
                with open(cookie_file, 'r') as f:
                    self._cookies = json.load(f)
                if self._context and self._cookies:
                    await self._context.add_cookies(self._cookies)
                logger.info("Successfully loaded cookies")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to load cookies: {str(e)}")
            return False
    
    async def save_cookies(self) -> bool:
        """Save current cookies to file"""
        try:
            if self._context:
                cookies = await self._context.cookies()
                with open("cookies.json", 'w') as f:
                    json.dump(cookies, f)
                self._cookies = cookies
                logger.info("Successfully saved cookies")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to save cookies: {str(e)}")
            return False
    
    async def get_page_content(self) -> Optional[str]:
        """Get the HTML content of the current page"""
        try:
            if self._page:
                return await self._page.content()
            return None
        except Exception as e:
            logger.error(f"Failed to get page content: {str(e)}")
            return None
    
    async def close(self) -> bool:
        """Close the browser and cleanup resources"""
        try:
            if self._browser:
                await self._browser.close()
                self._browser = None
                self._context = None
                self._page = None
                logger.info("Browser closed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to close browser: {str(e)}")
            return False 