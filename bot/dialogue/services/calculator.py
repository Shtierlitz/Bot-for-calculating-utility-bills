from __future__ import annotations

from decimal import Decimal
from typing import List

from bot.dialogue.dtos import (
    CalculationSection,
    PaymentDetails,
)
from bot.dialogue.services.formatting import ValueFormatter


class PaymentCalculator:
    """Відповідає за побудову текстових повідомлень із підсумками та тарифами."""

    def __init__(self, formatter: ValueFormatter | None = None) -> None:
        self.formatter = formatter or ValueFormatter()

    def summary(self, payload: PaymentDetails) -> str:
        month_name, _, year = self.formatter.month_name(payload.period)
        hot_prev = self.formatter.decimal_for_summary(payload.hot_prev)
        hot_curr = self.formatter.decimal_for_summary(payload.hot_curr)
        cold_prev = self.formatter.decimal_for_summary(payload.cold_prev)
        cold_curr = self.formatter.decimal_for_summary(payload.cold_curr)
        sponsorship = self.formatter.decimal_for_summary(payload.sponsorship_amount)
        return (
            f"Ком.послуги за {month_name} {year}р. {payload.full_name},{payload.address};"
            f"ГВП(показники:{hot_prev}-{hot_curr}),"
            f"ХВП(показники:{cold_prev}-{cold_curr}),"
            f"спонсорство-{sponsorship}"
        )

    def details(self, payload: PaymentDetails) -> str:
        cold_usage = payload.cold_curr - payload.cold_prev
        hot_usage = payload.hot_curr - payload.hot_prev
        area = payload.apartment_area
        cold_tariff = payload.cold_tariff
        hot_tariff = payload.hot_tariff
        rent_tariff = payload.rent_tariff
        heat_tariff = payload.heat_tariff
        sponsorship_amount = payload.sponsorship_amount

        cold_amount = cold_usage * cold_tariff
        hot_amount = hot_usage * hot_tariff
        rent_amount = area * rent_tariff
        heat_amount = area * heat_tariff

        sections = self._build_sections(
            cold_usage, hot_usage, area, cold_tariff, hot_tariff, rent_tariff, heat_tariff,
            cold_amount, hot_amount, rent_amount, heat_amount,
        )
        if sponsorship_amount > 0:
            sections.append(self._build_sponsorship_section(sponsorship_amount))

        _, month_locative, year = self.formatter.month_name(payload.period)
        readings_block = self._build_readings_block(payload, cold_usage, hot_usage)
        tariffs_block = self._build_tariffs_block(cold_tariff, hot_tariff, rent_tariff, heat_tariff)

        lines: List[str] = [readings_block, tariffs_block, '\n\n'.join(section.body for section in sections), '\n\n']

        total = sum(section.amount for section in sections)
        total_display = self.formatter.money(total)

        lines.append(f'✅ ПІДСУМОК до оплати у {month_locative} {year}р.:\n')
        lines.append('Послуга — Сума (грн)\n')
        for section in sections:
            lines.append(f'{section.label} — {section.amount_display}\n')
        lines.append(f'Всього — {total_display} грн ✅')

        return ''.join(lines)

    def _build_sections(
        self,
        cold_usage: Decimal,
        hot_usage: Decimal,
        area: Decimal,
        cold_tariff: Decimal,
        hot_tariff: Decimal,
        rent_tariff: Decimal,
        heat_tariff: Decimal,
        cold_amount: Decimal,
        hot_amount: Decimal,
        rent_amount: Decimal,
        heat_amount: Decimal,
    ) -> List[CalculationSection]:
        formatter = self.formatter
        sections: List[CalculationSection] = []

        cold_body = (
            '🔹 Холодна вода:\n\n'
            f"{formatter.quantity(cold_usage)} × {formatter.tariff(cold_tariff)} = {formatter.money(cold_amount)} грн"
        )
        sections.append(CalculationSection('Холодна вода', cold_body, cold_amount, formatter.money(cold_amount)))

        if hot_tariff > 0 and hot_usage > 0:
            hot_body = (
                '🔸 Гаряча вода:\n\n'
                f"{formatter.quantity(hot_usage)} × {formatter.tariff(hot_tariff)} = {formatter.money(hot_amount)} грн"
            )
            sections.append(CalculationSection('Гаряча вода', hot_body, hot_amount, formatter.money(hot_amount)))

        rent_body = (
            '🧱 Технічне обслуговування будинку:\n\n'
            f"{formatter.quantity(area)} × {formatter.tariff(rent_tariff)} = {formatter.money(rent_amount)} грн"
        )
        sections.append(
            CalculationSection('Технічне обслуговування будинку', rent_body, rent_amount, formatter.money(rent_amount)))

        if heat_tariff > 0 and area > 0:
            heat_body = (
                f'♨️ Опалення (з урахуванням {formatter.quantity(area)} м²):\n\n'
                f"{formatter.quantity(area)} × {formatter.tariff(heat_tariff)} = {formatter.money(heat_amount)} грн"
            )
            sections.append(CalculationSection('Опалення', heat_body, heat_amount, formatter.money(heat_amount)))

        return sections

    def _build_sponsorship_section(self, amount: Decimal) -> CalculationSection:
        amount_display = self.formatter.money(amount)
        body = f'🤝 Спонсорство будинку:\n\n{amount_display} грн'
        return CalculationSection('Спонсорство будинку', body, amount, amount_display)

    def _build_tariffs_block(
        self,
        cold_tariff: Decimal,
        hot_tariff: Decimal,
        rent_tariff: Decimal,
        heat_tariff: Decimal,
    ) -> str:
        fmt = self.formatter
        return (
            '⸻\n\n'
            '💰 Тарифи:\n'
            f" • Холодна вода: {fmt.tariff(cold_tariff)} грн/м³\n"
            f" • Гаряча вода: {fmt.tariff(hot_tariff)} грн/м³\n"
            f" • Технічне обслуговування будинку: {fmt.tariff(rent_tariff)} грн/м²\n"
            f" • Опалення: {fmt.tariff(heat_tariff)} грн/м²\n\n"
            '⸻\n\n'
        )

    def _build_readings_block(self, payload: PaymentDetails, cold_usage: Decimal, hot_usage: Decimal) -> str:
        fmt = self.formatter
        prev_date, current_date = fmt.period_dates(payload.period)
        cold_prev = fmt.decimal_for_summary(payload.cold_prev)
        cold_curr = fmt.decimal_for_summary(payload.cold_curr)
        hot_prev = fmt.decimal_for_summary(payload.hot_prev)
        hot_curr = fmt.decimal_for_summary(payload.hot_curr)
        return (
            '🔁 Повтор розрахунків:\n\n'
            '📸 Показники (м³):\n'
            f'Вода: {current_date} - {prev_date} = Розхід\n'
            f'Холодна:  {cold_curr} - {cold_prev} = {fmt.quantity(cold_usage)} м³\n'
            f'Гаряча:  {hot_curr} - {hot_prev} = {fmt.quantity(hot_usage)} м³\n\n'
        )
