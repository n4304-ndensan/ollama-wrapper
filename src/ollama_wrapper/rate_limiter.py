from __future__ import annotations

import asyncio
import threading
import time
from dataclasses import dataclass
from typing import Optional

from .exceptions import RateLimitError


@dataclass
class _Window:
    window_start: float
    used_requests: int
    used_tokens: int


class SlidingWindowRateLimiter:
    """
    Simple 60s window limiter (practical, predictable).
    Not a perfect token bucket; intentionally deterministic for batch workloads.
    """

    def __init__(
        self,
        requests_per_minute: Optional[int],
        tokens_per_minute: Optional[int],
        *,
        raise_on_limit: bool = False,
    ):
        self._rpm = requests_per_minute
        self._tpm = tokens_per_minute
        self._raise = raise_on_limit
        now = time.monotonic()
        self._win = _Window(window_start=now, used_requests=0, used_tokens=0)

        # locks
        self._lock = asyncio.Lock()
        self._sync_lock: Optional[threading.Lock] = (
            None  # created lazily to avoid threading import if unused
        )

    def _reset_if_needed(self, now: float) -> None:
        if now - self._win.window_start >= 60.0:
            self._win.window_start = now
            self._win.used_requests = 0
            self._win.used_tokens = 0

    def _need_wait_seconds(self, now: float, add_req: int, add_tokens: int) -> float:
        self._reset_if_needed(now)

        if self._rpm is not None and (self._win.used_requests + add_req) > self._rpm:
            return 60.0 - (now - self._win.window_start)

        if self._tpm is not None and (self._win.used_tokens + add_tokens) > self._tpm:
            return 60.0 - (now - self._win.window_start)

        return 0.0

    def _commit(self, add_req: int, add_tokens: int) -> None:
        self._win.used_requests += add_req
        self._win.used_tokens += add_tokens

    # -------- sync --------
    def acquire_sync(self, add_tokens: int = 0) -> None:
        import threading  # local import

        if self._sync_lock is None:
            self._sync_lock = threading.Lock()

        with self._sync_lock:
            while True:
                now = time.monotonic()
                wait = self._need_wait_seconds(now, add_req=1, add_tokens=add_tokens)
                if wait <= 0:
                    self._commit(add_req=1, add_tokens=add_tokens)
                    return

                if self._raise:
                    raise RateLimitError(f"Rate limit exceeded. Need wait {wait:.2f}s")

                time.sleep(wait)

    # -------- async --------
    async def acquire(self, add_tokens: int = 0) -> None:
        async with self._lock:
            while True:
                now = time.monotonic()
                wait = self._need_wait_seconds(now, add_req=1, add_tokens=add_tokens)
                if wait <= 0:
                    self._commit(add_req=1, add_tokens=add_tokens)
                    return

                if self._raise:
                    raise RateLimitError(f"Rate limit exceeded. Need wait {wait:.2f}s")

                # release lock while sleeping to not block others
                # but keep semantics simple: sleep inside lock is okay for batch use
                await asyncio.sleep(wait)
