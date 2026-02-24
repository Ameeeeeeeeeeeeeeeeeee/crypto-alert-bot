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

load_dotenv()

TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()
dp.include_router(main_router)

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
    
    await set_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
