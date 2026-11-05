from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.dialogue.services.payment import PaymentService
from bot.dialogue.states import Form
from bot.ui.keyboards import back_keyboard

router = Router()
payment_service = PaymentService()


@router.message(StateFilter(None), F.text)
async def handle_without_session(message: Message) -> None:
    await message.answer('Щоб почати, натисніть /start та дотримуйтеся підказок.', reply_markup=ReplyKeyboardRemove())


@router.message(Form.collecting, F.text)
async def handle_plain_text(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    result = payment_service.process(data, message.text or '')
    if result.state is not None:
        await state.update_data(**result.state)

    if result.finished:
        await message.answer(result.details_message or '', reply_markup=ReplyKeyboardRemove())
        await message.answer(result.summary_message or '')
        await state.clear()
        await message.answer(result.completion_message or '')
        return

    if result.show_back_keyboard:
        await message.answer(result.message or '', reply_markup=back_keyboard())
    else:
        await message.answer(result.message or '')
