from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal, InvalidOperation
from typing import cast

from bot.dialogue.dtos import BillingPeriod, PaymentDetails, PaymentDraft


class PaymentDraftMapper:
    """Maps payment DTOs to storage data and builds complete calculation input."""

    def to_dict(self, draft: PaymentDraft) -> dict[str, object]:
        period = None
        if draft.period is not None:
            period = {'month': draft.period.month, 'year': draft.period.year}

        return {
            'full_name': draft.full_name,
            'period': period,
            'address': draft.address,
            'hot_prev': draft.hot_prev,
            'hot_curr': draft.hot_curr,
            'cold_prev': draft.cold_prev,
            'cold_curr': draft.cold_curr,
            'cold_tariff': draft.cold_tariff,
            'hot_tariff': draft.hot_tariff,
            'rent_tariff': draft.rent_tariff,
            'heat_tariff': draft.heat_tariff,
            'apartment_area': draft.apartment_area,
            'sponsorship_amount': draft.sponsorship_amount,
        }

    def from_dict(self, data: Mapping[str, object] | None) -> PaymentDraft:
        source = data or {}
        return PaymentDraft(
            full_name=self._restore_text(source.get('full_name')),
            period=self._restore_period(source.get('period')),
            address=self._restore_text(source.get('address')),
            hot_prev=self._restore_decimal(source.get('hot_prev')),
            hot_curr=self._restore_decimal(source.get('hot_curr')),
            cold_prev=self._restore_decimal(source.get('cold_prev')),
            cold_curr=self._restore_decimal(source.get('cold_curr')),
            cold_tariff=self._restore_decimal(source.get('cold_tariff')),
            hot_tariff=self._restore_decimal(source.get('hot_tariff')),
            rent_tariff=self._restore_decimal(source.get('rent_tariff')),
            heat_tariff=self._restore_decimal(source.get('heat_tariff')),
            apartment_area=self._restore_decimal(source.get('apartment_area')),
            sponsorship_amount=self._restore_decimal(source.get('sponsorship_amount', Decimal('0'))),
        )

    def to_details(self, draft: PaymentDraft) -> PaymentDetails:
        missing = [item.name for item in fields(draft) if getattr(draft, item.name) is None]
        if missing:
            raise ValueError(f"PaymentDraft is incomplete; missing fields: {', '.join(missing)}")

        return PaymentDetails(
            full_name=cast(str, draft.full_name),
            period=cast(BillingPeriod, draft.period),
            address=cast(str, draft.address),
            hot_prev=cast(Decimal, draft.hot_prev),
            hot_curr=cast(Decimal, draft.hot_curr),
            cold_prev=cast(Decimal, draft.cold_prev),
            cold_curr=cast(Decimal, draft.cold_curr),
            cold_tariff=cast(Decimal, draft.cold_tariff),
            hot_tariff=cast(Decimal, draft.hot_tariff),
            rent_tariff=cast(Decimal, draft.rent_tariff),
            heat_tariff=cast(Decimal, draft.heat_tariff),
            apartment_area=cast(Decimal, draft.apartment_area),
            sponsorship_amount=cast(Decimal, draft.sponsorship_amount),
        )

    @staticmethod
    def _restore_text(value: object) -> str | None:
        return value if isinstance(value, str) else None

    @staticmethod
    def _restore_period(value: object) -> BillingPeriod | None:
        if isinstance(value, BillingPeriod):
            return value
        if not isinstance(value, Mapping):
            return None
        try:
            return BillingPeriod(month=int(value['month']), year=int(value['year']))
        except (KeyError, TypeError, ValueError):
            return None

    @staticmethod
    def _restore_decimal(value: object) -> Decimal | None:
        if value is None or isinstance(value, bool):
            return None
        if isinstance(value, Decimal):
            return value
        try:
            restored = Decimal(str(value))
        except (InvalidOperation, ValueError):
            return None
        return restored if restored.is_finite() else None
