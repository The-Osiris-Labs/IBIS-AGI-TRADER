#!/usr/bin/env python3
"""
IBIS FAST - Continuous Trading System
Scans and trades when signals appear.
"""

import asyncio
import os
import logging
from pathlib import Path

os.environ["PYTHONPATH"] = "/root/projects/Dont enter unless solicited/AGI Trader"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(
            "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_fast.log"
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

DATA_DIR = Path("/root/projects/Dont enter unless solicited/AGI Trader/data")
DATA_DIR.mkdir(exist_ok=True)

TRADING = {
    "TAKE_PROFIT": 0.02,  # 2.0% - Balanced 1:1 risk/reward
    "STOP_LOSS": 0.02,  # 2.0%
    "POSITION_PCT": 0.50,
    "MIN_TRADE": 5.0,
    "MAX_POSITION_PCT": 0.75,
    "SCORE_THRESHOLD": 50,  # Lowered for more trades
}


async def get_client():
    from ibis.exchange.kucoin_client import get_kucoin_client

    return get_kucoin_client()


async def get_intel():
    from ibis.free_intelligence import FreeIntelligence

    return FreeIntelligence()


async def get_balance(client):
    balances = await client.get_all_balances()
    return balances.get("USDT", {}).get("available", 0)


async def get_price(client, symbol):
    try:
        ticker = await client.get_ticker(f"{symbol}-USDT")
        return ticker.price
    except:
        return None


async def get_score(free_intel, symbol):
    try:
        result = await free_intel.get_comprehensive_sentiment(symbol)
        return result.get("score", 50), result.get("confidence", 50)
    except:
        return 50, 50


async def execute_buy(client, symbol, amount):
    try:
        order = await client.create_market_order(f"{symbol}-USDT", "buy", amount)
        logger.info(f"BUY: {symbol} ${amount:.2f}")
        return order
    except Exception as e:
        logger.error(f"Buy failed {symbol}: {e}")
        return None


async def place_limit(client, symbol, entry_price, quantity):
    try:
        tp = entry_price * 1.03
        order = await client.place_limit_order(
            symbol=f"{symbol}-USDT", side="sell", price=tp, size=quantity
        )
        logger.info(f"LIMIT SELL: {symbol} @ {tp:.8f} (+3%)")
        return order
    except Exception as e:
        logger.error(f"Limit failed {symbol}: {e}")
        return None


async def calculate_size(capital, confidence):
    min_size = TRADING["MIN_TRADE"]
    max_size = capital * TRADING["MAX_POSITION_PCT"]
    base_size = capital * TRADING["POSITION_PCT"]
    size = base_size * (0.8 + confidence * 0.4)
    final = max(min_size, min(size, max_size))
    return round(final, 2)


async def scan_and_trade(client, free_intel):
    capital = await get_balance(client)
    symbols = [
        "BTC",
        "ETH",
        "SOL",
        "XRP",
        "ADA",
        "DOGE",
        "MATIC",
        "DOT",
        "LINK",
        "UNI",
        "ATOM",
        "LTC",
        "NEAR",
        "ARB",
        "OP",
        "INJ",
        "SUI",
        "SEI",
        "ENS",
        "LDO",
        "RNDR",
    ]

    trades = 0

    for symbol in symbols:
        score, conf = await get_score(free_intel, symbol)

        if score < TRADING["SCORE_THRESHOLD"]:
            continue

        price = await get_price(client, symbol)
        if not price:
            continue

        size = await calculate_size(capital, conf / 100)
        if size < TRADING["MIN_TRADE"]:
            continue

        quantity = size / price

        logger.info(
            f"TRADE: {symbol} | Score: {score:.0f} | ${size:.2f} @ ${price:.2f}"
        )

        await execute_buy(client, symbol, size)
        await place_limit(client, symbol, price, quantity)
        trades += 1

    return trades


async def run():
    logger.info("=" * 60)
    logger.info("IBIS FAST TRADING SYSTEM - CONTINUOUS")
    logger.info("=" * 60)

    client = await get_client()
    free_intel = await get_intel()

    try:
        while True:
            try:
                capital = await get_balance(client)
                logger.info(f"Capital: ${capital:.2f} | Scanning...")

                count = await scan_and_trade(client, free_intel)

                if count == 0:
                    logger.info("No trades this cycle")

                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Cycle error: {e}")
                await asyncio.sleep(10)

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(run())
