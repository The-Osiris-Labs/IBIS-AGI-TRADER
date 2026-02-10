#!/usr/bin/env python3
import asyncio
import json
import os
from ibis_true_agent import IBISTrueAgent


async def fix_state():
    agent = IBISTrueAgent()
    await agent.initialize()

    print("=== INITIAL STATE ===")
    print(json.dumps(agent.state["capital_awareness"], indent=2))

    # Force update capital awareness
    await agent.update_capital_awareness()

    print("\n=== AFTER UPDATE ===")
    print(json.dumps(agent.state["capital_awareness"], indent=2))

    # Save the state
    agent._save_state()
    print("\n✅ State file saved successfully")

    # Verify
    state_path = "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_true_state.json"
    if os.path.exists(state_path):
        with open(state_path, "r") as f:
            saved_state = json.load(f)
        print("\n=== VERIFIED SAVED STATE ===")
        print(json.dumps(saved_state["capital_awareness"], indent=2))


asyncio.run(fix_state())
