#!/bin/bash

# Quick Start Guide for Pacman GUI

cat << 'EOF'

╔════════════════════════════════════════════════════════════════════════╗
║           PACMAN GUI - QUICK START GUIDE                              ║
║     PyQt6 Frontend for pacman and yay on Arch Linux                   ║
╚════════════════════════════════════════════════════════════════════════╝

📋 WHAT'S INCLUDED
═══════════════════════════════════════════════════════════════════════

✓ Complete Python application (PyQt6-based)
✓ Support for official repos: core, extra, multilib
✓ Support for AUR (if yay is installed)
✓ Live search with real-time filtering
✓ Package caching (JSON-based)
✓ Install/Remove functionality
✓ Wayland + X11 compatible
✓ Beautiful UI with dark theme

📦 PREREQUISITES
═══════════════════════════════════════════════════════════════════════

Required:
  ✓ Arch Linux (or derivative)
  ✓ Python 3.8+
  ✓ pacman (default on Arch)

Optional:
  • yay (for AUR support)
  • polkit (for pkexec - usually pre-installed)

⚡ INSTALLATION (3 EASY STEPS)
═══════════════════════════════════════════════════════════════════════

Step 1: Install Python dependencies
─────────────────────────────────────
  $ pip install --user -r requirements.txt

Or use the automated script:
  $ chmod +x install.sh
  $ ./install.sh


Step 2: (Optional) Install yay for AUR support
──────────────────────────────────────────────
  $ git clone https://aur.archlinux.org/yay.git
  $ cd yay
  $ makepkg -si


Step 3: Run the application
────────────────────────────
  $ python3 main.py

🎯 USAGE
═══════════════════════════════════════════════════════════════════════

1. Search: Type package name or description in the search box
2. Filter: Choose between "All", "Installed", "Not Installed"
3. Sort: Order by "Name" or "Repository"
4. Refresh: Click "Refresh" to update the package list
5. Install: Select a package and click "Install"
6. Remove: Click "Remove" to uninstall a package

💾 FILE STRUCTURE
═══════════════════════════════════════════════════════════════════════

aplikacja/
├── main.py                    ← Main entry point (run this!)
├── requirements.txt           ← Python dependencies
├── install.sh                 ← Automated installation script
├── test.sh                    ← Test script
├── build_appimage.sh          ← Build portable AppImage
├── README.md                  ← Full documentation
├── QUICKSTART.md              ← This file
└── pacman_gui/
    ├── utils/
    │   ├── package_manager.py ← Pacman/yay wrapper
    │   └── cache_manager.py   ← Caching system
    └── ui/
        ├── main_window.py     ← Main application window
        ├── search_widget.py   ← Search box
        ├── package_list_widget.py  ← Package table
        └── package_details_widget.py ← Package details pane


🔧 TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════

Issue: "PyQt6 not found"
  → Run: pip install --user PyQt6

Issue: "yay not found - AUR support disabled"
  → This is OK. You can install yay later if needed.
  → Or install it now: git clone https://aur.archlinux.org/yay.git

Issue: "Permission denied" when installing packages
  → Make sure polkit is installed: sudo pacman -S polkit
  → Application uses pkexec (safer than sudo)

Issue: Application won't run
  → Check Python version: python3 --version (need 3.8+)
  → Test modules: cd aplikacja && python3 test.sh
  → Check if PyQt6 is really installed: python3 -c "import PyQt6"

Issue: Cache is outdated
  → Click "Refresh" button in the application
  → Or delete cache manually: rm ~/.cache/pacman-gui/packages.json

📚 DOCUMENTATION
═══════════════════════════════════════════════════════════════════════

For detailed documentation, see README.md in the application directory.

🚀 ADVANCED USAGE
═══════════════════════════════════════════════════════════════════════

Build AppImage (portable executable):
  $ chmod +x build_appimage.sh
  $ ./build_appimage.sh
  
  Then run:
  $ ./pacman-gui-x86_64.AppImage

Create desktop shortcut (for Plasma/GNOME):
  $ ./install.sh  (choose "Yes" when prompted)

💡 QUICK TIPS
═══════════════════════════════════════════════════════════════════════

• The app caches package list for 1 hour
• Search is case-insensitive and searches both name and description
• Installed packages appear in bold in the list
• AUR packages have blue background
• Click on any package to see full details
• Installation/removal requires your password (via polkit)

═══════════════════════════════════════════════════════════════════════

Ready to use! Run: python3 main.py

═══════════════════════════════════════════════════════════════════════

EOF
