from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from ollama import ChatResponse


@dataclass(frozen=True)
class Usage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated: bool


class UsageExtractor:
    """
    Extract usage from Ollama response when available.
    Fallback to rough estimation if missing.
    """

    @staticmethod
    def from_response_or_estimate(
        response: ChatResponse,
        messages: list[dict],
        assistant_text: str,
    ) -> Usage:
        # Try common patterns
        # Some backends provide: response.get("eval_count"), "prompt_eval_count", etc.
        prompt = None
        completion = None

        # Ollama / llama.cpp style fields (varies by version/model)
        if isinstance(response, dict):
            if "prompt_eval_count" in response:
                prompt = int(response["prompt_eval_count"])
            if "eval_count" in response:
                completion = int(response["eval_count"])

            # Alternative nested structure (defensive)
            usage = response.get("usage")
            if isinstance(usage, dict):
                pt = usage.get("prompt_tokens")
                ct = usage.get("completion_tokens")
                tt = usage.get("total_tokens")
                if pt is not None and ct is not None:
                    prompt = int(pt)
                    completion = int(ct)
                    if tt is not None:
                        return Usage(prompt, completion, int(tt), estimated=False)

        if prompt is not None and completion is not None:
            return Usage(prompt, completion, prompt + completion, estimated=False)

        # Fallback: rough estimate by chars.
        # Typical heuristic: ~4 chars/token (English), Japanese differs; still useful for throttling.
        prompt_text = UsageExtractor._concat_user_text(messages)
        est_prompt = max(1, len(prompt_text) // 4)
        est_completion = max(1, len(assistant_text) // 4)
        return Usage(est_prompt, est_completion, est_prompt + est_completion, estimated=True)

    @staticmethod
    def _concat_user_text(messages: list[dict]) -> str:
        parts = []
        for m in messages:
            content = m.get("content")
            if isinstance(content, str):
                parts.append(content)
        return "\n".join(parts)
