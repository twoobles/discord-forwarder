from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.commands.follow import _followed_channels, setup_follow


def _make_interaction(channel_id: int = 123) -> MagicMock:
    interaction = AsyncMock()
    interaction.channel_id = channel_id
    interaction.channel = MagicMock()
    interaction.channel.mention = "#test-channel"
    interaction.response = AsyncMock()
    return interaction


def _make_message(channel_id: int = 123, bot: bool = False, content: str = "hi") -> MagicMock:
    msg = MagicMock()
    msg.channel = MagicMock()
    msg.channel.id = channel_id
    msg.author = MagicMock()
    msg.author.bot = bot
    msg.content = content
    msg.attachments = []
    return msg


def _setup() -> tuple[dict, MagicMock, MagicMock]:
    """Register commands and return (registered_callbacks, adapter, settings)."""
    tree = MagicMock()
    client = MagicMock()
    adapter = AsyncMock()
    settings = MagicMock()
    settings.deepl_api_key = "fake-key"

    # Collect registered callbacks
    callbacks: dict[str, object] = {}

    def capture_command(**kwargs):
        def decorator(func):
            callbacks[kwargs.get("name", func.__name__)] = func
            return func

        return decorator

    tree.command = capture_command
    client.event = lambda fn: callbacks.update({"on_message": fn}) or fn

    _followed_channels.clear()
    with patch("bot.commands.follow.bot.store.load_channels", return_value={}):
        setup_follow(tree, client, adapter, settings)

    return callbacks, adapter, settings


class TestFollowCommand:
    @pytest.mark.asyncio
    async def test_follow_adds_channel(self) -> None:
        callbacks, _adapter, _settings = _setup()
        interaction = _make_interaction(channel_id=456)

        with patch("bot.commands.follow.bot.store.save_channels"):
            await callbacks["follow"](interaction, translate_to=None)

        assert 456 in _followed_channels
        assert _followed_channels[456] is None

    @pytest.mark.asyncio
    async def test_follow_with_language(self) -> None:
        callbacks, _adapter, _settings = _setup()
        interaction = _make_interaction(channel_id=789)
        choice = MagicMock()
        choice.value = "ZH"

        with patch("bot.commands.follow.bot.store.save_channels"):
            await callbacks["follow"](interaction, translate_to=choice)

        assert _followed_channels[789] == "ZH"

    @pytest.mark.asyncio
    async def test_follow_sends_confirmation(self) -> None:
        callbacks, _adapter, _settings = _setup()
        interaction = _make_interaction()

        with patch("bot.commands.follow.bot.store.save_channels"):
            await callbacks["follow"](interaction, translate_to=None)

        interaction.response.send_message.assert_awaited_once()
        msg = interaction.response.send_message.call_args
        assert "#test-channel" in msg.args[0]


class TestUnfollowCommand:
    @pytest.mark.asyncio
    async def test_unfollow_removes_channel(self) -> None:
        callbacks, _adapter, _settings = _setup()
        _followed_channels[123] = None

        interaction = _make_interaction(channel_id=123)
        with patch("bot.commands.follow.bot.store.save_channels"):
            await callbacks["unfollow"](interaction)

        assert 123 not in _followed_channels

    @pytest.mark.asyncio
    async def test_unfollow_noop_when_not_followed(self) -> None:
        callbacks, _adapter, _settings = _setup()
        interaction = _make_interaction(channel_id=999)

        with patch("bot.commands.follow.bot.store.save_channels"):
            await callbacks["unfollow"](interaction)

        assert 999 not in _followed_channels
        interaction.response.send_message.assert_awaited_once()


class TestOnMessage:
    @pytest.mark.asyncio
    async def test_forwards_message_from_followed_channel(self) -> None:
        callbacks, adapter, _settings = _setup()
        _followed_channels[123] = None
        msg = _make_message(channel_id=123, content="hello")

        with patch("bot.commands.follow.forward_content", new_callable=AsyncMock) as mock_fwd:
            await callbacks["on_message"](msg)
            mock_fwd.assert_awaited_once_with("hello", [], adapter, "fake-key", None)

    @pytest.mark.asyncio
    async def test_ignores_unfollowed_channel(self) -> None:
        callbacks, _adapter, _settings = _setup()
        msg = _make_message(channel_id=999)

        with patch("bot.commands.follow.forward_content", new_callable=AsyncMock) as mock_fwd:
            await callbacks["on_message"](msg)
            mock_fwd.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_ignores_bot_messages(self) -> None:
        callbacks, _adapter, _settings = _setup()
        _followed_channels[123] = None
        msg = _make_message(channel_id=123, bot=True)

        with patch("bot.commands.follow.forward_content", new_callable=AsyncMock) as mock_fwd:
            await callbacks["on_message"](msg)
            mock_fwd.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_passes_target_lang_to_forward(self) -> None:
        callbacks, adapter, _settings = _setup()
        _followed_channels[123] = "ZH"
        msg = _make_message(channel_id=123, content="hi")

        with patch("bot.commands.follow.forward_content", new_callable=AsyncMock) as mock_fwd:
            await callbacks["on_message"](msg)
            mock_fwd.assert_awaited_once_with("hi", [], adapter, "fake-key", "ZH")

    @pytest.mark.asyncio
    async def test_silently_handles_forward_error(self) -> None:
        callbacks, _adapter, _settings = _setup()
        _followed_channels[123] = None
        msg = _make_message(channel_id=123)

        with patch(
            "bot.commands.follow.forward_content",
            new_callable=AsyncMock,
            side_effect=Exception("boom"),
        ):
            # Should not raise
            await callbacks["on_message"](msg)
