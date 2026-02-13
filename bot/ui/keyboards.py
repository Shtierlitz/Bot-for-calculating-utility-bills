from __future__ import annotations

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from bot.dialogue.constants import BACK_BUTTON_TEXT


def back_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text=BACK_BUTTON_TEXT)]]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


__all__ = ['back_keyboard']
