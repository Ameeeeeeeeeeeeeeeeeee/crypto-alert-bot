import aiohttp
import logging

# Reuse a single session for speed
_session: aiohttp.ClientSession | None = None

async def get_session():
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )
    return _session

class CryptoAPI:
    BASE_URL = "https://api.dexscreener.com/latest/dex/search"

    @classmethod
    async def search_coin(cls, query: str):
        url = f"{cls.BASE_URL}?q={query}"
        try:
            session = await get_session()
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    pairs = data.get("pairs", [])
                    if not pairs:
                        return None
                    return pairs[0]
                else:
                    logging.error(f"DexScreener API error: {response.status}")
                    return None
        except Exception as e:
            logging.error(f"Failed to fetch data from DexScreener: {e}")
            return None

    @classmethod
    def format_coin_info(cls, pair_data: dict):
        if not pair_data:
            return "Coin not found."

        base_token = pair_data.get("baseToken", {})
        name = base_token.get("name", "Unknown")
        symbol = base_token.get("symbol", "Unknown")
        price_usd = pair_data.get("priceUsd", "N/A")
        change_24h = pair_data.get("priceChange", {}).get("h24", 0)
        dex_id = pair_data.get("dexId", "N/A")

        try:
            volume_raw = pair_data.get("volume", {}).get("h24", 0)
            volume_24h = float(volume_raw) if volume_raw else 0
            vol_str = f"${volume_24h:,.0f}"
        except (ValueError, TypeError):
            vol_str = "N/A"

        try:
            change_val = float(change_24h) if change_24h else 0
        except (ValueError, TypeError):
            change_val = 0

        emoji = "📈" if change_val >= 0 else "📉"

        return (
            f"<b>{name} ({symbol})</b>\n"
            f"DEX: {dex_id.capitalize()}\n\n"
            f"💰 Price: <code>${price_usd}</code>\n"
            f"{emoji} 24h: <code>{change_24h}%</code>\n"
            f"📊 Vol: <code>{vol_str}</code>\n\n"
            f"<a href='{pair_data.get('url', '')}'>View on DexScreener</a>"
        )
