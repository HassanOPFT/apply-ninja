from agents import Agent, Runner
from typing import Dict, Any

class LinkedInLoginAgent:
    def __init__(self):
        self.agent = Agent(
            name="LinkedIn Login Agent",
            instructions="""You are a specialized agent for handling LinkedIn login.
            You will receive the current page content and need to determine:
            1. If we're already logged in
            2. If not, how to proceed with login
            
            Available actions:
            - Check if we're on the feed page (already logged in)
            - Check if we're on the login page
            - Check for any error messages
            
            Return a JSON with:
            {
                "status": "logged_in" | "needs_login" | "error",
                "message": "Description of current state",
                "action": "none" | "login" | "retry"
            }""",
            tools=[]  # No tools needed as we'll pass page content directly
        )

    async def analyze_page(self, page_content: str) -> Dict[str, Any]:
        """
        Analyze the page content to determine login status and required actions.
        
        Args:
            page_content: The HTML content of the current page
            
        Returns:
            Dict containing analysis results with keys:
            - status: "logged_in", "needs_login", or "error"
            - message: Description of current state
            - action: "none", "login", or "retry"
        """
        result = await Runner.run(self.agent, f"Analyze this page content: {page_content}")
        return eval(result.output)  # Convert string to dict 