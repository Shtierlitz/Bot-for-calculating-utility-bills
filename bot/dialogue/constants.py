from __future__ import annotations

from decimal import Decimal
import re


FULL_NAME_STEP = 'full_name'
PERIOD_STEP = 'period'
ADDRESS_STEP = 'address'
HOT_PREV_STEP = 'hot_prev'
HOT_CURR_STEP = 'hot_curr'
COLD_PREV_STEP = 'cold_prev'
COLD_CURR_STEP = 'cold_curr'
COLD_TARIFF_STEP = 'cold_tariff'
HOT_TARIFF_STEP = 'hot_tariff'
RENT_TARIFF_STEP = 'rent_tariff'
HEAT_TARIFF_STEP = 'heat_tariff'
AREA_STEP = 'apartment_area'

STEP_ORDER = [
    FULL_NAME_STEP,
    PERIOD_STEP,
    ADDRESS_STEP,
    HOT_PREV_STEP,
    HOT_CURR_STEP,
    COLD_PREV_STEP,
    COLD_CURR_STEP,
    COLD_TARIFF_STEP,
    HOT_TARIFF_STEP,
    RENT_TARIFF_STEP,
    HEAT_TARIFF_STEP,
    AREA_STEP,
]

STEP_PROMPTS = {
    FULL_NAME_STEP: 'Напишіть, будь ласка, Ваше ПІБ повністю (наприклад, Корнієнко Сергій Іванович).',
    PERIOD_STEP: 'Вкажіть місяць і рік у форматі MM-YYYY (наприклад, 01-2026).',
    ADDRESS_STEP: 'Введіть адресу (вулиця, будинок, квартира).',
    HOT_PREV_STEP: 'Напишіть попередні показники лічильника гарячої води.',
    HOT_CURR_STEP: 'Напишіть поточні показники лічильника гарячої води.',
    COLD_PREV_STEP: 'Напишіть попередні показники лічильника холодної води.',
    COLD_CURR_STEP: 'Напишіть поточні показники лічильника холодної води.',
    COLD_TARIFF_STEP: 'Вкажіть тариф холодної води (грн/м³), наприклад 30.384.',
    HOT_TARIFF_STEP: 'Вкажіть тариф гарячої води (грн/м³). Якщо не користуєтесь, введіть 0.',
    RENT_TARIFF_STEP: 'Вкажіть тариф технічного обслуговування будинку (грн/м²), наприклад 8.',
    HEAT_TARIFF_STEP: 'Вкажіть тариф опалення (грн/м²). Якщо опалення відсутнє, введіть 0.',
    AREA_STEP: 'Вкажіть площу квартири (м²), наприклад 68.1. Якщо технічне обслуговування будинку не потрібне, введіть 0.',
}

STEP_PAYLOAD_KEYS = {
    FULL_NAME_STEP: 'full_name',
    PERIOD_STEP: 'period',
    ADDRESS_STEP: 'address',
    HOT_PREV_STEP: 'hot_prev',
    HOT_CURR_STEP: 'hot_curr',
    COLD_PREV_STEP: 'cold_prev',
    COLD_CURR_STEP: 'cold_curr',
    COLD_TARIFF_STEP: 'cold_tariff',
    HOT_TARIFF_STEP: 'hot_tariff',
    RENT_TARIFF_STEP: 'rent_tariff',
    HEAT_TARIFF_STEP: 'heat_tariff',
    AREA_STEP: 'apartment_area',
}

PERIOD_PATTERN = re.compile(r'^(0[1-9]|1[0-2])-(\d{4,5})$')

MONTH_NAMES = {
    1: 'січень',
    2: 'лютий',
    3: 'березень',
    4: 'квітень',
    5: 'травень',
    6: 'червень',
    7: 'липень',
    8: 'серпень',
    9: 'вересень',
    10: 'жовтень',
    11: 'листопад',
    12: 'грудень',
}

MONTH_NAMES_LOCATIVE = {
    1: 'січні',
    2: 'лютому',
    3: 'березні',
    4: 'квітні',
    5: 'травні',
    6: 'червні',
    7: 'липні',
    8: 'серпні',
    9: 'вересні',
    10: 'жовтні',
    11: 'листопаді',
    12: 'грудні',
}

BACK_BUTTON_TEXT = '⬅️ Назад'
BACK_TOKENS = {'назад', 'back', 'повернутися', 'повернутись', BACK_BUTTON_TEXT.strip().lower()}

THREE_DECIMALS = Decimal('0.001')
TWO_DECIMALS = Decimal('0.01')

TEXT_STEPS = {FULL_NAME_STEP, ADDRESS_STEP}
NUMERIC_STEPS = {
    HOT_PREV_STEP,
    HOT_CURR_STEP,
    COLD_PREV_STEP,
    COLD_CURR_STEP,
    COLD_TARIFF_STEP,
    HOT_TARIFF_STEP,
    RENT_TARIFF_STEP,
    HEAT_TARIFF_STEP,
    AREA_STEP,
}

__all__ = [
    'FULL_NAME_STEP',
    'PERIOD_STEP',
    'ADDRESS_STEP',
    'HOT_PREV_STEP',
    'HOT_CURR_STEP',
    'COLD_PREV_STEP',
    'COLD_CURR_STEP',
    'COLD_TARIFF_STEP',
    'HOT_TARIFF_STEP',
    'RENT_TARIFF_STEP',
    'HEAT_TARIFF_STEP',
    'AREA_STEP',
    'STEP_ORDER',
    'STEP_PROMPTS',
    'STEP_PAYLOAD_KEYS',
    'PERIOD_PATTERN',
    'MONTH_NAMES',
    'MONTH_NAMES_LOCATIVE',
    'BACK_BUTTON_TEXT',
    'BACK_TOKENS',
    'THREE_DECIMALS',
    'TWO_DECIMALS',
    'TEXT_STEPS',
    'NUMERIC_STEPS',
]
