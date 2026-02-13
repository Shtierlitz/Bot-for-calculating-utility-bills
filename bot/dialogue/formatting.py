from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Dict

from bot.dialogue.constants import MONTH_NAMES, MONTH_NAMES_LOCATIVE, THREE_DECIMALS, TWO_DECIMALS


class ValueFormatter:
    """Форматує числові та календарні значення для повідомлень."""

    @staticmethod
    def decimal_for_summary(value: Decimal) -> str:
        text = format(value.normalize(), 'f')
        return text.replace('.', ',')

    @staticmethod
    def decimal_fixed(value: Decimal, quantum: Decimal, strip_trailing: bool = True) -> str:
        try:
            quantized = value.quantize(quantum)
        except InvalidOperation:
            quantized = value
        text = format(quantized, 'f')
        if strip_trailing:
            text = text.rstrip('0').rstrip('.')
        return text or '0'

    @classmethod
    def quantity(cls, value: Decimal) -> str:
        return cls.decimal_fixed(value, THREE_DECIMALS)

    @classmethod
    def tariff(cls, value: Decimal) -> str:
        return cls.decimal_fixed(value, THREE_DECIMALS)

    @classmethod
    def money(cls, value: Decimal) -> str:
        return cls.decimal_fixed(value, TWO_DECIMALS, strip_trailing=False)

    @staticmethod
    def month_name(period: Dict[str, int]) -> tuple[str, str, int]:
        month = period['month']
        year = period['year']
        return MONTH_NAMES.get(month, ''), MONTH_NAMES_LOCATIVE.get(month, MONTH_NAMES.get(month, '')), year

    @staticmethod
    def period_dates(period: Dict[str, int]) -> tuple[str, str]:
        month = period['month']
        year = period['year']
        prev_month = month - 1
        prev_year = year
        if prev_month == 0:
            prev_month = 12
            prev_year -= 1
        prev_date = f'01.{prev_month:02d}.{prev_year}'
        current_date = f'01.{month:02d}.{year}'
        return prev_date, current_date


__all__ = ['ValueFormatter']
