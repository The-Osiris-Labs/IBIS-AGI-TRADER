#!/usr/bin/env python3
"""
IBIS v2.0 - Live Trading Setup
Configure API keys for live trading
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def setup_live_trading():
    """Setup live trading with API keys."""

    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║     IBIS v2.0 - LIVE TRADING SETUP                                 ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
    """)

    env_path = Path(__file__).parent / "keys.env"

    if env_path.exists():
        print(f"\n✓ keys.env found: {env_path}")

        with open(env_path) as f:
            content = f.read()

        if "your_api_key_here" in content:
            print("\n⚠️  API keys not configured!")
            print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Go to: https://www.kucoin.com/account/api

2. Create API credentials:
   - Name: IBIS_TRADING
   - Permissions: Read, Trade, Transfer
   - IP Restriction: Optional
   - Passphrase: Remember this!

3. Edit keys.env:
   
   KUCOIN_API_KEY=your_api_key
   KUCOIN_API_SECRET=your_api_secret  
   KUCOIN_PASSPHRASE=your_passphrase
   PAPER_TRADING=false

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """)
            return False
        else:
            paper_trading = "true"
            for line in content.split("\n"):
                if line.startswith("PAPER_TRADING="):
                    paper_trading = line.split("=")[1].strip().lower()
                    break

            if paper_trading == "false":
                print("\n✅ LIVE TRADING ENABLED")
            else:
                print(f"\n⚠️  Paper trading: {paper_trading} (set to false for live)")

            return True
    else:
        print(f"\n⚠️  keys.env not found at: {env_path}")
        return False


def test_connection():
    """Test API connection."""
    print("\n" + "=" * 60)
    print("TESTING CONNECTION")
    print("=" * 60)

    try:
        from ibis.exchange import get_kucoin_client

        client = get_kucoin_client(paper_trading=False)

        if client is None:
            print("\n❌ Client initialization failed")
            return False

        print(f"\n  Exchange: {client}")
        print(f"  Sandbox: {client.sandbox}")
        print(f"  Paper: {client.paper_trading}")

        if not client.api_key:
            print("\n⚠️  API key not configured!")
            return False

        print(f"\n  API Key: {client.api_key[:8]}...")

        import asyncio

        async def test():
            try:
                balances = await asyncio.wait_for(client.get_all_balances(), timeout=10)
                if balances is not None:
                    print("\n✅ Connection successful!")
                    return True
            except Exception as e:
                print(f"\n❌ Connection failed: {e}")
            return False

        try:
            return asyncio.run(asyncio.wait_for(test(), timeout=12))
        except Exception as e:
            print(f"\n❌ Connection failed: {e}")
            return False

    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        return False


def enable_live_trading():
    """Enable live trading mode."""
    env_path = Path(__file__).parent / "keys.env"

    if not env_path.exists():
        print("keys.env not found.")
        return False

    with open(env_path) as f:
        content = f.read()

    lines = []
    for line in content.split("\n"):
        if line.startswith("PAPER_TRADING="):
            lines.append("PAPER_TRADING=false")
        else:
            lines.append(line)

    with open(env_path, "w") as f:
        f.write("\n".join(lines))

    print("\n✅ Live trading enabled!")
    print("   PAPER_TRADING=false")

    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="IBIS Live Trading Setup")
    parser.add_argument("--setup", action="store_true", help="Run setup")
    parser.add_argument("--test", action="store_true", help="Test connection")
    parser.add_argument("--enable", action="store_true", help="Enable live trading")
    parser.add_argument("--status", action="store_true", help="Show status")

    args = parser.parse_args()

    if args.setup:
        ok = setup_live_trading()
        sys.exit(0 if ok else 1)
    elif args.test:
        ok = test_connection()
        sys.exit(0 if ok else 1)
    elif args.enable:
        ok = enable_live_trading()
        sys.exit(0 if ok else 1)
    elif args.status:
        ok1 = setup_live_trading()
        ok2 = test_connection()
        sys.exit(0 if (ok1 and ok2) else 1)
    else:
        print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║     IBIS v2.0 - LIVE TRADING SETUP                                 ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝

Commands:
--------
  python3 setup_live.py --setup     Setup keys.env
  python3 setup_live.py --enable   Enable live trading
  python3 setup_live.py --test     Test API connection
  python3 setup_live.py --status   Show full status
        """)

        if setup_live_trading():
            test_connection()


if __name__ == "__main__":
    main()
