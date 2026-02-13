from __future__ import annotations

from typing import Any, Dict

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.dialogue.calculator import PaymentCalculator
from bot.dialogue.flow import DialogueState, PaymentFlow
from bot.dialogue.states import Form
from bot.dialogue.utils import is_back_command
from bot.ui.keyboards import back_keyboard


router = Router()
calculator = PaymentCalculator()


@router.message(StateFilter(None), F.text)
async def handle_without_session(message: Message) -> None:
    await message.answer('Щоб почати, натисніть /start та дотримуйтеся підказок.', reply_markup=ReplyKeyboardRemove())


@router.message(Form.collecting, F.text)
async def handle_plain_text(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    dialogue_state = DialogueState(
        step_index=int(data.get('step_index', 0)),
        payload=dict(data.get('payload') or {}),
    )
    flow = PaymentFlow(dialogue_state)
    user_message = message.text or ''

    if is_back_command(user_message):
        if flow.go_back():
            await _persist_state(state, flow)
            await message.answer(
                'Повертаємося до попереднього кроку.\n' + flow.current_prompt(),
                reply_markup=back_keyboard(),
            )
        else:
            await message.answer('Ви вже на першому кроці, повертатися нікуди.', reply_markup=back_keyboard())
        return

    result = flow.process(user_message)
    if not result.success:
        await message.answer(result.error or 'Помилка під час обробки введення.')
        return

    await _persist_state(state, flow)

    if result.finished:
        details = calculator.details(flow.payload)
        await message.answer(details, reply_markup=ReplyKeyboardRemove())
        summary = calculator.summary(flow.payload)
        await message.answer(summary)
        await state.clear()
        await message.answer('Щоб підготувати ще одне повідомлення, натисніть /start.')
        return

    await message.answer(flow.current_prompt(), reply_markup=back_keyboard())


async def _persist_state(state: FSMContext, flow: PaymentFlow) -> None:
    await state.update_data(payload=flow.payload, step_index=flow.step_index, step=flow.current_step)
