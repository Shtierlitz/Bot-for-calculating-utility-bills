from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Optional

import bot.dialogue.constants as constants
from bot.dialogue.dtos import BillingPeriod, DialogueState, FlowResult, PaymentDraft


class PaymentFlow:
    """Управляет послідовністю кроків та валідацією введення."""

    def __init__(self, state: DialogueState | None = None) -> None:
        self.state = state or DialogueState()

    @property
    def payload(self) -> PaymentDraft:
        return self.state.payload

    @property
    def step_index(self) -> int:
        return self.state.step_index

    @property
    def current_step(self) -> str:
        return constants.STEP_ORDER[self.state.step_index]

    def current_prompt(self) -> str:
        return constants.STEP_PROMPTS[self.current_step]

    def go_back(self) -> bool:
        if self.state.step_index == 0:
            return False
        self.state.step_index -= 1
        previous_step = constants.STEP_ORDER[self.state.step_index]
        self._set_step_value(previous_step, None)
        return True

    def process(self, text: str) -> FlowResult:
        step = self.current_step

        if step in constants.TEXT_STEPS:
            return self._store_text(step, text.strip())

        if step == constants.PERIOD_STEP:
            return self._store_period(text)

        if step in constants.NUMERIC_STEPS:
            return self._store_decimal(step, text)

        return FlowResult(success=False, error='Невідомий крок. Спробуйте почати заново через /start.')

    def _store_text(self, step: str, value: str) -> FlowResult:
        if not value:
            return FlowResult(success=False, error='Поле не може бути порожнім.')
        self._set_step_value(step, value)
        finished = not self._advance()
        return FlowResult(success=True, finished=finished)

    def _store_period(self, raw_text: str) -> FlowResult:
        text = raw_text.strip()
        match = constants.PERIOD_PATTERN.fullmatch(text)
        if not match:
            return FlowResult(success=False, error='Не впізнаю формат. Використайте MM-YYYY, наприклад 01-2026.')
        month, year = int(match.group(1)), int(match.group(2))
        self._set_step_value(constants.PERIOD_STEP, BillingPeriod(month=month, year=year))
        finished = not self._advance()
        return FlowResult(success=True, finished=finished)

    def _store_decimal(self, step: str, raw_text: str) -> FlowResult:
        parsed = self._parse_decimal(raw_text)
        if parsed is None:
            return FlowResult(success=False, error='Будь ласка, введіть числове значення (наприклад, 123.45).')
        if step == constants.SPONSORSHIP_STEP and parsed < 0:
            return FlowResult(success=False, error='Сума спонсорства не може бути відʼємною. Введіть 0 або додатну суму.')
        self._set_step_value(step, parsed)
        finished = not self._advance()
        return FlowResult(success=True, finished=finished)

    def _advance(self) -> bool:
        if self.state.step_index + 1 >= len(constants.STEP_ORDER):
            return False
        self.state.step_index += 1
        return True

    def _set_step_value(self, step: str, value: object) -> None:
        field_name = constants.STEP_PAYLOAD_KEYS.get(step)
        if field_name is None or field_name not in PaymentDraft.__dataclass_fields__:
            raise RuntimeError(f'Unknown payment draft field for step: {step}')
        setattr(self.state.payload, field_name, value)

    @staticmethod
    def _parse_decimal(raw_text: str) -> Optional[Decimal]:
        trimmed = raw_text.strip()
        if not trimmed:
            return None
        normalized = trimmed.replace(' ', '').replace(',', '.').rstrip('.').rstrip(',')
        if not normalized:
            return None
        try:
            value = Decimal(normalized)
        except InvalidOperation:
            return None
        if not value.is_finite():
            return None
        return value


def is_back_command(text: str) -> bool:
    normalized = text.strip().lower()
    if not normalized:
        return False
    normalized = normalized.rstrip('.,!')
    if normalized.startswith('/'):
        normalized = normalized[1:]
    if normalized in constants.BACK_TOKENS:
        return True
    first_token = normalized.split()[0]
    return first_token in constants.BACK_TOKENS
