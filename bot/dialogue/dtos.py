from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True)
class BillingPeriod:
    month: int
    year: int


@dataclass(frozen=True)
class PaymentDetails:
    full_name: str
    period: BillingPeriod
    address: str
    hot_prev: Decimal
    hot_curr: Decimal
    cold_prev: Decimal
    cold_curr: Decimal
    cold_tariff: Decimal
    hot_tariff: Decimal
    rent_tariff: Decimal
    heat_tariff: Decimal
    apartment_area: Decimal
    sponsorship_amount: Decimal


@dataclass
class PaymentDraft:
    full_name: str | None = None
    period: BillingPeriod | None = None
    address: str | None = None
    hot_prev: Decimal | None = None
    hot_curr: Decimal | None = None
    cold_prev: Decimal | None = None
    cold_curr: Decimal | None = None
    cold_tariff: Decimal | None = None
    hot_tariff: Decimal | None = None
    rent_tariff: Decimal | None = None
    heat_tariff: Decimal | None = None
    apartment_area: Decimal | None = None
    sponsorship_amount: Decimal | None = None


@dataclass
class DialogueState:
    step_index: int = 0
    payload: PaymentDraft = field(default_factory=PaymentDraft)


@dataclass(frozen=True)
class FlowResult:
    success: bool
    error: str | None = None
    finished: bool = False


@dataclass(frozen=True)
class PaymentServiceStart:
    state: dict[str, object]
    prompt: str


@dataclass(frozen=True)
class PaymentServiceResult:
    success: bool
    state: dict[str, object] | None = None
    message: str | None = None
    show_back_keyboard: bool = False
    finished: bool = False
    details_message: str | None = None
    summary_message: str | None = None
    completion_message: str | None = None


@dataclass
class CalculationSection:
    label: str
    body: str
    amount: Decimal
    amount_display: str
