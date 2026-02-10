#!/usr/bin/env python3
import sys

sys.path.insert(0, "/root/projects/Dont enter unless solicited/AGI Trader/ibis")

from ibis import IBIS, IBISConfig
import asyncio


async def test():
    ibis = IBIS(IBISConfig())
    await ibis.initialize()
    print("IBIS initialized successfully!")
    await ibis.stop()
    print("IBIS stopped.")


if __name__ == "__main__":
    asyncio.run(test())
