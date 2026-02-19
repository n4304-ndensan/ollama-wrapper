from __future__ import annotations

import json
from .exceptions import InvalidJsonError


class JsonValidator:
    @staticmethod
    def normalize_or_raise(text: str) -> str:
        try:
            obj = json.loads(text)
            return json.dumps(obj, ensure_ascii=False, indent=2)
        except Exception as e:
            raise InvalidJsonError("Model did not return valid JSON.") from e
