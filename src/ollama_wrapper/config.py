from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ClientConfig:
    model: str
    host: str = "http://localhost:11434"
    temperature: float = 0.2
    timeout_s: Optional[float] = None

    # rate limit
    requests_per_minute: Optional[int] = None
    tokens_per_minute: Optional[int] = None

    # logging
    log_usage: bool = False
    logger_name: str = "ollama_wrapper"
