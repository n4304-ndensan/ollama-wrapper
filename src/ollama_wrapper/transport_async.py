from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import ollama

from .exceptions import TransportError


class OllamaTransportAsync:
    def __init__(self, host: str, timeout_s: Optional[float] = None):
        self._client = ollama.AsyncClient(host=host)
        self._timeout_s = timeout_s

    async def chat(
        self, model: str, messages: List[Dict], options: Dict[str, Any]
    ) -> ollama.ChatResponse:
        try:
            t0 = time.perf_counter()
            res = await self._client.chat(model=model, messages=messages, options=options)
            res["_latency_s"] = time.perf_counter() - t0
            return res
        except Exception as e:
            raise TransportError("Ollama async transport failed.") from e

    async def close(self) -> None:
        # AsyncClient also typically doesn't require explicit close.
        return
