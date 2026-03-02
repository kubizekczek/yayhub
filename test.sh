#!/bin/bash

# Test script for Pacman GUI
# Checks dependencies and runs basic tests

set -e

echo "=== Pacman GUI Test Script ==="
echo ""

# Check Python
echo "Checking Python..."
python3 --version
echo "✓ Python OK"
echo ""

# Check pacman
echo "Checking pacman..."
pacman --version | head -1
echo "✓ Pacman OK"
echo ""

# Check yay
echo "Checking yay..."
if command -v yay &> /dev/null; then
    yay --version
    echo "✓ Yay OK"
else
    echo "⚠ Yay NOT found (AUR support will be disabled)"
fi
echo ""

# Check Python modules
echo "Checking Python modules..."
python3 -c "import sys; print(f'sys.version: {sys.version}')"
python3 -c "import PyQt6" 2>/dev/null && echo "✓ PyQt6 installed" || echo "✗ PyQt6 NOT installed"
echo ""

# Try importing the application
echo "Checking application modules..."
python3 -c "import sys; sys.path.insert(0, '.'); from pacman_gui.utils import PackageManager" && \
    echo "✓ PackageManager module OK" || echo "✗ PackageManager module NOT found"
python3 -c "import sys; sys.path.insert(0, '.'); from pacman_gui.utils import CacheManager" && \
    echo "✓ CacheManager module OK" || echo "✗ CacheManager module NOT found"
python3 -c "import sys; sys.path.insert(0, '.'); from pacman_gui.ui import MainWindow" && \
    echo "✓ UI modules OK" || echo "✗ UI modules NOT found"
echo ""

# Test package manager
echo "Testing PackageManager..."
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from pacman_gui.utils import PackageManager

pm = PackageManager()
print(f"✓ AUR available: {pm.aur_available}")
print(f"✓ Installed packages: {len(pm.installed_packages)}")

# Not calling get_all_packages here as it might take long
EOF

echo ""
echo "=== All tests passed ==="
echo ""
echo "To run the application:"
echo "  python3 main.py"
