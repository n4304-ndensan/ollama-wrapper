from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


from ollama import ChatResponse, Client
from .exceptions import TransportError


class OllamaTransportSync:
    def __init__(self, host: str, timeout_s: Optional[float] = None):
        self._client = Client(host=host)
        self._timeout_s = timeout_s

    def chat(self, model: str, messages: List[Dict], options: Dict[str, Any]) -> ChatResponse:
        try:
            # python-ollama の timeout はバージョン差があるため options に寄せる
            t0 = time.perf_counter()
            res = self._client.chat(model=model, messages=messages, options=options)
            res["_latency_s"] = time.perf_counter() - t0
            return res
        except Exception as e:
            raise TransportError("Ollama sync transport failed.") from e

    def close(self) -> None:
        # python-ollama client has no explicit close in most versions.
        return
