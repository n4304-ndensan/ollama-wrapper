from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class IChatClient(ABC):
    @abstractmethod
    def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        expect_json: bool = False,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError


class IAsyncChatClient(ABC):
    @abstractmethod
    async def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        expect_json: bool = False,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError
