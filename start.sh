#!/bin/bash

# Quick start script for Pacman GUI
# This script checks dependencies and runs the application

set -e

echo "🚀 Starting Pacman GUI..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Are you in the right directory?"
    exit 1
fi

# Check if PyQt6 is installed
echo "Checking dependencies..."
if ! python3 -c "import PyQt6" 2>/dev/null; then
    echo "❌ PyQt6 is not installed."
    echo ""
    echo "Install it with:"
    echo "  pip install --user PyQt6"
    echo ""
    echo "Or run the install script:"
    echo "  ./install.sh"
    exit 1
fi

echo "✓ All dependencies found"
echo ""

# Run the application
echo "Starting application..."
python3 main.py "$@"
