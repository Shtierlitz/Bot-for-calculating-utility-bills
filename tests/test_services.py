from decimal import Decimal
from unittest.mock import Mock

import bot.dialogue.constants as constants
from bot.dialogue.services.calculator import PaymentCalculator
from bot.dialogue.services.flow import PaymentFlow
from bot.dialogue.services.mapping import PaymentDraftMapper
from bot.dialogue.services.payment import PaymentService
from tests.dtos import PaymentDraftDTO


def make_service(calculator: Mock) -> PaymentService:
    return PaymentService(
        mapper=PaymentDraftMapper(),
        flow_factory=PaymentFlow,
        calculator=calculator,
    )


def test_intermediate_success_returns_serialized_state_and_next_prompt():
    calculator = Mock(spec=PaymentCalculator)
    service = make_service(calculator)

    result = service.process(service.start().state, 'Корнієнко Сергій Іванович')

    assert result.success
    assert not result.finished
    assert result.state is not None
    assert result.state['step_index'] == 1
    assert result.state['step'] == constants.PERIOD_STEP
    assert result.message == constants.STEP_PROMPTS[constants.PERIOD_STEP]
    assert result.show_back_keyboard
    calculator.details.assert_not_called()
    calculator.summary.assert_not_called()


def test_input_error_returns_message_without_changing_state_or_calculating():
    calculator = Mock(spec=PaymentCalculator)
    service = make_service(calculator)

    result = service.process(service.start().state, '   ')

    assert not result.success
    assert result.state is None
    assert result.message == 'Поле не може бути порожнім.'
    calculator.details.assert_not_called()
    calculator.summary.assert_not_called()


def test_back_command_restores_previous_step_and_clears_its_value():
    calculator = Mock(spec=PaymentCalculator)
    service = make_service(calculator)
    intermediate = service.process(service.start().state, 'Корнієнко Сергій Іванович')

    result = service.process(intermediate.state, '⬅️ Назад')

    assert result.success
    assert result.state is not None
    assert result.state['step_index'] == 0
    assert result.state['step'] == constants.FULL_NAME_STEP
    assert result.state['payload']['full_name'] is None
    assert result.message == 'Повертаємося до попереднього кроку.\n' + constants.STEP_PROMPTS[constants.FULL_NAME_STEP]
    assert result.show_back_keyboard
    calculator.details.assert_not_called()
    calculator.summary.assert_not_called()


def test_finished_input_returns_detailed_and_summary_messages():
    calculator = Mock(spec=PaymentCalculator)
    calculator.details.return_value = 'DETAILS'
    calculator.summary.return_value = 'SUMMARY'
    mapper = PaymentDraftMapper()
    service = make_service(calculator)
    draft = PaymentDraftDTO(sponsorship_amount=None)
    stored_state = {
        'payload': mapper.to_dict(draft),
        'step_index': constants.STEP_ORDER.index(constants.SPONSORSHIP_STEP),
        'step': constants.SPONSORSHIP_STEP,
    }

    result = service.process(stored_state, '25')

    assert result.success
    assert result.finished
    assert result.details_message == 'DETAILS'
    assert result.summary_message == 'SUMMARY'
    assert result.completion_message == 'Щоб підготувати ще одне повідомлення, натисніть /start.'
    details = calculator.details.call_args.args[0]
    assert details.sponsorship_amount == Decimal('25')
    calculator.summary.assert_called_once_with(details)


def test_back_on_first_step_does_not_call_calculator():
    calculator = Mock(spec=PaymentCalculator)
    service = make_service(calculator)

    result = service.process(service.start().state, 'назад')

    assert not result.success
    assert result.state is None
    assert result.message == 'Ви вже на першому кроці, повертатися нікуди.'
    calculator.details.assert_not_called()
    calculator.summary.assert_not_called()


def test_payment_service_uses_default_dependencies():
    service = PaymentService()

    initial = service.start()

    assert isinstance(service, PaymentService)
    assert initial.state['step_index'] == 0
    assert initial.state['step'] == constants.FULL_NAME_STEP
    assert initial.prompt == constants.STEP_PROMPTS[constants.FULL_NAME_STEP]
