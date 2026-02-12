from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes


WELCOME_MESSAGE = (
    '👋 Привет, {name}!\n\n'
    'Я помогу посчитать коммунальные платежи и подготовлю текст для назначения платежа.\n'
    'Сейчас я в режиме черновика: просто напиши что-нибудь, а я отвечу подсказками.'
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет приветственное сообщение при /start."""

    user = update.effective_user
    name = user.first_name if user and user.first_name else 'друг'
    await update.message.reply_text(WELCOME_MESSAGE.format(name=name))


async def handle_plain_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Временный обработчик любых текстовых сообщений."""

    text = (
        '🛠️ Каркас бота готов, логика расчётов появится позже.\n'
        'Пока что ответь на приветствие или уточни требования.'
    )
    await update.message.reply_text(text)
