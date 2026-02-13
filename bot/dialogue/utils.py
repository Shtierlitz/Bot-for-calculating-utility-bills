from __future__ import annotations

from bot.dialogue.constants import BACK_TOKENS


def is_back_command(text: str) -> bool:
    normalized = text.strip().lower()
    if not normalized:
        return False
    normalized = normalized.rstrip('.,!')
    if normalized.startswith('/'):
        normalized = normalized[1:]
    if normalized in BACK_TOKENS:
        return True
    first_token = normalized.split()[0]
    return first_token in BACK_TOKENS


__all__ = ['is_back_command']
