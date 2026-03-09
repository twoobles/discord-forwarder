from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from deepl import QuotaExceededException

from bot.commands.forward import forward_content


def _make_attachment(content_type: str = "image/png", filename: str = "img.png") -> MagicMock:
    att = MagicMock()
    att.content_type = content_type
    att.filename = filename
    att.read = AsyncMock(return_value=b"fake-image-bytes")
    return att


class TestForwardContent:
    @pytest.mark.asyncio
    async def test_forwards_text_only(self) -> None:
        adapter = AsyncMock()

        await forward_content("hello", [], adapter, "key")

        adapter.send_text.assert_awaited_once_with("hello")
        adapter.send_image.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_forwards_image_attachment(self) -> None:
        adapter = AsyncMock()
        att = _make_attachment()

        await forward_content("", [att], adapter, "key")

        adapter.send_text.assert_not_awaited()
        adapter.send_image.assert_awaited_once_with(b"fake-image-bytes", "img.png")

    @pytest.mark.asyncio
    async def test_skips_non_image_attachment(self) -> None:
        adapter = AsyncMock()
        att = _make_attachment(content_type="application/pdf", filename="doc.pdf")

        await forward_content("", [att], adapter, "key")

        adapter.send_image.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_forwards_text_and_images(self) -> None:
        adapter = AsyncMock()
        att = _make_attachment()

        await forward_content("caption", [att], adapter, "key")

        adapter.send_text.assert_awaited_once_with("caption")
        adapter.send_image.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("bot.commands.forward.translate", return_value="translated")
    async def test_translates_before_forwarding(self, mock_translate: MagicMock) -> None:
        adapter = AsyncMock()

        await forward_content("hello", [], adapter, "deepl-key", target_lang="ZH")

        mock_translate.assert_called_once_with("hello", "ZH", "deepl-key")
        adapter.send_text.assert_awaited_once_with("translated")

    @pytest.mark.asyncio
    @patch("bot.commands.forward.translate")
    async def test_skips_translation_when_no_target_lang(self, mock_translate: MagicMock) -> None:
        adapter = AsyncMock()

        await forward_content("hello", [], adapter, "key", target_lang=None)

        mock_translate.assert_not_called()
        adapter.send_text.assert_awaited_once_with("hello")

    @pytest.mark.asyncio
    @patch("bot.commands.forward.translate")
    async def test_skips_translation_when_text_empty(self, mock_translate: MagicMock) -> None:
        adapter = AsyncMock()

        await forward_content("", [], adapter, "key", target_lang="ZH")

        mock_translate.assert_not_called()

    @pytest.mark.asyncio
    @patch("bot.commands.forward.translate", side_effect=QuotaExceededException("quota"))
    async def test_raises_quota_exceeded(self, _mock: MagicMock) -> None:
        adapter = AsyncMock()

        with pytest.raises(QuotaExceededException):
            await forward_content("hello", [], adapter, "key", target_lang="ZH")
