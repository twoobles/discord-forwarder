import discord
from discord import app_commands

from bot.adapters.wechat import WeChatWorkAdapter
from bot.commands.follow import setup_follow
from bot.commands.forward import setup_forward
from bot.config import load_settings


def main() -> None:
    """Set up the Discord client, register commands, and start the bot."""
    settings = load_settings()

    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)
    adapter = WeChatWorkAdapter(url=settings.wechat_webhook_url)

    setup_forward(tree, adapter, settings)
    setup_follow(tree, client, adapter, settings)

    synced = False

    @client.event
    async def on_ready() -> None:
        nonlocal synced
        if synced:
            print(f"Reconnected as {client.user}")
            return

        if settings.discord_guild_id:
            guild = discord.Object(id=settings.discord_guild_id)
            tree.copy_global_to(guild=guild)
            await tree.sync(guild=guild)
            # Clear any stale global commands to prevent duplicates
            tree.clear_commands(guild=None)
            await tree.sync()
        else:
            await tree.sync()

        synced = True
        print(f"Logged in as {client.user}")

    client.run(settings.discord_token)


if __name__ == "__main__":
    main()
