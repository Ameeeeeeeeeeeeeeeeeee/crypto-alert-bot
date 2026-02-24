import asyncio
import os
from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

async def update_bot_metadata():
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("Error: No BOT_TOKEN found in .env")
        return

    bot = Bot(token=token)
    
    # Text for the "Description" section (The "What can this bot do?" screen)
    full_description = (
        "🔍 Live Search: Get instant price, 24h change, and volume for any coin.\n"
        "🔔 Price Alerts: Set targets for your favorite tokens and get notified!\n"
        "👥 Group Ready: Add me to your group and just type 'price btc' for instant updates.\n"
        "💎 Premium Features: Upgrade for unlimited alerts and pro tracking.\n\n"
        "🚀 Created by @ame_kt\n\n"
        "How to use:\n"
        "1. Type /search <coin> to find a token.\n"
        "2. Click 'Alert Above' or 'Alert Below' to track it.\n"
        "3. Add to your group for shared price lookups!"
    )

    try:
        print("Updating bot description...")
        await bot.set_my_description(full_description)
        print("Success!")
    except Exception as e:
        print(f"Failed to update description: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(update_bot_metadata())
