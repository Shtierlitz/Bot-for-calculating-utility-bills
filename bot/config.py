from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Контейнер с настройками, полученными из окружения."""

    bot_token: str
    parse_mode: Optional[str] = None


def get_settings() -> Settings:
    """Читает настройки из окружения и валидирует обязательные поля."""

    token = os.getenv('BOT_TOKEN')
    if not token:
        raise RuntimeError('Не указан BOT_TOKEN в переменных окружения или .env файле')

    parse_mode = os.getenv('BOT_PARSE_MODE') or None
    return Settings(bot_token=token, parse_mode=parse_mode)
