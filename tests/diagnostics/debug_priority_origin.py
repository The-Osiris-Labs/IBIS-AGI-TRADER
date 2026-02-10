#!/usr/bin/env python3
"""
Debug where priority symbols are coming from
"""

import sys

sys.path.insert(0, "/root/projects/Dont enter unless solicited/AGI Trader")
import inspect
import asyncio
from ibis_true_agent import IBISTrueAgent


async def debug_priority_origin():
    agent = IBISTrueAgent()
    await agent.initialize()

    print("🔍 DEBUG PRIORITY SYMBOLS ORIGIN")
    print("=" * 50)

    # Get the source code of analyze_market_intelligence
    source = inspect.getsource(agent.analyze_market_intelligence)
    print("📄 analyze_market_intelligence source:")
    print(source)
    print("-" * 50)

    # Find where priority_symbols is being defined or modified
    print("🧐 Finding priority_symbols usage in method:")
    for i, line in enumerate(source.split("\n")):
        if "priority_symbols" in line:
            print(f"Line {i + 1}: {line.strip()}")

    print("=" * 50)

    # Call the method to see what happens
    print("🎯 Calling analyze_market_intelligence():")

    # Run with debug printing
    from io import StringIO
    import contextlib

    @contextlib.contextmanager
    def capture_stdout():
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            yield sys.stdout
        finally:
            sys.stdout = old_stdout

    with capture_stdout() as buf:
        await agent.analyze_market_intelligence()

    output = buf.getvalue()
    print(output)

    print("✅ Analysis complete")


asyncio.run(debug_priority_origin())
