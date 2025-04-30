from agents import Runner, Agent
import asyncio
from tools.browser_form_tool import browser_form_tool
from configs import env_config
from configs.logging_config import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

job_url = "https://sa.linkedin.com/jobs/view/react-front-end-developer-at-ejadah-management-consultancy-4216328815?utm_campaign=google_jobs_apply&utm_source=google_jobs_apply&utm_medium=organic"

agent = Agent(
    name="Job Apply Ninja",
    instructions="You are an assistant that fills LinkedIn Easy Apply forms with dummy data, without submitting.",
    tools=[
        browser_form_tool
    ]
)

async def main():
    logger.info("Running job apply agent...")
    result = await Runner.run(agent, f"Apply to this job: {job_url} using credentials.")
    logger.info(result)

if __name__ == "__main__":
    asyncio.run(main())
