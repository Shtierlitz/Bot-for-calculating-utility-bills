from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.dialogue.flow import PaymentFlow
from bot.dialogue.states import Form
from bot.ui.keyboards import back_keyboard


router = Router()

WELCOME_MESSAGE = (
    '👋 Вітаю, {name}! Я допоможу підрахувати та підготувати текст для комунальних платежів.\n\n'
    'Давайте починати: надсилайте відповіді українською мовою. Для виправлень скористайтеся кнопкою "Назад".'
)


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    user = message.from_user
    name = user.first_name if user and user.first_name else 'шановний користувачу'

    flow = PaymentFlow()
    await state.clear()
    await state.set_state(Form.collecting)
    await state.update_data(payload=flow.payload, step_index=flow.step_index, step=flow.current_step)

    await message.answer(WELCOME_MESSAGE.format(name=name))
    await message.answer(flow.current_prompt(), reply_markup=back_keyboard())
