from base64 import b64encode
from hashlib import md5

from aiohttp import ClientSession

from bot.adapters.base import PlatformAdapter


class WeChatWorkAdapter(PlatformAdapter):
    def __init__(self, url: str, session: ClientSession | None) -> None:
        self._url = url
        self._session = session

    async def send_text(self, text: str) -> None:
        payload = {"msgtype": "text", "text": {"content": text}}
        async with self._session.post(self._url, json=payload) as res:
            res.raise_for_status()

    async def send_image(self, data: bytes, filename: str) -> None:
        b64 = b64encode(data).decode("utf-8")
        md5_check = md5(data).hexdigest()
        payload = {"msgtype": "image", "image": { "base64": b64, "md5": md5_check}}
        async with self._session.post(self._url, json=payload) as res:
            res.raise_for_status()