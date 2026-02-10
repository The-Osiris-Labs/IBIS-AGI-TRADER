#!/usr/bin/env python3
"""Lightweight KuCoin API connectivity check (no trading)."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def main() -> int:
    try:
        from ibis.exchange import get_kucoin_client

        client = get_kucoin_client(paper_trading=False)
        if not client.api_key:
            print("❌ API key not configured")
            return 1

        async def test():
            try:
                # Fast public check first
                ticker = await asyncio.wait_for(client.get_ticker("BTC-USDT"), timeout=5)
                if ticker and ticker.price:
                    print("✅ Public endpoint reachable")

                # Private check (requires keys)
                balances = await asyncio.wait_for(client.get_all_balances(), timeout=8)
                if balances is not None:
                    print("✅ Private endpoint reachable")
                    return 0
                print("❌ No balances returned")
                return 1
            except Exception as e:
                print(f"❌ Connection failed: {e}")
                return 1
            finally:
                try:
                    await asyncio.wait_for(client.close(), timeout=3)
                except Exception:
                    pass

        return asyncio.run(asyncio.wait_for(test(), timeout=15))
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
