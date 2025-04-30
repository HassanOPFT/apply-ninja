from agents import Runner, Agent
import asyncio
from configs import env_config


agent = Agent(
    name="Math Tutor",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
    tools=[
        
    ]
)

async def main():
    print('Running...')
    result = await Runner.run(agent, "What is pythagorean theorem?")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())


