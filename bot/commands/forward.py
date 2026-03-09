import asyncio
import re

from deepl import QuotaExceededException
from discord import Attachment, Forbidden, Interaction, NotFound
from discord.app_commands import Choice, CommandTree, choices, describe

from bot.adapters.base import PlatformAdapter
from bot.config import LANGUAGE_CHOICES, Settings
from bot.translation import translate

MSG_LINK_RE = re.compile(r"https://discord\.com/channels/(\d+)/(\d+)/(\d+)")


async def forward_content(
    text: str,
    attachments: list[Attachment],
    adapter: PlatformAdapter,
    deepl_api_key: str,
    target_lang: str | None = None,
) -> None:
    """Translate (optionally) and forward text and image attachments to the target platform.

    Raises deepl.QuotaExceededException or adapter errors — callers handle these.
    """
    if target_lang and text:
        text = await asyncio.to_thread(translate, text, target_lang, deepl_api_key)

    if text:
        await adapter.send_text(text)

    for attachment in attachments:
        if attachment.content_type and attachment.content_type.startswith("image/"):
            img_data = await attachment.read()
            await adapter.send_image(img_data, attachment.filename)


def setup_forward(
    tree: CommandTree,
    adapter: PlatformAdapter,
    settings: Settings,
) -> None:
    """Register the /forward slash command on the command tree."""

    @tree.command(name="forward", description="Forward a message.")
    @describe(
        message="Raw text or message link to read and forward.",
        translate_to="Optional: target language to translate to.",
    )
    @choices(translate_to=LANGUAGE_CHOICES)
    async def forward_command(
        interaction: Interaction,
        message: str,
        translate_to: Choice[str] | None = None,
    ) -> None:
        await interaction.response.defer(ephemeral=True)

        match = MSG_LINK_RE.fullmatch(message)
        if match:  # Message link
            guild_id = int(match.group(1))
            channel_id = int(match.group(2))
            message_id = int(match.group(3))

            guild = interaction.client.get_guild(guild_id)
            if guild is None:
                await interaction.followup.send("Unable to access server.")
                return
            channel = guild.get_channel(channel_id)
            if channel is None:
                await interaction.followup.send("Unable to access channel.")
                return

            try:
                res = await channel.fetch_message(message_id)

            except (NotFound, Forbidden):
                await interaction.followup.send("Unable to access message.")
                return

            text = res.content
            attachments = res.attachments

        else:  # Raw text
            text = message
            attachments = []

        lang = translate_to.value if translate_to else None

        try:
            await forward_content(text, attachments, adapter, settings.deepl_api_key, lang)
        except QuotaExceededException:
            await interaction.followup.send("Token translation quota exceeded.")
            return
        except Exception:
            await interaction.followup.send("Failed to forward message.")
            return

        await interaction.followup.send("Forwarded!")
