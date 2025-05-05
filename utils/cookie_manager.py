import json
import os
from pathlib import Path
from typing import List, Dict, Any
from configs.logging_config import get_logger

logger = get_logger(__name__)

class CookieManager:
    def __init__(self):
        self.cookie_dir = Path("cookies")
        self.cookie_dir.mkdir(exist_ok=True)
        self.cookie_file = self.cookie_dir / "linkedin_cookies.json"

    def save_cookies(self, cookies: List[Dict[str, Any]]) -> None:
        """Save cookies to a JSON file"""
        try:
            with open(self.cookie_file, 'w') as f:
                json.dump(cookies, f)
            logger.info("Successfully saved LinkedIn cookies")
        except Exception as e:
            logger.error(f"Failed to save cookies: {str(e)}")

    def load_cookies(self) -> List[Dict[str, Any]]:
        """Load cookies from JSON file"""
        try:
            if not self.cookie_file.exists():
                logger.info("No saved cookies found")
                return []
            
            with open(self.cookie_file, 'r') as f:
                cookies = json.load(f)
            logger.info("Successfully loaded LinkedIn cookies")
            return cookies
        except Exception as e:
            logger.error(f"Failed to load cookies: {str(e)}")
            return []

    def clear_cookies(self) -> None:
        """Clear saved cookies"""
        try:
            if self.cookie_file.exists():
                self.cookie_file.unlink()
            logger.info("Successfully cleared LinkedIn cookies")
        except Exception as e:
            logger.error(f"Failed to clear cookies: {str(e)}") 