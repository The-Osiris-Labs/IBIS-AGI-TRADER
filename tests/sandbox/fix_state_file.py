#!/usr/bin/env python3
import asyncio
import json
import os
from ibis_true_agent import IBISTrueAgent


async def fix_state_file():
    agent = IBISTrueAgent()
    await agent.initialize()

    # Get real capital awareness
    await agent.update_capital_awareness()
    real_capital = agent.state["capital_awareness"]

    print("=== REAL CAPITAL FROM EXCHANGE ===")
    print(json.dumps(real_capital, indent=2))

    # Load current state file
    state_path = "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_true_state.json"
    if os.path.exists(state_path):
        with open(state_path, "r") as f:
            state = json.load(f)
    else:
        state = {}

    # Update with real capital
    state["capital_awareness"] = real_capital
    state["updated"] = asyncio.get_event_loop().time()  # Update timestamp

    # Save the fixed state
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2, default=str)

    print("\n✅ State file fixed successfully")

    # Verify
    with open(state_path, "r") as f:
        fixed_state = json.load(f)
    print("\n=== FIXED STATE FILE ===")
    print(json.dumps(fixed_state["capital_awareness"], indent=2))


asyncio.run(fix_state_file())
