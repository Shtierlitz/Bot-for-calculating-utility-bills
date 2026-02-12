"""Точка входа Telegram-бота."""
from __future__ import annotations

import logging

from telegram.ext import Application, ApplicationBuilder, CommandHandler, Defaults, MessageHandler, filters

from bot.config import get_settings
from bot.handlers import handle_plain_text, start

logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    level=logging.INFO,
)


def main() -> None:

    settings = get_settings()
    builder: ApplicationBuilder = Application.builder().token(settings.bot_token)

    if settings.parse_mode:
        builder = builder.defaults(Defaults(parse_mode=settings.parse_mode))

    application: Application = builder.build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_plain_text))

    logging.info('Бот запущен и ожидает сообщения')
    application.run_polling()


if __name__ == '__main__':
    main()
