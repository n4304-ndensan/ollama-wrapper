from __future__ import annotations

from typing import Dict, List, Optional


class MessageBuilder:
    @staticmethod
    def build(user_message: str, system_prompt: Optional[str] = None) -> List[Dict]:
        messages: List[Dict] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_message})
        return messages

    @staticmethod
    def build_with_image(
        user_message: str,
        image_path: str,
        system_prompt: Optional[str] = None,
    ) -> List[Dict]:
        messages: List[Dict] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_message, "images": [image_path]})
        return messages
