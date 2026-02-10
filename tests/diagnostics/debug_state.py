#!/usr/bin/env python3
import asyncio
import json
import os
from ibis_true_agent import IBISTrueAgent


async def debug_state():
    agent = IBISTrueAgent()

    # Debug: Check if state file exists and contains data
    state_path = "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_true_state.json"
    if os.path.exists(state_path):
        with open(state_path, "r") as f:
            saved_state = json.load(f)
        print("=== STATE FILE CONTENTS ===")
        print(json.dumps(saved_state, indent=2))

        print("\n=== CAPITAL AWARENESS FROM FILE ===")
        if "capital_awareness" in saved_state:
            print(json.dumps(saved_state["capital_awareness"], indent=2))
        else:
            print("❌ No capital_awareness in state file")
    else:
        print("❌ State file does not exist")

    # Initialize agent and check
    await agent.initialize()

    print("\n=== AGENT STATE AFTER INITIALIZATION ===")
    print(json.dumps(agent.state, indent=2))

    print("\n=== CAPITAL AWARENESS IN AGENT ===")
    print(json.dumps(agent.state["capital_awareness"], indent=2))


asyncio.run(debug_state())
