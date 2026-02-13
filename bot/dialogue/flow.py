from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Optional

from bot.dialogue import constants


@dataclass
class DialogueState:
    step_index: int = 0
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FlowResult:
    success: bool
    error: Optional[str] = None
    finished: bool = False


class PaymentFlow:
    """Управляет послідовністю кроків та валідацією введення."""

    def __init__(self, state: DialogueState | None = None) -> None:
        self.state = state or DialogueState()

    @property
    def payload(self) -> Dict[str, Any]:
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
        payload_key = constants.STEP_PAYLOAD_KEYS[previous_step]
        self.state.payload.pop(payload_key, None)
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
        self.state.payload[constants.STEP_PAYLOAD_KEYS[step]] = value
        finished = not self._advance()
        return FlowResult(success=True, finished=finished)

    def _store_period(self, raw_text: str) -> FlowResult:
        text = raw_text.strip()
        match = constants.PERIOD_PATTERN.fullmatch(text)
        if not match:
            return FlowResult(success=False, error='Не впізнаю формат. Використайте MM-YYYY, наприклад 01-2026.')
        month, year = int(match.group(1)), int(match.group(2))
        self.state.payload['period'] = {'month': month, 'year': year}
        finished = not self._advance()
        return FlowResult(success=True, finished=finished)

    def _store_decimal(self, step: str, raw_text: str) -> FlowResult:
        parsed = self._parse_decimal(raw_text)
        if parsed is None:
            return FlowResult(success=False, error='Будь ласка, введіть числове значення (наприклад, 123.45).')
        self.state.payload[constants.STEP_PAYLOAD_KEYS[step]] = parsed
        finished = step == constants.AREA_STEP
        if not finished:
            finished = not self._advance()
        return FlowResult(success=True, finished=finished)

    def _advance(self) -> bool:
        if self.state.step_index + 1 >= len(constants.STEP_ORDER):
            return False
        self.state.step_index += 1
        return True

    @staticmethod
    def _parse_decimal(raw_text: str) -> Optional[Decimal]:
        trimmed = raw_text.strip()
        if not trimmed:
            return None
        normalized = trimmed.replace(' ', '').replace(',', '.').rstrip('.').rstrip(',')
        if not normalized:
            return None
        try:
            return Decimal(normalized)
        except InvalidOperation:
            return None


__all__ = ['PaymentFlow', 'DialogueState', 'FlowResult']
