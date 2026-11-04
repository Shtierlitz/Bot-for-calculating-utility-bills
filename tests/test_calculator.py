from decimal import Decimal

import pytest

from bot.dialogue.calculator import PaymentCalculator


def make_payload(**overrides):
    payload = {
        'full_name': 'Корнієнко Сергій Іванович',
        'period': {'month': 1, 'year': 2026},
        'address': 'вул. Тестова, 1, кв. 1',
        'hot_prev': Decimal('10'),
        'hot_curr': Decimal('12'),
        'cold_prev': Decimal('100'),
        'cold_curr': Decimal('105'),
        'cold_tariff': Decimal('30.384'),
        'hot_tariff': Decimal('100'),
        'rent_tariff': Decimal('8'),
        'heat_tariff': Decimal('0'),
        'apartment_area': Decimal('50'),
        'sponsorship_amount': Decimal('0'),
    }
    payload.update(overrides)
    return payload


# Холодна 5 × 30.384 = 151.92, гаряча 2 × 100 = 200, обслуговування 50 × 8 = 400.
BASE_TOTAL = '751.92'


@pytest.fixture
def calculator():
    return PaymentCalculator()


def test_zero_sponsorship_adds_no_section(calculator):
    details = calculator.details(make_payload())

    assert 'Спонсорство будинку' not in details
    assert details.endswith(f'Всього — {BASE_TOTAL} грн ✅')


def test_missing_sponsorship_behaves_like_zero(calculator):
    payload = make_payload()
    del payload['sponsorship_amount']

    assert calculator.details(payload) == calculator.details(make_payload())


@pytest.mark.parametrize(
    ('amount', 'display', 'total'),
    [(Decimal('100'), '100.00', '851.92'), (Decimal('150.5'), '150.50', '902.42'), (Decimal('0.01'), '0.01', '751.93')],
)
def test_positive_sponsorship_is_separate_line_and_added_to_total(calculator, amount, display, total):
    details = calculator.details(make_payload(sponsorship_amount=amount))

    assert f'🤝 Спонсорство будинку:\n\n{display} грн' in details
    assert f'Спонсорство будинку — {display}\n' in details
    assert details.endswith(f'Всього — {total} грн ✅')


def test_sponsorship_not_in_tariffs_block(calculator):
    details = calculator.details(make_payload(sponsorship_amount=Decimal('100')))

    tariffs_block = details.split('💰 Тарифи:')[1].split('⸻')[0]
    assert 'Спонсорство' not in tariffs_block


def test_sponsorship_does_not_change_existing_sections(calculator):
    without = calculator.details(make_payload())
    with_sponsorship = calculator.details(make_payload(sponsorship_amount=Decimal('100')))

    for line in ('Холодна вода — 151.92', 'Гаряча вода — 200.00', 'Технічне обслуговування будинку — 400.00'):
        assert line in without
        assert line in with_sponsorship


SUMMARY_PREFIX = (
    'Ком.послуги за січень 2026р. Корнієнко Сергій Іванович,вул. Тестова, 1, кв. 1;'
    'ГВП(показники:10-12),ХВП(показники:100-105),'
)


@pytest.mark.parametrize(
    ('amount', 'suffix'),
    [
        (Decimal('150'), 'спонсорство-150'),
        (Decimal('150.00'), 'спонсорство-150'),
        (Decimal('150.5'), 'спонсорство-150,5'),
        (Decimal('150.50'), 'спонсорство-150,5'),
        (Decimal('0'), 'спонсорство-0'),
    ],
)
def test_summary_ends_with_sponsorship_suffix(calculator, amount, suffix):
    summary = calculator.summary(make_payload(sponsorship_amount=amount))

    assert summary == SUMMARY_PREFIX + suffix
    assert 'спонсорство- ' not in summary


def test_summary_without_sponsorship_key_ends_with_zero(calculator):
    payload = make_payload()
    del payload['sponsorship_amount']

    assert calculator.summary(payload).endswith(',спонсорство-0')
