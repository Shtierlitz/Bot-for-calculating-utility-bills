from __future__ import annotations

from collections.abc import Callable, Mapping

from bot.dialogue.dtos import DialogueState, PaymentServiceResult, PaymentServiceStart
from bot.dialogue.services.calculator import PaymentCalculator
from bot.dialogue.services.flow import PaymentFlow, is_back_command
from bot.dialogue.services.mapping import PaymentDraftMapper


class PaymentService:
    """Facade for the complete stateful payment dialogue operation."""

    def __init__(
        self,
        mapper: PaymentDraftMapper | None = None,
        flow_factory: Callable[[DialogueState | None], PaymentFlow] | None = None,
        calculator: PaymentCalculator | None = None,
    ) -> None:
        self.mapper = mapper if mapper is not None else PaymentDraftMapper()
        self.flow_factory = flow_factory if flow_factory is not None else PaymentFlow
        self.calculator = calculator if calculator is not None else PaymentCalculator()

    def start(self) -> PaymentServiceStart:
        flow = self.flow_factory(None)
        return PaymentServiceStart(state=self._serialize_state(flow), prompt=flow.current_prompt())

    def process(self, stored_state: Mapping[str, object] | None, text: str) -> PaymentServiceResult:
        flow = self.flow_factory(self._restore_state(stored_state))

        if is_back_command(text):
            if not flow.go_back():
                return PaymentServiceResult(
                    success=False,
                    message='Ви вже на першому кроці, повертатися нікуди.',
                    show_back_keyboard=True,
                )
            return PaymentServiceResult(
                success=True,
                state=self._serialize_state(flow),
                message='Повертаємося до попереднього кроку.\n' + flow.current_prompt(),
                show_back_keyboard=True,
            )

        flow_result = flow.process(text)
        if not flow_result.success:
            return PaymentServiceResult(
                success=False,
                message=flow_result.error or 'Помилка під час обробки введення.',
            )

        serialized_state = self._serialize_state(flow)
        if not flow_result.finished:
            return PaymentServiceResult(
                success=True,
                state=serialized_state,
                message=flow.current_prompt(),
                show_back_keyboard=True,
            )

        details = self.mapper.to_details(flow.payload)
        return PaymentServiceResult(
            success=True,
            state=serialized_state,
            finished=True,
            details_message=self.calculator.details(details),
            summary_message=self.calculator.summary(details),
            completion_message='Щоб підготувати ще одне повідомлення, натисніть /start.',
        )

    def _restore_state(self, data: Mapping[str, object] | None) -> DialogueState:
        source = data or {}
        stored_payload = source.get('payload')
        payload = self.mapper.from_dict(stored_payload if isinstance(stored_payload, Mapping) else None)
        try:
            step_index = int(source.get('step_index', 0))
        except (TypeError, ValueError):
            step_index = 0
        return DialogueState(step_index=step_index, payload=payload)

    def _serialize_state(self, flow: PaymentFlow) -> dict[str, object]:
        return {
            'payload': self.mapper.to_dict(flow.payload),
            'step_index': flow.step_index,
            'step': flow.current_step,
        }
