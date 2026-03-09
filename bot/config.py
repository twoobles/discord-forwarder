import os
from dataclasses import dataclass

from discord.app_commands import Choice
from dotenv import load_dotenv

load_dotenv()

LANGUAGE_CHOICES = [Choice(name="Chinese", value="ZH"), Choice(name="English", value="EN-US")]
STORE_PATH = "data/followed.json"


@dataclass(frozen=True)
class Settings:
    discord_token: str
    wechat_webhook_url: str
    deepl_api_key: str
    discord_guild_id: int | None = None


def load_settings() -> Settings:
    """Load and validate all required environment variables."""
    guild_id = os.environ.get("DISCORD_GUILD_ID")
    return Settings(
        discord_token=os.environ["DISCORD_TOKEN"],
        wechat_webhook_url=os.environ["WECHAT_WEBHOOK_URL"],
        deepl_api_key=os.environ["DEEPL_API_KEY"],
        discord_guild_id=int(guild_id) if guild_id else None,
    )
