#!/bin/bash
# 🦅 IBIS TRUE TRADER - Quick Start Script

# Get project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if venv exists
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "⚠️ Virtual environment not found. Creating one..."
    python3 -m venv "$PROJECT_DIR/venv"
fi

# Activate venv and run
echo "🚀 Starting IBIS TRUE TRADER v1.0..."
source "$PROJECT_DIR/venv/bin/activate"
python3 "$PROJECT_DIR/ibis_true_agent.py"
