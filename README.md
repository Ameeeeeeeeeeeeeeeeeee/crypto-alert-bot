# 🚀 Crypto Analytics & Alert Bot

A professional Telegram bot built with Python and Aiogram to provide real-time cryptocurrency analytics and custom price alerts for decentralized exchanges.

## ✨ Key Features

- 🔍 **Real-time DEX Search**: Get instant price, 24h change, and volume for any token (SOL, ETH, BSC, BASE, etc.) using the DexScreener API.
- 🔔 **Smart Price Alerts**: Set targets for your favorite tokens and receive instant notifications when they are hit.
- 👥 **Group Integrated**: Add the bot to your group and simply type `price <coin>` for quick shared updates.
- 💎 **Monetization Ready**: Tiered subscription system with premium limits and "Stars" payment prompts.
- 📊 **PostgreSQL Persistence**: Fully compatible with Render hosting and persistent databases.

## 🛠️ Commands

- `/start` - Launch the bot and register.
- `/search <coin>` - Find live market data for a specific token.
- `/alerts` - View and manage your active price alerts.
- `/help` - Quick guide on features and commands.
- `price <coin>` - Quick-fire price check (works in groups without a command).

## 🚀 Setup & Local Deployment

1. **Clone the repo:**

   ```bash
   git clone https://github.com/Ameeeeeeeeeeeeeeeeeee/crypto-alert-bot.git
   cd crypto-alert-bot
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   Create a `.env` file in the root directory:

   ```env
   BOT_TOKEN=your_telegram_bot_token
   DATABASE_URL=postgresql://user:password@localhost/db_name (or your local sqlite path)
   PORT=8080
   ```

4. **Run the bot:**
   ```bash
   python main.py
   ```

## 🏗️ Architecture

- **Core**: `aiogram` (Asynchronous Telegram framework)
- **Data**: `SQLAlchemy` + `PostgreSQL` / `aiosqlite`
- **Networking**: `aiohttp` for high-performance API calls.
- **Scheduler**: `APScheduler` for background price monitoring.

## 📄 License

This project is open-source and free to use.
