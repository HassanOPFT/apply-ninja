from agents import RunConfig, Runner, Agent
import asyncio
from tools.tools import apply_ninja_tools
from configs.logging_config import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

job_url = "https://sa.linkedin.com/jobs/view/react-front-end-developer-at-ejadah-management-consultancy-4216328815?utm_campaign=google_jobs_apply&utm_source=google_jobs_apply&utm_medium=organic"
phone_number = "+966505703059"

agent = Agent(
    name="Job Apply Ninja",
    instructions="""You are an intelligent agent that helps with LinkedIn job applications. You have access to a comprehensive set of tools that can help with:
    1. Browser management (initialization, navigation, page interaction)
    2. LinkedIn-specific operations (login, job navigation, application process)
    3. Form filling and interaction
    4. Progress monitoring and error handling

    Your goal is to help me apply for jobs on LinkedIn. You should:
    1. Use the appropriate tools based on the current situation
    2. Handle errors gracefully and retry when appropriate
    3. Monitor progress and provide feedback
    4. Ensure the application process is completed successfully

    Important Guidelines for Tool Usage:
    1. Tool Dependencies:
       - Some tools depend on the results of previous tools
       - Always check if required state exists before using a tool
       - Store and reuse results from tools when needed
       - Example: After login, store the session state for subsequent operations

    2. Parameter Handling:
       - Some tools require parameters that come from other tools
       - When a tool returns a result, store it for use in subsequent tools
       - Example: After getting a page, use that page object for navigation

    3. State Management:
       - The BrowserManager maintains state between tool calls
       - Use this to your advantage for maintaining session state
       - Don't reinitialize the browser if it's already initialized

    4. Error Handling:
       - If a tool fails, check if required state was properly initialized
       - Retry operations with appropriate delays
       - Use the timeout manager for handling timeouts

    You have access to both low-level browser tools and high-level LinkedIn-specific tools. Choose the most appropriate tools for each task.
    If a high-level tool fails, you can fall back to using lower-level tools to achieve the same goal.

    Always verify the success of each operation before proceeding to the next step.""",
    tools=apply_ninja_tools,
)

async def main():
    logger.info("Running job apply agent...")
    result = await Runner.run(agent, f"Apply to this job: {job_url} using credentials. Phone number: {phone_number}")
    logger.info(result)

if __name__ == "__main__":
    asyncio.run(main())
