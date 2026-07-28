#!/bin/bash
# Demo-safe DSTerminal launcher

# Activate the venv
source "$(dirname "$0")/venv/bin/activate"

# Info banner
echo "Launching DSTerminal in demo mode..."
echo "Python: $(python --version)"
echo "Using virtual environment: $(pwd)/venv"

# Run DSTerminal demo
python dsterminal.py --demo
