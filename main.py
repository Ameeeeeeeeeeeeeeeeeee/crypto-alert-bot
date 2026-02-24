import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, BotCommand
from dotenv import load_dotenv

from bot.handlers import router as main_router
from database.db import init_db, add_user
from services.alerts import setup_scheduler
from aiohttp import web

load_dotenv()

TOKEN = getenv("BOT_TOKEN")
PORT = int(getenv("PORT", 8080))

dp = Dispatcher()
dp.include_router(main_router)

# --- Dummy Web Server for Render Free Tier ---
async def handle_ping(request):
    return web.Response(text="Bot is alive!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logging.info(f"Web server started on port {PORT}")
# ---------------------------------------------

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await add_user(message.from_user.id, message.from_user.username)
    await message.answer(
        f"Hello, <b>{message.from_user.full_name}</b>!\n\n"
        "Welcome to the <b>Crypto Analytics & Alert Bot</b>. 🚀\n\n"
        "I can help you track real-time prices for any coin on decentralized exchanges.\n\n"
        "<b>Commands:</b>\n"
        "🔍 /search - Find a coin\n"
        "🔔 /alerts - Set price alerts\n"
        "❓ /help - See all commands"
    )

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="search", description="Search for a coin"),
        BotCommand(command="alerts", description="Manage alerts"),
        BotCommand(command="help", description="Show help")
    ]
    await bot.set_my_commands(commands)

async def main() -> None:
    # Initialize DB
    await init_db()
    
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    # Setup background alerts
    setup_scheduler(bot)
    
    # Start the dummy web server
    asyncio.create_task(start_web_server())
    
    await set_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped!")
