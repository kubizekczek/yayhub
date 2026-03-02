#!/bin/bash

###############################################################################
# YayHub Installer - Git Version
# Downloads the app from Git and installs it
###############################################################################

set -e  # Exit on error

# Configuration
REPO_URL="${1:-https://github.com/kubizekczek/yayhub.git}"
INSTALL_DIR="${HOME}/.local/opt/yayhub"

echo "╔════════════════════════════════════════╗"
echo "║      YayHub - Installer                 ║"
echo "║   (Package Manager for Arch)            ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Check if Git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed!"
    echo "   Install it: sudo pacman -S git"
    exit 1
fi

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed!"
    echo "   Install it: sudo pacman -S python"
    exit 1
fi

echo "📥 Downloading repository..."
if [ -d "$INSTALL_DIR" ]; then
    echo "⚠️  Directory $INSTALL_DIR already exists. Removing..."
    rm -rf "$INSTALL_DIR"
fi

git clone "$REPO_URL" "$INSTALL_DIR" || {
    echo "❌ Failed to clone repository!"
    echo "   Check if the URL is correct: $REPO_URL"
    exit 1
}

cd "$INSTALL_DIR"

echo ""
echo "📦 Creating Python virtual environment..."
python3 -m venv venv

echo "⬇️  Installing dependencies..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

echo ""
echo "🔧 Creating desktop launcher..."
mkdir -p ~/.local/share/applications

cat > ~/.local/share/applications/yayhub.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=YayHub
Comment=Package Manager GUI for Arch Linux
Exec=$INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/main.py
Icon=system-software-install
Categories=System;Utility;
Terminal=false
EOF

chmod +x ~/.local/share/applications/yayhub.desktop

echo ""
echo "✅ Installation complete!"
echo ""
echo "To run the app:"
echo "  • Search 'YayHub' in your app menu"
echo "  • Or in terminal: $INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/main.py"
echo ""
echo "📍 Install path: $INSTALL_DIR"
echo ""
