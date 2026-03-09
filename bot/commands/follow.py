from discord import Client, Interaction, Message
from discord.app_commands import Choice, CommandTree, choices, describe

import bot.store
from bot.adapters.base import PlatformAdapter
from bot.commands.forward import forward_content
from bot.config import LANGUAGE_CHOICES, STORE_PATH, Settings

# channel_id -> target language code (or None)
_followed_channels: dict[int, str | None] = {}


def setup_follow(
    tree: CommandTree,
    client: Client,
    adapter: PlatformAdapter,
    settings: Settings,
) -> None:
    """Register /follow, /unfollow commands and the on_message listener."""
    _followed_channels.update(bot.store.load_channels(STORE_PATH))

    @tree.command(name="follow", description="Follow this channel to auto-forward new messages.")
    @describe(translate_to="Optional: target language to translate to.")
    @choices(translate_to=LANGUAGE_CHOICES)
    async def follow_command(
        interaction: Interaction,
        translate_to: Choice[str] | None = None,
    ) -> None:
        _followed_channels[interaction.channel_id] = translate_to.value if translate_to else None
        await interaction.response.send_message(
            f"Following {interaction.channel.mention}.", ephemeral=True
        )
        bot.store.save_channels(STORE_PATH, _followed_channels)

    @tree.command(name="unfollow", description="Unfollow this channel to stop auto-forwards.")
    async def unfollow_command(interaction: Interaction) -> None:
        _followed_channels.pop(interaction.channel_id, None)
        await interaction.response.send_message(
            f"Unfollowed {interaction.channel.mention}.", ephemeral=True
        )
        bot.store.save_channels(STORE_PATH, _followed_channels)

    @client.event
    async def on_message(message: Message) -> None:
        channel_id = message.channel.id

        if channel_id not in _followed_channels:
            return

        if message.author.bot:
            return

        text = message.content
        attachments = message.attachments
        lang = _followed_channels.get(channel_id)

        try:
            await forward_content(text, attachments, adapter, settings.deepl_api_key, lang)
        except Exception:
            return
