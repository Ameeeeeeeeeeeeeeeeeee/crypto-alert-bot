import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.db import get_all_alerts, delete_alert
from services.crypto_api import CryptoAPI
from aiogram import Bot

async def check_alerts(bot: Bot):
    alerts = await get_all_alerts()
    if not alerts:
        return

    logging.info(f"Checking {len(alerts)} alerts...")
    
    # Simple alert logic: Group by coin_id to minimize API calls
    coin_ids = list(set([a[2] for a in alerts]))
    
    for coin_id in coin_ids:
        # In a real app, we'd use a bulk API if available. 
        # DexScreener doesn't have a bulk 'by id' for search endpoint easily, 
        # but for this demo, we'll fetch them individually or use search.
        # For simplicity, we'll re-search the symbol/id.
        pair_data = await CryptoAPI.search_coin(coin_id)
        if not pair_data:
            continue
            
        current_price = float(pair_data.get("priceUsd", 0))
        
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
                        f"<a href='{pair_data.get('url')}'>Trade now on DexScreener</a>"
                    )
                    await bot.send_message(user_id, text)
                    await delete_alert(alert_id)
                    logging.info(f"Alert {alert_id} triggered for user {user_id}")
                except Exception as e:
                    logging.error(f"Failed to send alert to user {user_id}: {e}")

def setup_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_alerts, "interval", minutes=5, args=[bot])
    scheduler.start()
    return scheduler
