import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    discord_token: str
    wechat_webhook_url: str
    deepl_api_key: str


def load_settings() -> Settings:
    """Load and validate all required environment variables."""
    return Settings(
        discord_token=os.environ["DISCORD_TOKEN"],
        wechat_webhook_url=os.environ["WECHAT_WEBHOOK_URL"],
        deepl_api_key=os.environ["DEEPL_API_KEY"],
    )
