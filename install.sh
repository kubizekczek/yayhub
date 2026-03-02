#!/bin/bash

###############################################################################
# YayHub Installer - Git Version
# Pobiera aplikację z Git i instaluje ją
###############################################################################

set -e  # Exit on error

# Konfiguracja
REPO_URL="${1:-https://github.com/yourusername/yayhub}"
INSTALL_DIR="${HOME}/.local/opt/yayhub"

echo "╔════════════════════════════════════════╗"
echo "║      YayHub - Instalator                ║"
echo "║   (Package Manager dla Arch)            ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Sprawdzenie czy Git jest zainstalowany
if ! command -v git &> /dev/null; then
    echo "❌ Git nie jest zainstalowany!"
    echo "   Zainstaluj: sudo pacman -S git"
    exit 1
fi

# Sprawdzenie czy Python3 jest zainstalowany
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 nie jest zainstalowany!"
    echo "   Zainstaluj: sudo pacman -S python"
    exit 1
fi

echo "📥 Pobieranie repozytorium..."
if [ -d "$INSTALL_DIR" ]; then
    echo "⚠️  Katalog $INSTALL_DIR już istnieje. Usuwanie..."
    rm -rf "$INSTALL_DIR"
fi

git clone "$REPO_URL" "$INSTALL_DIR" || {
    echo "❌ Nie udało się sklonować repozytorium!"
    echo "   Sprawdź czy URL jest poprawny: $REPO_URL"
    exit 1
}

cd "$INSTALL_DIR"

echo ""
echo "📦 Tworzenie wirtualnego środowiska Pythona..."
python3 -m venv venv

echo "⬇️  Instalowanie zależności..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

echo ""
echo "🔧 Tworzenie desktop launcher'a..."
mkdir -p ~/.local/share/applications

cat > ~/.local/share/applications/yayhub.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=YayHub
Comment=Package Manager GUI dla Arch Linuxa
Exec=$INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/main.py
Icon=system-software-install
Categories=System;Utility;
Terminal=false
EOF

chmod +x ~/.local/share/applications/yayhub.desktop

echo ""
echo "✅ Instalacja zakończona!"
echo ""
echo "Aby uruchomić aplikację:"
echo "  • Szukaj 'YayHub' w menu aplikacji"
echo "  • Lub w terminalu: $INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/main.py"
echo ""
echo "📍 Ścieżka instalacji: $INSTALL_DIR"
echo ""
