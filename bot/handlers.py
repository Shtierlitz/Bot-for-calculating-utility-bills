from __future__ import annotations

from decimal import Decimal, InvalidOperation
import re

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes


WELCOME_MESSAGE = (
    '👋 Вітаю, {name}! Я допоможу підрахувати та підготувати текст для комунальних платежів.\n\n'
    'Давайте починати: надсилайте відповіді українською мовою. Для виправлень скористайтеся кнопкою "Назад".'
)

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
    FULL_NAME_STEP: 'Напишіть, будь ласка, Ваше ПІБ повністю (наприклад, Іваненко Іван Іванович).',
    PERIOD_STEP: 'Вкажіть місяць і рік у форматі MM-YYYY (наприклад, 01-2026).',
    ADDRESS_STEP: 'Введіть адресу (вулиця, будинок, квартира).',
    HOT_PREV_STEP: 'Напишіть попередні показники лічильника гарячої води.',
    HOT_CURR_STEP: 'Напишіть поточні показники лічильника гарячої води.',
    COLD_PREV_STEP: 'Напишіть попередні показники лічильника холодної води.',
    COLD_CURR_STEP: 'Напишіть поточні показники лічильника холодної води.',
    COLD_TARIFF_STEP: 'Вкажіть тариф холодної води (грн/м³), наприклад 30.384.',
    HOT_TARIFF_STEP: 'Вкажіть тариф гарячої води (грн/м³). Якщо не користуєтесь, введіть 0.',
    RENT_TARIFF_STEP: 'Вкажіть тариф квартплати (грн/м²), наприклад 8.',
    HEAT_TARIFF_STEP: 'Вкажіть тариф опалення (грн/м²). Якщо опалення відсутнє, введіть 0.',
    AREA_STEP: 'Вкажіть площу квартири (м²), наприклад 68.1. Якщо квартплата не потрібна, введіть 0.',
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


def _keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[BACK_BUTTON_TEXT]], resize_keyboard=True, one_time_keyboard=False)


def _prompt_for_step(step: str) -> str:
    return STEP_PROMPTS[step]


def _set_step(context: ContextTypes.DEFAULT_TYPE, index: int) -> None:
    context.user_data['step_index'] = index
    context.user_data['step'] = STEP_ORDER[index]


def _current_step(context: ContextTypes.DEFAULT_TYPE) -> str:
    if 'step' not in context.user_data:
        raise RuntimeError('Step is not initialized')
    return context.user_data['step']


def _advance_step(context: ContextTypes.DEFAULT_TYPE) -> bool:
    index = context.user_data.get('step_index')
    if index is None or index + 1 >= len(STEP_ORDER):
        return False
    _set_step(context, index + 1)
    return True


def _go_to_previous_step(context: ContextTypes.DEFAULT_TYPE) -> bool:
    index = context.user_data.get('step_index')
    if index is None or index == 0:
        return False
    previous_index = index - 1
    previous_step = STEP_ORDER[previous_index]
    payload_key = STEP_PAYLOAD_KEYS[previous_step]
    payload: dict = context.user_data.setdefault('payload', {})
    payload.pop(payload_key, None)
    _set_step(context, previous_index)
    return True


def _is_back_command(text: str) -> bool:
    normalized = text.strip().lower()
    if not normalized:
        return False
    normalized = normalized.rstrip('.,!')
    if normalized.startswith('/'):
        normalized = normalized[1:]
    if normalized in BACK_TOKENS:
        return True
    first_token = normalized.split()[0]
    return first_token in BACK_TOKENS


def _parse_period(raw_text: str) -> tuple[int, int] | None:
    text = raw_text.strip()
    match = PERIOD_PATTERN.fullmatch(text)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def _parse_decimal_value(raw_text: str) -> Decimal | None:
    trimmed = raw_text.strip()
    if not trimmed:
        return None
    normalized = trimmed.replace(' ', '').replace(',', '.').rstrip('.').rstrip(',')
    if not normalized:
        return None
    try:
        return Decimal(normalized)
    except InvalidOperation:
        return None


def _format_decimal_for_summary(value: Decimal) -> str:
    text = format(value.normalize(), 'f')
    return text.replace('.', ',')


def _format_decimal_fixed(value: Decimal, quantum: Decimal, strip_trailing: bool = True) -> str:
    try:
        quantized = value.quantize(quantum)
    except InvalidOperation:
        quantized = value
    text = format(quantized, 'f')
    if strip_trailing:
        text = text.rstrip('0').rstrip('.')
    return text or '0'


def _format_quantity(value: Decimal) -> str:
    return _format_decimal_fixed(value, THREE_DECIMALS)


def _format_tariff_value(value: Decimal) -> str:
    return _format_decimal_fixed(value, THREE_DECIMALS)


def _format_money(value: Decimal) -> str:
    return _format_decimal_fixed(value, TWO_DECIMALS, strip_trailing=False)


def _format_summary(data: dict[str, object]) -> str:
    period = data['period']  # type: ignore[index]
    month_name = MONTH_NAMES.get(period['month'], '')  # type: ignore[index]
    year = period['year']  # type: ignore[index]
    hot_prev = _format_decimal_for_summary(data['hot_prev'])  # type: ignore[arg-type]
    hot_curr = _format_decimal_for_summary(data['hot_curr'])  # type: ignore[arg-type]
    cold_prev = _format_decimal_for_summary(data['cold_prev'])  # type: ignore[arg-type]
    cold_curr = _format_decimal_for_summary(data['cold_curr'])  # type: ignore[arg-type]
    return (
        f"Ком.послуги за {month_name} {year}р. {data['full_name']},{data['address']};"
        f"ГВП(показники:{hot_prev}-{hot_curr}),"
        f"ХВП(показники:{cold_prev}-{cold_curr})"
    )


def _period_date_strings(period: dict[str, int]) -> tuple[str, str]:
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


def _build_readings_section(
    data: dict[str, object],
    cold_usage_text: str,
    hot_usage_text: str,
    cold_usage: Decimal,
    hot_usage: Decimal,
) -> str:
    period = data['period']  # type: ignore[index]
    prev_date, current_date = _period_date_strings(period)
    cold_prev_text = _format_decimal_for_summary(data['cold_prev'])  # type: ignore[arg-type]
    cold_curr_text = _format_decimal_for_summary(data['cold_curr'])  # type: ignore[arg-type]
    hot_prev_text = _format_decimal_for_summary(data['hot_prev'])  # type: ignore[arg-type]
    hot_curr_text = _format_decimal_for_summary(data['hot_curr'])  # type: ignore[arg-type]

    lines = ['🔁 Повтор розрахунків:\n\n', '📸 Показники (м³):\n', f'Вода - {prev_date} - {current_date} - Розхід\n',
             f'Холодна - {cold_prev_text} - {cold_curr_text} - {cold_usage_text} м³\n',
             f'Гаряча - {hot_prev_text} - {hot_curr_text} - {hot_usage_text} м³\n', '\n']

    return ''.join(lines)


def _build_calculation_message(data: dict[str, object]) -> str:
    cold_usage = data['cold_curr'] - data['cold_prev']  # type: ignore[operator]
    hot_usage = data['hot_curr'] - data['hot_prev']  # type: ignore[operator]
    area = data['apartment_area']  # type: ignore[assignment]
    cold_tariff = data['cold_tariff']  # type: ignore[assignment]
    hot_tariff = data['hot_tariff']  # type: ignore[assignment]
    rent_tariff = data['rent_tariff']  # type: ignore[assignment]
    heat_tariff = data['heat_tariff']  # type: ignore[assignment]

    cold_amount = (cold_usage * cold_tariff).quantize(TWO_DECIMALS)
    hot_amount = (hot_usage * hot_tariff).quantize(TWO_DECIMALS)
    rent_amount = (area * rent_tariff).quantize(TWO_DECIMALS)
    heat_amount = (area * heat_tariff).quantize(TWO_DECIMALS)

    cold_amount_display = _format_money(cold_amount)
    hot_amount_display = _format_money(hot_amount)
    rent_amount_display = _format_money(rent_amount)
    heat_amount_display = _format_money(heat_amount)

    cold_usage_text = _format_quantity(cold_usage)
    hot_usage_text = _format_quantity(hot_usage)
    area_text = _format_quantity(area)
    cold_tariff_text = _format_tariff_value(cold_tariff)
    hot_tariff_text = _format_tariff_value(hot_tariff)
    rent_tariff_text = _format_tariff_value(rent_tariff)
    heat_tariff_text = _format_tariff_value(heat_tariff)

    readings_block = _build_readings_section(data, cold_usage_text, hot_usage_text, cold_usage, hot_usage)

    sections: list[str] = []
    breakdown: list[tuple[str, Decimal, str]] = []

    sections.append(
        '🔹 Холодна вода:\n\n'
        f'{cold_usage_text} × {cold_tariff_text} = {cold_amount_display} грн'
    )
    breakdown.append(('Холодна вода', cold_amount, cold_amount_display))

    if hot_tariff > 0 and hot_usage > 0:
        sections.append(
            '🔸 Гаряча вода:\n\n'
            f'{hot_usage_text} × {hot_tariff_text} = {hot_amount_display} грн'
        )
        breakdown.append(('Гаряча вода', hot_amount, hot_amount_display))

    sections.append(
        '🧱 Квартплата:\n\n'
        f'{area_text} × {rent_tariff_text} = {rent_amount_display} грн'
    )
    breakdown.append(('Квартплата', rent_amount, rent_amount_display))

    if heat_tariff > 0 and area > 0:
        sections.append(
            f'♨️ Опалення (з урахуванням {area_text} м²):\n\n'
            f'{area_text} × {heat_tariff_text} = {heat_amount_display} грн'
        )
        breakdown.append(('Опалення', heat_amount, heat_amount_display))

    tariffs_block = (
        '⸻\n\n'
        '💰 Тарифи:\n'
        f" • Холодна вода: {cold_tariff_text} грн/м³\n"
        f" • Гаряча вода: {hot_tariff_text} грн/м³\n"
        f" • Квартплата: {rent_tariff_text} грн/м²\n"
        f" • Опалення: {heat_tariff_text} грн/м²\n\n"
        '⸻\n\n'
    )

    lines = [readings_block, tariffs_block, '\n\n'.join(sections), '\n\n']

    period = data['period']  # type: ignore[index]
    month_locative = MONTH_NAMES_LOCATIVE.get(period['month'], MONTH_NAMES.get(period['month'], ''))  # type: ignore[index]
    year = period['year']  # type: ignore[index]

    total = sum(amount for _, amount, _ in breakdown)
    total_display = _format_money(total)

    lines.append(f'✅ ПІДСУМОК до оплати у {month_locative} {year}р.:\n')
    lines.append('Послуга — Сума (грн)\n')
    for label, _, amount_display in breakdown:
        lines.append(f'{label} — {amount_display}\n')
    lines.append(f'Всього — {total_display} грн ✅')

    return ''.join(lines)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Виводить привітання та запитує початкові дані."""

    user = update.effective_user
    name = user.first_name if user and user.first_name else 'шановний користувачу'
    context.user_data.clear()
    context.user_data['payload'] = {}
    _set_step(context, 0)
    await update.message.reply_text(WELCOME_MESSAGE.format(name=name))
    await update.message.reply_text(_prompt_for_step(_current_step(context)), reply_markup=_keyboard())


async def handle_plain_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Покроково збирає дані для підготовки платіжного повідомлення."""

    if 'step' not in context.user_data:
        await update.message.reply_text('Щоб почати, натисніть /start та дотримуйтеся підказок.', reply_markup=ReplyKeyboardRemove())
        return

    payload: dict = context.user_data.setdefault('payload', {})
    user_message = update.message.text or ''

    if _is_back_command(user_message):
        if _go_to_previous_step(context):
            await update.message.reply_text(
                'Повертаємося до попереднього кроку.\n' + _prompt_for_step(_current_step(context)),
                reply_markup=_keyboard(),
            )
        else:
            await update.message.reply_text('Ви вже на першому кроці, повертатися нікуди.', reply_markup=_keyboard())
        return

    current_step = _current_step(context)

    if current_step == FULL_NAME_STEP:
        payload['full_name'] = user_message.strip()
        _advance_step(context)
        await update.message.reply_text(_prompt_for_step(_current_step(context)), reply_markup=_keyboard())
        return

    if current_step == PERIOD_STEP:
        parsed_period = _parse_period(user_message)
        if not parsed_period:
            await update.message.reply_text('Не впізнаю формат. Використайте MM-YYYY, наприклад 01-2026.')
            return
        month, year = parsed_period
        payload['period'] = {'month': month, 'year': year}
        _advance_step(context)
        await update.message.reply_text(_prompt_for_step(_current_step(context)), reply_markup=_keyboard())
        return

    if current_step == ADDRESS_STEP:
        payload['address'] = user_message.strip()
        _advance_step(context)
        await update.message.reply_text(_prompt_for_step(_current_step(context)), reply_markup=_keyboard())
        return

    if current_step in {
        HOT_PREV_STEP,
        HOT_CURR_STEP,
        COLD_PREV_STEP,
        COLD_CURR_STEP,
        COLD_TARIFF_STEP,
        HOT_TARIFF_STEP,
        RENT_TARIFF_STEP,
        HEAT_TARIFF_STEP,
        AREA_STEP,
    }:
        value = _parse_decimal_value(user_message)
        if value is None:
            await update.message.reply_text('Будь ласка, введіть числове значення (наприклад, 123.45).')
            return
        payload[STEP_PAYLOAD_KEYS[current_step]] = value

        if current_step == AREA_STEP:
            summary = _format_summary(payload)
            await update.message.reply_text(summary)
            details = _build_calculation_message(payload)
            await update.message.reply_text(details, reply_markup=ReplyKeyboardRemove())
            context.user_data.clear()
            await update.message.reply_text('Щоб підготувати ще одне повідомлення, натисніть /start.')
            return

        _advance_step(context)
        await update.message.reply_text(_prompt_for_step(_current_step(context)), reply_markup=_keyboard())
        return

    await update.message.reply_text('Сталася неочікувана ситуація. Спробуйте почати заново через /start.')
