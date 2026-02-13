from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    collecting = State()


__all__ = ['Form']
