from decimal import Decimal

import pytest

import bot.dialogue.constants as constants
from bot.dialogue.dtos import DialogueState, PaymentDraft
from bot.dialogue.services.flow import PaymentFlow


def flow_at(step: str, payload: PaymentDraft | None = None) -> PaymentFlow:
    return PaymentFlow(DialogueState(step_index=constants.STEP_ORDER.index(step), payload=payload or PaymentDraft()))


def test_sponsorship_follows_area_step():
    flow = flow_at(constants.AREA_STEP)

    result = flow.process('68.1')

    assert result.success
    assert not result.finished
    assert flow.current_step == constants.SPONSORSHIP_STEP
    assert flow.payload.apartment_area == Decimal('68.1')
    assert flow.current_prompt() == (
        'Чи є побажання внести додаткові кошти в якості спонсорства будинку? '
        'Введіть суму. Якщо бажання нема, то введіть 0.'
    )


def test_period_step_stores_billing_period():
    flow = flow_at(constants.PERIOD_STEP)

    result = flow.process('01-2026')

    assert result.success
    assert flow.payload.period is not None
    assert flow.payload.period.month == 1
    assert flow.payload.period.year == 2026


def test_sponsorship_is_last_step():
    assert constants.STEP_ORDER[-1] == constants.SPONSORSHIP_STEP
    assert constants.STEP_PAYLOAD_KEYS[constants.SPONSORSHIP_STEP] == 'sponsorship_amount'


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [('150.50', Decimal('150.50')), ('150,5', Decimal('150.5')), ('1 000', Decimal('1000')), ('0', Decimal('0'))],
)
def test_sponsorship_finishes_flow_and_stores_decimal(raw, expected):
    flow = flow_at(constants.SPONSORSHIP_STEP)

    result = flow.process(raw)

    assert result.success
    assert result.finished
    assert isinstance(flow.payload.sponsorship_amount, Decimal)
    assert flow.payload.sponsorship_amount == expected


@pytest.mark.parametrize('raw', ['-10', '-0.01', 'abc', '', 'nan', 'inf'])
def test_invalid_sponsorship_is_rejected(raw):
    flow = flow_at(constants.SPONSORSHIP_STEP)

    result = flow.process(raw)

    assert not result.success
    assert not result.finished
    assert result.error
    assert flow.payload.sponsorship_amount is None
    assert flow.current_step == constants.SPONSORSHIP_STEP


def test_negative_sponsorship_error_mentions_negative():
    result = flow_at(constants.SPONSORSHIP_STEP).process('-5')

    assert 'відʼємною' in result.error


def test_go_back_from_sponsorship_returns_to_area():
    flow = flow_at(constants.SPONSORSHIP_STEP, PaymentDraft(apartment_area=Decimal('68.1')))

    assert flow.go_back()

    assert flow.current_step == constants.AREA_STEP
    assert flow.payload.apartment_area is None
    assert flow.current_prompt() == constants.STEP_PROMPTS[constants.AREA_STEP]


def test_area_can_be_reentered_after_going_back():
    flow = flow_at(constants.SPONSORSHIP_STEP, PaymentDraft(apartment_area=Decimal('68.1')))
    flow.go_back()

    result = flow.process('70')

    assert result.success and not result.finished
    assert flow.payload.apartment_area == Decimal('70')
    assert flow.current_step == constants.SPONSORSHIP_STEP
