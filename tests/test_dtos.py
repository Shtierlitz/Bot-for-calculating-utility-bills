from decimal import Decimal

import pytest

from bot.dialogue.dtos import BillingPeriod, PaymentDraft
from bot.dialogue.services.mapping import PaymentDraftMapper
from tests.dtos import PaymentDetailsDTO, PaymentDraftDTO


def test_payment_draft_round_trip_restores_nested_and_decimal_values():
    mapper = PaymentDraftMapper()
    draft = PaymentDraftDTO()

    restored = mapper.from_dict(mapper.to_dict(draft))

    assert mapper.to_dict(restored) == mapper.to_dict(draft)
    assert restored.period == BillingPeriod(month=1, year=2026)
    assert isinstance(restored.cold_tariff, Decimal)


def test_empty_payment_draft_round_trip():
    mapper = PaymentDraftMapper()
    draft = PaymentDraft()

    assert mapper.from_dict(mapper.to_dict(draft)) == draft


def test_old_fsm_payload_without_sponsorship_restores_zero():
    mapper = PaymentDraftMapper()
    stored = mapper.to_dict(PaymentDraftDTO())
    del stored['sponsorship_amount']

    restored = mapper.from_dict(stored)

    assert restored.sponsorship_amount == Decimal('0')


def test_decimal_strings_from_fsm_are_restored():
    restored = PaymentDraftMapper().from_dict({'cold_tariff': '30.384', 'sponsorship_amount': '12.50'})

    assert restored.cold_tariff == Decimal('30.384')
    assert restored.sponsorship_amount == Decimal('12.50')


def test_incomplete_draft_cannot_be_converted_to_details():
    with pytest.raises(ValueError, match='full_name.*period.*sponsorship_amount'):
        PaymentDraftMapper().to_details(PaymentDraft())


def test_complete_draft_converts_to_payment_details():
    expected = PaymentDetailsDTO()
    actual = PaymentDraftMapper().to_details(PaymentDraftDTO())

    assert actual.full_name == expected.full_name
    assert actual.period == expected.period
    assert actual.sponsorship_amount == expected.sponsorship_amount
