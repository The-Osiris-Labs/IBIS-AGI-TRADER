#!/usr/bin/env python3
"""Apply learning suggestions to config (best-effort)."""

from pathlib import Path
import json
import sys

CONFIG_PATH = Path("agi_trader_config.json")
SUGGESTIONS_PATH = Path("data/learning_suggestions_long.json")


def main() -> int:
    if not CONFIG_PATH.exists():
        print("Config not found")
        return 1
    if not SUGGESTIONS_PATH.exists():
        print("Learning suggestions not found")
        return 1

    config = json.loads(CONFIG_PATH.read_text())
    data = json.loads(SUGGESTIONS_PATH.read_text())
    suggestions = data.get("suggestions", {})

    changed = False
    note = []

    if suggestions.get("min_score"):
        # Simple parser: "Increase min_score by +0.05" or decrease
        text = suggestions["min_score"]
        if "Increase" in text:
            config["trading"]["min_score"] = round(config["trading"]["min_score"] + 0.05, 4)
            changed = True
            note.append("min_score +0.05")
        elif "Decrease" in text:
            config["trading"]["min_score"] = max(0.0, round(config["trading"]["min_score"] - 0.02, 4))
            changed = True
            note.append("min_score -0.02")

    if suggestions.get("kelly_fraction"):
        text = suggestions["kelly_fraction"]
        if "Reduce" in text:
            config["trading"]["kelly_fraction"] = max(0.0, round(config["trading"]["kelly_fraction"] - 0.05, 4))
            changed = True
            note.append("kelly_fraction -0.05")
        elif "Increase" in text:
            config["trading"]["kelly_fraction"] = round(config["trading"]["kelly_fraction"] + 0.03, 4)
            changed = True
            note.append("kelly_fraction +0.03")

    if changed:
        CONFIG_PATH.write_text(json.dumps(config, indent=2))
        print("Applied learning suggestions:", ", ".join(note))
    else:
        print("No applicable learning changes")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
