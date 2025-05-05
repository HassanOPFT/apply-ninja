from typing import Optional
from configs.logging_config import get_logger
from configs.env_config import LINKEDIN_EMAIL, LINKEDIN_PASSWORD
from utils.workflow_browser_manager import WorkflowBrowserManager
from custom_agents.linkedin_login_agent import LinkedInLoginAgent

logger = get_logger(__name__)

class LinkedInManager:
    def __init__(self):
        self.browser_manager = WorkflowBrowserManager()
        self.login_agent = LinkedInLoginAgent()

    async def initialize(self) -> bool:
        """Initialize the browser and load cookies"""
        try:
            await self.browser_manager.initialize()
            await self.browser_manager.load_cookies()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize LinkedIn manager: {str(e)}")
            return False

    async def perform_login(self) -> bool:
        """Perform the actual login operation with credentials"""
        try:
            # Navigate to login page if not already there
            await self.browser_manager.navigate_to("https://www.linkedin.com/login")
            
            # TODO: Finish this logic using selectors
            # Fill in credentials
            await self.browser_manager.fill_form({
                "username": LINKEDIN_EMAIL,
                "password": LINKEDIN_PASSWORD
            })
            
            # Submit form
            await self.browser_manager.submit_form()
            
            # Wait for navigation and save cookies
            await self.browser_manager.wait_for_navigation()
            await self.browser_manager.save_cookies()
            
            return True
        except Exception as e:
            logger.error(f"Login operation failed: {str(e)}")
            return False

    async def check_login_status(self) -> bool:
        """Check if we're currently logged in to LinkedIn"""
        try:
            # Get current page content
            page_content = await self.browser_manager.get_page_content()
            
            if not page_content:
                await self.browser_manager.navigate_to("https://www.linkedin.com/feed")
                page_content = await self.browser_manager.get_page_content()
            
            # TODO: Might not need agent for this
            # Analyze page with login agent
            analysis = await self.login_agent.analyze_page(page_content)
            
            if analysis["status"] == "logged_in":
                logger.info("Already logged in to LinkedIn")
                return True
                
            return False
        except Exception as e:
            logger.error(f"Failed to check login status: {str(e)}")
            return False 