import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.db import get_all_alerts, delete_alert
from services.crypto_api import CryptoAPI
from aiogram import Bot

async def check_alerts(bot: Bot):
    try:
        alerts = await get_all_alerts()
    except Exception as e:
        logging.error(f"Failed to fetch alerts from DB: {e}")
        return

    if not alerts:
        return

    logging.info(f"Checking {len(alerts)} alerts...")
    
    # Group by coin_id to minimize API calls
    coin_ids = list(set([a[2] for a in alerts]))
    
    for coin_id in coin_ids:
        try:
            pair_data = await CryptoAPI.search_coin(coin_id)
        except Exception as e:
            logging.error(f"Failed to fetch price for {coin_id}: {e}")
            continue

        if not pair_data:
            continue
            
        try:
            current_price = float(pair_data.get("priceUsd", 0))
        except (ValueError, TypeError):
            logging.error(f"Invalid price data for {coin_id}")
            continue
        
        # Check all alerts for this coin
        for alert in [a for a in alerts if a[2] == coin_id]:
            alert_id, user_id, _, symbol, target_price, condition, _ = alert
            
            triggered = False
            if condition == "above" and current_price >= target_price:
                triggered = True
            elif condition == "below" and current_price <= target_price:
                triggered = True
                
            if triggered:
                try:
                    text = (
                        f"🔔 <b>Alert Triggered!</b>\n\n"
                        f"<b>{symbol}</b> has hit your target of <b>${target_price}</b>!\n"
                        f"Current Price: <code>${current_price}</code>\n\n"
                        f"<a href='{pair_data.get('url', '')}'>Trade now on DexScreener</a>"
                    )
                    await bot.send_message(user_id, text, parse_mode="HTML")
                    await delete_alert(alert_id)
                    logging.info(f"Alert {alert_id} triggered for user {user_id}")
                except Exception as e:
                    logging.error(f"Failed to send alert to user {user_id}: {e}")

        # Small delay between API calls to avoid rate limiting
        await asyncio.sleep(1)

def setup_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_alerts, "interval", minutes=5, args=[bot])
    scheduler.start()
    logging.info("✅ Alert scheduler started (checking every 5 minutes)")
    return scheduler
