from base64 import b64encode
from hashlib import md5
from unittest.mock import AsyncMock, MagicMock

import pytest

from bot.adapters.wechat import WeChatWorkAdapter

WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test-key"


def _make_adapter(status: int = 200) -> tuple[WeChatWorkAdapter, MagicMock]:
    """Create an adapter with a mocked aiohttp session.

    Returns the adapter and the mock session so tests can inspect calls.
    """
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    if status >= 400:
        mock_response.raise_for_status.side_effect = Exception(f"HTTP {status}")

    # aiohttp's session.post() returns an async context manager (not a coroutine).
    # MagicMock handles __aenter__/__aexit__ correctly here — AsyncMock would
    # make post() itself a coroutine, which breaks "async with session.post(...)".
    ctx_manager = AsyncMock()
    ctx_manager.__aenter__.return_value = mock_response

    mock_session = MagicMock()
    mock_session.post.return_value = ctx_manager

    adapter = WeChatWorkAdapter(url=WEBHOOK_URL, session=mock_session)
    return adapter, mock_session


class TestSendText:
    @pytest.mark.asyncio
    async def test_posts_correct_payload(self) -> None:
        adapter, session = _make_adapter()

        await adapter.send_text("Hello WeChat")

        session.post.assert_called_once_with(
            WEBHOOK_URL,
            json={"msgtype": "text", "text": {"content": "Hello WeChat"}},
        )

    @pytest.mark.asyncio
    async def test_raises_on_http_error(self) -> None:
        adapter, _session = _make_adapter(status=403)

        with pytest.raises(Exception, match="403"):
            await adapter.send_text("should fail")


class TestSendImage:
    @pytest.mark.asyncio
    async def test_posts_correct_payload(self) -> None:
        adapter, session = _make_adapter()
        img_data = b"fake-png-image-bytes"

        await adapter.send_image(img_data, "photo.png")

        expected_b64 = b64encode(img_data).decode("utf-8")
        expected_md5 = md5(img_data).hexdigest()
        session.post.assert_called_once_with(
            WEBHOOK_URL,
            json={
                "msgtype": "image",
                "image": {"base64": expected_b64, "md5": expected_md5},
            },
        )

    @pytest.mark.asyncio
    async def test_raises_on_http_error(self) -> None:
        adapter, _session = _make_adapter(status=500)

        with pytest.raises(Exception, match="500"):
            await adapter.send_image(b"data", "img.png")
