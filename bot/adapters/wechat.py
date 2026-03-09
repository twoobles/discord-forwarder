from base64 import b64encode
from hashlib import md5

from aiohttp import ClientSession

from bot.adapters.base import PlatformAdapter


class WeChatWorkAdapter(PlatformAdapter):
    """Forwards messages to a WeChat Work group via incoming webhook."""

    def __init__(self, url: str, session: ClientSession | None = None) -> None:
        self._url = url
        self._session = session

    async def _get_session(self) -> ClientSession:
        if self._session is None:
            self._session = ClientSession()
        return self._session

    async def send_text(self, text: str) -> None:
        session = await self._get_session()
        payload = {"msgtype": "text", "text": {"content": text}}
        async with session.post(self._url, json=payload) as res:
            res.raise_for_status()

    async def send_image(self, data: bytes, filename: str) -> None:
        session = await self._get_session()
        # WeChat webhook requires both base64 data and md5 checksum for images
        b64 = b64encode(data).decode("utf-8")
        md5_check = md5(data).hexdigest()
        payload = {"msgtype": "image", "image": {"base64": b64, "md5": md5_check}}
        async with session.post(self._url, json=payload) as res:
            res.raise_for_status()
