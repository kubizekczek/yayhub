#!/bin/bash

# Launcher script for YayHub
# This script launches the application with elevated privileges using pkexec

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Use pkexec to run python with venv and main.py
# The app's main.py will handle the privilege check
exec pkexec "$SCRIPT_DIR/venv/bin/python3" "$SCRIPT_DIR/main.py" "$@"
