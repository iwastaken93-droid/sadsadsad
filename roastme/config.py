"""Configuration management — BYOK, bring your own API URL."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import dotenv

CONFIG_DIR = Path.home() / ".roastme"
CONFIG_FILE = CONFIG_DIR / "config.env"
ROAST_LEVELS = {"mild": 1, "medium": 2, "savage": 3, "nuclear": 4}

dotenv.load_dotenv(CONFIG_FILE)


@dataclass
class RoastConfig:
    api_key: str = ""
    api_base: str = "https://api.openai.com/v1"
    model: str = "gpt-4o"
    roast_level: str = "savage"
    persona: str = "disappointed_mentor"
    max_tokens: int = 1024
    temperature: float = 0.9
    language: str = "python"

    @classmethod
    def load(cls) -> RoastConfig:
        CONFIG_DIR.mkdir(exist_ok=True)
        if not CONFIG_FILE.exists():
            CONFIG_FILE.write_text(
                'api_key=""\n'
                'api_base="https://api.openai.com/v1"\n'
                'model="gpt-4o"\n'
                'roast_level="savage"\n'
                'persona="disappointed_mentor"\n'
            )
        dotenv.load_dotenv(CONFIG_FILE, override=True)
        return cls(
            api_key=os.getenv("ROASTME_API_KEY", ""),
            api_base=os.getenv("ROASTME_API_BASE", "https://api.openai.com/v1"),
            model=os.getenv("ROASTME_MODEL", "gpt-4o"),
            roast_level=os.getenv("ROASTME_ROAST_LEVEL", "savage"),
            persona=os.getenv("ROASTME_PERSONA", "disappointed_mentor"),
        )

    def save(self) -> None:
        CONFIG_DIR.mkdir(exist_ok=True)
        CONFIG_FILE.write_text(
            f'api_key="{self.api_key}"\n'
            f'api_base="{self.api_base}"\n'
            f'model="{self.model}"\n'
            f'roast_level="{self.roast_level}"\n'
            f'persona="{self.persona}"\n'
        )
