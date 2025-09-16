#!/bin/bash
# HamppServer Command Script
# Author: Md Habibur Rahman
# Just run: ./hampp.sh or bash hampp.sh

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to script directory
cd "$SCRIPT_DIR"

# Check if Python is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Error: Python is not installed."
    echo ""
    echo "Please install Python first:"
    echo "  - On Termux: pkg install python"
    echo "  - On Ubuntu: sudo apt install python3"
    echo ""
    exit 1
fi

# Set PYTHONPATH to include the current directory
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Run HamppServer with all arguments passed through
# If no arguments, it will start interactive mode automatically
exec $PYTHON_CMD hampp.py "$@"
