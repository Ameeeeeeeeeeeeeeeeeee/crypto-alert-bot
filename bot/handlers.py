from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.crypto_api import CryptoAPI
from database.db import add_user, is_premium, add_alert, get_user_alerts, delete_alert
from bot.keyboards import get_alert_type_keyboard, get_premium_keyboard, get_alerts_list_keyboard

router = Router()

class AlertStates(StatesGroup):
    waiting_for_price = State()

@router.message(Command("search"))
async def search_coin_handler(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Please provide a coin name or symbol.\nExample: <code>/search BTC</code>")
        return

    query = args[1]
    msg = await message.answer(f"🔍 Searching for <b>{query}</b>...")

    pair_data = await CryptoAPI.search_coin(query)
    if pair_data:
        text = CryptoAPI.format_coin_info(pair_data)
        symbol = pair_data.get("baseToken", {}).get("symbol", "COIN")
        price = pair_data.get("priceUsd", "0")

        await msg.edit_text(
            text,
            reply_markup=get_alert_type_keyboard(symbol, price),
            disable_web_page_preview=True
        )
    else:
        await msg.edit_text(f"❌ Could not find any data for <b>{query}</b>.")

@router.callback_query(F.data.startswith("a:"))
async def process_alert_callback(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    premium = await is_premium(user_id)
    alerts = await get_user_alerts(user_id)

    if len(alerts) >= 3 and not premium:
        await callback.message.answer(
            "⚠️ <b>Alert Limit Reached!</b>\n\n"
            "Free users can have 3 alerts.\n"
            "Upgrade to Premium for unlimited! 🚀",
            reply_markup=get_premium_keyboard()
        )
        await callback.answer()
        return

    parts = callback.data.split(":")
    condition = parts[1]  # above or below
    symbol = parts[2]

    await state.update_data(symbol=symbol, condition=condition)

    await callback.message.answer(
        f"You want to be alerted when <b>{symbol}</b> goes <b>{condition}</b>.\n\n"
        "Enter the target price (USD):"
    )
    await state.set_state(AlertStates.waiting_for_price)
    await callback.answer()

@router.message(AlertStates.waiting_for_price)
async def process_target_price(message: Message, state: FSMContext):
    try:
        target_price = float(message.text.replace("$", "").strip())
    except ValueError:
        await message.answer("Please enter a valid number.")
        return

    data = await state.get_data()
    await add_alert(
        user_id=message.from_user.id,
        coin_id=data['symbol'],
        symbol=data['symbol'],
        target_price=target_price,
        condition=data['condition']
    )

    await message.answer(
        f"✅ <b>Alert Set!</b>\n"
        f"I'll notify you when <b>{data['symbol']}</b> is <b>{data['condition']}</b> <b>${target_price}</b>."
    )
    await state.clear()

@router.message(Command("alerts"))
async def list_alerts_handler(message: Message):
    alerts = await get_user_alerts(message.from_user.id)
    if not alerts:
        await message.answer("You have no active alerts.\nUse /search to find a coin and set one!")
        return

    await message.answer(
        "🔔 <b>Your Active Alerts:</b>\nTap to delete.",
        reply_markup=get_alerts_list_keyboard(alerts)
    )

@router.callback_query(F.data.startswith("del:"))
async def process_delete_alert(callback: CallbackQuery):
    alert_id = int(callback.data.split(":")[1])
    await delete_alert(alert_id)

    alerts = await get_user_alerts(callback.from_user.id)
    if not alerts:
        await callback.message.edit_text("You have no active alerts.")
    else:
        await callback.message.edit_reply_markup(reply_markup=get_alerts_list_keyboard(alerts))

    await callback.answer("Alert deleted.")

@router.message(Command("help"))
async def help_handler(message: Message):
    help_text = (
        "<b>Available Commands:</b>\n"
        "/start - Start the bot\n"
        "/search &lt;coin&gt; - Get live price\n"
        "/alerts - Manage your alerts\n"
        "/help - Show this help\n\n"
        "💡 <b>Tip:</b> You can also just type <code>price btc</code> in any chat!"
    )
    await message.answer(help_text)

@router.message(F.text.lower().regexp(r'^(/?price|/search)\s+(\w+)'))
async def flexible_price_handler(message: Message):
    """Flexible handler for 'price btc', '/price btc', or '/search btc'. Works better in groups."""
    logging.info(f"Received message in {message.chat.type}: {message.text}")
    
    # Extract the coin name (the second part of the match)
    import re
    match = re.search(r'(/?price|/search)\s+(\w+)', message.text.lower())
    if not match:
        return
        
    query = match.group(2)
    msg = await message.answer(f"🔍 Checking <b>{query.upper()}</b>...")

    pair_data = await CryptoAPI.search_coin(query)
    if pair_data:
        text = CryptoAPI.format_coin_info(pair_data)
        symbol = pair_data.get("baseToken", {}).get("symbol", "COIN")
        price = pair_data.get("priceUsd", "0")

        await msg.edit_text(
            text,
            reply_markup=get_alert_type_keyboard(symbol, price),
            disable_web_page_preview=True
        )
    else:
        await msg.edit_text(f"❌ No data found for <b>{query.upper()}</b>.")

@router.callback_query(F.data == "upgrade_premium")
async def upgrade_callback(callback: CallbackQuery):
    await callback.message.answer("To upgrade to Premium, send 100 ⭐️ Stars or contact @Admin.")
    await callback.answer()
