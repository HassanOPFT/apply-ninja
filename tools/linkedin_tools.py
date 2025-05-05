from agents import function_tool, Agent, Runner
from utils.workflow_browser_manager import WorkflowBrowserManager
from utils.linkedin_manager import LinkedInManager
from configs.logging_config import get_logger
from configs.env_config import LINKEDIN_EMAIL, LINKEDIN_PASSWORD
import asyncio

logger = get_logger(__name__)
browser_manager = WorkflowBrowserManager()

@function_tool
async def handle_linkedin_login() -> bool:
    """
    Handle the LinkedIn login process using the LinkedInManager.
    This tool will:
    1. Initialize browser and load cookies
    2. Check if already logged in
    3. If not logged in, perform login
    4. Save cookies if successful
    """
    try:
        # Initialize LinkedIn manager
        linkedin_manager = LinkedInManager()
        if not await linkedin_manager.initialize():
            logger.error("Failed to initialize LinkedIn manager")
            return False

        # Check if already logged in
        if await linkedin_manager.check_login_status():
            return True

        # Perform login if needed
        return await linkedin_manager.perform_login()
        
    except Exception as e:
        logger.error(f"Login workflow failed: {str(e)}")
        return False

@function_tool
async def handle_job_application(job_url: str) -> bool:
    """
    Handle the job application process using an internal agent.
    This tool will:
    1. Navigate to the job page
    2. Check for Easy Apply
    3. Handle the application process
    """
    try:
        # Create application agent
        app_agent = Agent(
            name="Job Application Agent",
            instructions="""You are a specialized agent for handling LinkedIn job applications.
            You will receive the job page content and need to:
            1. Find the Easy Apply button
            2. Handle the application form
            3. Track progress
            
            Return a JSON with:
            {
                "status": "success" | "error" | "in_progress",
                "message": "Current state",
                "next_action": "click_easy_apply" | "fill_form" | "submit" | "none"
            }""",
            tools=[]
        )
        
        # Navigate to job page
        await browser_manager.navigate_to(job_url)
        page_content = await browser_manager.get_page_content()
        
        # Run application agent
        result = await Runner.run(app_agent, f"Analyze job page: {page_content}")
        response = eval(result.output)
        
        # Handle application based on agent's response
        if response["next_action"] == "click_easy_apply":
            # Create click agent
            click_agent = Agent(
                name="Button Click Agent",
                instructions="""Find and click the Easy Apply button.
                Return a JSON with:
                {
                    "status": "success" | "error",
                    "selector": "CSS selector for the button"
                }""",
                tools=[]
            )
            
            click_result = await Runner.run(click_agent, f"Find Easy Apply button in: {page_content}")
            click_response = eval(click_result.output)
            
            if click_response["status"] == "success":
                # Click the button and continue application
                # ... (similar pattern for form filling)
                pass
        
        return response["status"] == "success"
        
    except Exception as e:
        logger.error(f"Job application workflow failed: {str(e)}")
        return False 