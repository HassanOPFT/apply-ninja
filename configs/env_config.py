import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("Please set OPENAI_API_KEY in your .env file or environment variables")

if not os.getenv("LINKEDIN_EMAIL"):
    raise ValueError("Please set LINKEDIN_EMAIL in your .env file or environment variables")

if not os.getenv("LINKEDIN_PASSWORD"):
    raise ValueError("Please set LINKEDIN_PASSWORD in your .env file or environment variables")