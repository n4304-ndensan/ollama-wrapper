from __future__ import annotations

import itertools
from typing import Optional

from ..config import ClientConfig
from ..interfaces import IAsyncChatClient
from ..json_validator import JsonValidator
from ..logging_utils import UsageLogger
from ..message_builder import MessageBuilder
from ..rate_limiter import SlidingWindowRateLimiter
from ..transport_async import OllamaTransportAsync
from ..usage import UsageExtractor


class AsyncOllamaTextClient(IAsyncChatClient):
    _counter = itertools.count(1)

    def __init__(self, cfg: ClientConfig):
        self._cfg = cfg
        self._transport = OllamaTransportAsync(cfg.host, timeout_s=cfg.timeout_s)

        self._limiter = SlidingWindowRateLimiter(
            cfg.requests_per_minute, cfg.tokens_per_minute, raise_on_limit=False
        )
        self._usage_logger = UsageLogger(cfg.logger_name)

    async def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        expect_json: bool = False,
    ) -> str:
        request_id = f"req-{next(self._counter)}"
        messages = MessageBuilder.build(message, system_prompt)

        est_add_tokens = max(1, len(message) // 4)
        await self._limiter.acquire(add_tokens=est_add_tokens)

        res = await self._transport.chat(
            model=self._cfg.model,
            messages=messages,
            options={"temperature": self._cfg.temperature},
        )

        content = res["message"]["content"]
        usage = UsageExtractor.from_response_or_estimate(res, messages, content)

        if self._cfg.log_usage:
            latency_ms = int(res.get("_latency_s", 0.0) * 1000)
            self._usage_logger.log_request(
                request_id=request_id,
                model=self._cfg.model,
                latency_ms=latency_ms,
                usage=usage,
            )

        if expect_json:
            return JsonValidator.normalize_or_raise(content)
        return content

    async def close(self) -> None:
        await self._transport.close()
