import asyncio
import re

from deepl import QuotaExceededException
from discord import Forbidden, Interaction, NotFound
from discord.app_commands import CommandTree, describe

from bot.adapters.base import PlatformAdapter
from bot.config import Settings
from bot.translation import translate

MSG_LINK_RE = re.compile(r"https://discord\.com/channels/(\d+)/(\d+)/(\d+)")


def setup_forward(
    tree: CommandTree,
    adapter: PlatformAdapter,
    settings: Settings,
) -> None:
    @tree.command(name="forward", description="Forward a message.")
    @describe(
        message="Raw text or message link to read and forward.",
        translate_to="Optional: target language to translate to.",
    )
    async def forward_command(
        interaction: Interaction,
        message: str,
        translate_to: str | None = None,
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

        try:
            if translate_to and text:
                text = await asyncio.to_thread(
                    translate, text, translate_to, settings.deepl_api_key
                )
        except QuotaExceededException:
            await interaction.followup.send("Token translation quota exceeded.")
            return
        except Exception:
            await interaction.followup.send("Translation failed.")
            return

        try:
            if text:
                await adapter.send_text(text)

            for attachment in attachments:
                if attachment.content_type and attachment.content_type.startswith("image/"):
                    img_data = await attachment.read()
                    await adapter.send_image(img_data, attachment.filename)

        except Exception:
            await interaction.followup.send("Failed to forward message.")
            return

        await interaction.followup.send("Forwarded!")
