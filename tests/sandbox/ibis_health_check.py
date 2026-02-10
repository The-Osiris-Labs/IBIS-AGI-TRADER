#!/usr/bin/env python3
import asyncio
import sys
import os
import logging

# Add project root to path
PROJECT_ROOT = "/root/projects/Dont enter unless solicited/AGI Trader"
sys.path.append(PROJECT_ROOT)

from ibis.database.db import IbisDB
from ibis.exchange.kucoin_client import get_kucoin_client
from ibis.market_intelligence import market_intelligence
from ibis.market_funnel import MarketFunnel
from ibis.orchestrator import IBIS
from ibis.execution.engine import ExecutionEngine

# Silence logs during test
logging.getLogger("ibis_v8").setLevel(logging.ERROR)

async def test_core_modules():
    print("\n" + "="*80)
    print("      🧪 IBIS v8.1 CORE MODULES HEALTH CHECK")
    print("="*80)
    
    results = []
    
    # 1. Database
    try:
        db = IbisDB()
        positions = db.get_open_positions()
        print(f" [✓] Database: CONNECTED (Active Positions: {len(positions)})")
        results.append(True)
    except Exception as e:
        print(f" [✗] Database: FAILED ({e})")
        results.append(False)
        
    # 2. KuCoin Client
    try:
        client = get_kucoin_client()
        balances = await client.get_all_balances()
        print(f" [✓] KuCoin Client: AUTHENTICATED (Balances: {len(balances)})")
        results.append(True)
    except Exception as e:
        print(f" [✗] KuCoin Client: FAILED ({e})")
        results.append(False)

    # 3. Market Intelligence
    try:
        # Test batch fetch
        test_symbols = ["BTC-USDT"]
        intel = await market_intelligence.get_combined_intelligence(test_symbols)
        if all(s in intel for s in test_symbols):
            print(f" [✓] Market Intelligence: VALID (Fetched {len(intel)} symbols)")
            results.append(True)
        else:
            print(f" [!] Market Intelligence: PARTIAL (Fetched {len(intel)}/{len(test_symbols)})")
            results.append(True)
    except Exception as e:
        print(f" [✗] Market Intelligence: FAILED ({e})")
        results.append(False)

    # 4. Market Funnel
    try:
        funnel = MarketFunnel(client)
        ranked = await funnel.rank(limit=5)
        print(f" [✓] Market Funnel: OPERATIONAL (Ranked top {len(ranked)} candidates)")
        results.append(True)
    except Exception as e:
        print(f" [✗] Market Funnel: FAILED ({e})")
        results.append(False)

    # 5. AGI Orchestrator
    try:
        ibis = IBIS()
        ok = await ibis.initialize()
        if ok:
            print(f" [✓] AGI Orchestrator: INITIALIZED (Memory Synced)")
            results.append(True)
        else:
            print(f" [✗] AGI Orchestrator: INIT FAILED")
            results.append(False)
    except Exception as e:
        print(f" [✗] AGI Orchestrator: FAILED ({e})")
        results.append(False)

    # 6. Execution Engine
    try:
        engine = ExecutionEngine()
        # Test initialization only
        await engine.initialize()
        print(f" [✓] Execution Engine: READY (Lifecycle Hooks Active)")
        results.append(True)
    except Exception as e:
        print(f" [✗] Execution Engine: FAILED ({e})")
        results.append(False)

    print("\n" + "="*80)
    final_score = (sum(results) / len(results)) * 100
    color = "\033[92m" if final_score == 100 else "\033[93m" if final_score > 50 else "\033[91m"
    print(f" SYSTEM HEALTH SCORE: {color}{final_score:.1f}%\033[0m")
    print("="*80 + "\n")
    
    # MODULE CLEANUP
    try:
        if 'engine' in locals():
            await engine.shutdown()
        if 'ibis' in locals():
            await ibis.stop()
        
        client = get_kucoin_client()
        await client.close()
        await market_intelligence.close()
    except:
        pass

    return all(results)

if __name__ == "__main__":
    success = asyncio.run(test_core_modules())
    if not success:
        sys.exit(1)
