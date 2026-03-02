#!/bin/bash

# Build AppImage for Pacman GUI
# This script creates a portable AppImage bundle

set -e

echo "=== Building Pacman GUI AppImage ==="

# Check if we have the necessary tools
if ! command -v appimagetool &> /dev/null; then
    echo "Error: appimagetool is required"
    echo "Install it with: yay -S appimagetool"
    exit 1
fi

# Create build directory
BUILD_DIR="build/appimage"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/AppDir"

# Copy application files
echo "Copying application files..."
cp -r pacman_gui "$BUILD_DIR/AppDir/"
cp main.py "$BUILD_DIR/AppDir/"
cp requirements.txt "$BUILD_DIR/AppDir/"

# Create AppRun script
echo "Creating AppRun script..."
cat > "$BUILD_DIR/AppDir/AppRun" << 'EOF'
#!/bin/bash
APPDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$APPDIR"
python3 main.py "$@"
EOF

chmod +x "$BUILD_DIR/AppDir/AppRun"

# Create desktop entry
echo "Creating desktop entry..."
cat > "$BUILD_DIR/AppDir/pacman-gui.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Pacman GUI
Comment=GUI frontend for pacman and yay
Exec=AppRun
Icon=system-software-install
Categories=System;Utility;
StartupNotify=true
Terminal=false
EOF

# Create metadata
echo "Creating metadata..."
mkdir -p "$BUILD_DIR/AppDir/usr/share/metainfo"
cat > "$BUILD_DIR/AppDir/usr/share/metainfo/pacman-gui.appdata.xml" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>pacman-gui</id>
  <name>Pacman GUI</name>
  <summary>GUI frontend for pacman and yay</summary>
  <description>
    <p>A PyQt6-based graphical frontend for the Arch Linux package manager (pacman) and AUR helper (yay).</p>
  </description>
  <url type="homepage">https://github.com/example/pacman-gui</url>
  <metadata_license>MIT</metadata_license>
  <project_license>MIT</project_license>
  <developer_name>Community</developer_name>
  <releases>
    <release version="1.0.0" date="2024-01-01"/>
  </releases>
</component>
EOF

# Build AppImage
echo "Building AppImage..."
appimagetool "$BUILD_DIR/AppDir" "pacman-gui-x86_64.AppImage"

# Make executable
chmod +x pacman-gui-x86_64.AppImage

echo ""
echo "=== Build completed ==="
echo "AppImage created: pacman-gui-x86_64.AppImage"
echo ""
echo "To run:"
echo "  ./pacman-gui-x86_64.AppImage"
