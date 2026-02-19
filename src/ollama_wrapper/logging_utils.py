from __future__ import annotations

import json
import logging
from dataclasses import asdict
from typing import Any, Dict, Optional


class UsageLogger:
    def __init__(self, logger_name: str):
        self._log = logging.getLogger(logger_name)

    def log_request(
        self,
        *,
        request_id: str,
        model: str,
        latency_ms: int,
        usage: Any,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        payload: Dict[str, Any] = {
            "event": "ollama.chat",
            "request_id": request_id,
            "model": model,
            "latency_ms": latency_ms,
        }

        try:
            payload["usage"] = asdict(usage)
        except Exception:
            payload["usage"] = str(usage)

        if extra:
            payload.update(extra)

        # JSON風でログ出力（ELK等で取りやすい）
        self._log.info(json.dumps(payload, ensure_ascii=False))
