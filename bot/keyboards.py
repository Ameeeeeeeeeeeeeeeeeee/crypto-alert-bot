from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

def get_alert_type_keyboard(symbol: str, current_price: str):
    """Short callback data to stay under Telegram's 64-byte limit."""
    builder = InlineKeyboardBuilder()
    builder.button(text=f"🔔 Alert Above ${current_price}", callback_data=f"a:above:{symbol}")
    builder.button(text=f"🔔 Alert Below ${current_price}", callback_data=f"a:below:{symbol}")
    builder.adjust(1)
    return builder.as_markup()

def get_premium_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Upgrade to Premium ⭐", callback_data="upgrade_premium")
    return builder.as_markup()

def get_alerts_list_keyboard(alerts):
    builder = InlineKeyboardBuilder()
    for alert in alerts:
        alert_id, _, _, symbol, price, cond, _ = alert
        builder.button(
            text=f"❌ {symbol} {cond} ${price}",
            callback_data=f"del:{alert_id}"
        )
    builder.adjust(1)
    return builder.as_markup()
