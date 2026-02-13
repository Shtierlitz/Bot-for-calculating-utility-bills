"""Точка входу Telegram-бота на aiogram."""
from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.config import get_settings
from bot.handlers import router

logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    level=logging.INFO,
)


def _build_bot(settings) -> Bot:
    return Bot(token=settings.bot_token, parse_mode=settings.parse_mode)


async def main() -> None:
    settings = get_settings()
    bot = _build_bot(settings)
    dp = Dispatcher()
    dp.include_router(router)
    logging.info('Бот запущений та очікує повідомлення')
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info('Бот зупинено')
