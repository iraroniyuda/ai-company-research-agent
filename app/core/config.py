import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str | None


settings = Settings(
    gemini_api_key=os.getenv("GEMINI_API_KEY"),
)
