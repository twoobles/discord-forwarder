import discord
from discord import app_commands

from bot.adapters.wechat import WeChatWorkAdapter
from bot.commands.forward import setup_forward
from bot.config import load_settings


def main() -> None:
    settings = load_settings()

    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)
    adapter = WeChatWorkAdapter(url=settings.wechat_webhook_url)

    setup_forward(tree, adapter, settings)

    @client.event
    async def on_ready() -> None:
        await tree.sync()
        print(f"Logged in as {client.user}")

    client.run(settings.discord_token)


if __name__ == "__main__":
    main()
