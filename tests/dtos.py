from dataclasses import dataclass
from decimal import Decimal

from bot.dialogue.dtos import BillingPeriod, PaymentDetails, PaymentDraft


@dataclass(frozen=True)
class PaymentDetailsDTO(PaymentDetails):
    full_name: str = 'Корнієнко Сергій Іванович'
    period: BillingPeriod = BillingPeriod(month=1, year=2026)
    address: str = 'вул. Тестова, 1, кв. 1'
    hot_prev: Decimal = Decimal('10')
    hot_curr: Decimal = Decimal('12')
    cold_prev: Decimal = Decimal('100')
    cold_curr: Decimal = Decimal('105')
    cold_tariff: Decimal = Decimal('30.384')
    hot_tariff: Decimal = Decimal('100')
    rent_tariff: Decimal = Decimal('8')
    heat_tariff: Decimal = Decimal('0')
    apartment_area: Decimal = Decimal('50')
    sponsorship_amount: Decimal = Decimal('0')


@dataclass
class PaymentDraftDTO(PaymentDraft):
    full_name: str | None = 'Корнієнко Сергій Іванович'
    period: BillingPeriod | None = BillingPeriod(month=1, year=2026)
    address: str | None = 'вул. Тестова, 1, кв. 1'
    hot_prev: Decimal | None = Decimal('10')
    hot_curr: Decimal | None = Decimal('12')
    cold_prev: Decimal | None = Decimal('100')
    cold_curr: Decimal | None = Decimal('105')
    cold_tariff: Decimal | None = Decimal('30.384')
    hot_tariff: Decimal | None = Decimal('100')
    rent_tariff: Decimal | None = Decimal('8')
    heat_tariff: Decimal | None = Decimal('0')
    apartment_area: Decimal | None = Decimal('50')
    sponsorship_amount: Decimal | None = Decimal('0')
