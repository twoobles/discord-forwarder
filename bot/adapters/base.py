from abc import ABC, abstractmethod


class PlatformAdapter(ABC):
    @abstractmethod
    async def send_text(self, text: str) -> None: ...

    @abstractmethod
    async def send_image(self, data: bytes, filename: str) -> None: ...
