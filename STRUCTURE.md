# Project Structure - Pacman GUI

## Directory Layout

```
aplikacja/
├── 📄 main.py                      # Application entry point (MAIN SCRIPT)
├── 📄 requirements.txt             # Python dependencies (PyQt6)
├── 📄 .gitignore                   # Git ignore patterns
├── 📄 Makefile                     # Build commands (make run, make install)
│
├── 🔨 Installation & Deployment
│   ├── 📄 install.sh              # Automated installation script
│   ├── 📄 start.sh                # Quick start script
│   ├── 📄 test.sh                 # Test suite
│   └── 📄 build_appimage.sh       # AppImage builder
│
├── 📚 Documentation
│   ├── 📄 README.md               # Full documentation
│   ├── 📄 QUICKSTART.md           # Quick start guide
│   └── 📄 STRUCTURE.md            # This file
│
└── 📦 Application Code (pacman_gui/)
    ├── 📄 __init__.py             # Package initialization
    │
    ├── 🛠️ utils/                  # Backend & system integration
    │   ├── 📄 __init__.py
    │   ├── 📄 package_manager.py  # Pacman/yay wrapper
    │   └── 📄 cache_manager.py    # Package list caching
    │
    └── 🎨 ui/                     # User interface (PyQt6)
        ├── 📄 __init__.py
        ├── 📄 main_window.py      # Main application window
        ├── 📄 search_widget.py    # Search input widget
        ├── 📄 package_list_widget.py       # Package list table
        └── 📄 package_details_widget.py    # Details pane
```

## File Descriptions

### Root Level Files

| File | Purpose |
|------|---------|
| `main.py` | **Application entry point**. Run this to start the app: `python3 main.py` |
| `requirements.txt` | Python package dependencies (only PyQt6) |
| `.gitignore` | Git configuration for version control |
| `Makefile` | Build automation (make install, make run, etc.) |

### Scripts

| Script | Purpose |
|--------|---------|
| `install.sh` | Automates setup: checks deps, installs Python packages, creates desktop entry |
| `start.sh` | Quick launcher with dependency checking |
| `test.sh` | Validates installation and runs basic tests |
| `build_appimage.sh` | Builds portable AppImage executable |

### Documentation

| File | Content |
|------|---------|
| `README.md` | Complete documentation with features, usage, and troubleshooting |
| `QUICKSTART.md` | Quick start guide for new users |
| `STRUCTURE.md` | Project structure overview (this file) |

### Backend (pacman_gui/utils/)

#### `package_manager.py`
Core wrapper around system commands:
- **Classes**:
  - `Package` - Data class for package info
  - `Repository` - Enum for repo types  
  - `PackageManager` - Main class with methods:
    - `get_official_packages()` - Fetch from pacman
    - `get_aur_packages()` - Fetch from yay
    - `get_all_packages()` - Combined list
    - `install_package()` - Install via pkexec
    - `remove_package()` - Remove via pkexec
    - `is_installed()` - Check if installed
    - `refresh_installed_packages()` - Update cache
    - `get_package_info()` - Detailed info

#### `cache_manager.py`
Handles package list caching:
- **Class**: `CacheManager`
  - `save_packages()` - Save to JSON cache
  - `load_packages()` - Load from cache
  - `is_cache_valid()` - Check if cache expired
  - `clear_cache()` - Delete cache file
  - `get_cache_age()` - Get age in seconds
  - `get_cache_package_count()` - Count packages

### Frontend (pacman_gui/ui/)

#### `main_window.py`
Main application window:
- **Classes**:
  - `PackageLoaderThread` - Async package loading
  - `MainWindow` - Main QMainWindow
- **Features**:
  - Search bar with live filtering
  - Filter dropdown (All/Installed/Not Installed)
  - Sort dropdown (Name/Repository)
  - Refresh button
  - Split view: list + details

#### `search_widget.py`
Search input widget:
- **Class**: `SearchWidget`
- **Signals**: `search_changed(str)`
- **Features**:
  - Real-time search input
  - Clear button
  - Placeholder text

#### `package_list_widget.py`
Package list display:
- **Class**: `PackageListWidget`
- **Signals**: `package_selected(Package)`
- **Features**:
  - Table with columns: Name, Repo, Version, Description, Status
  - Color coding (AUR=blue, Installed=green)
  - Bold text for installed packages
  - Single selection mode

#### `package_details_widget.py`
Package details pane:
- **Class**: `PackageDetailsWidget`
- **Signals**: 
  - `install_clicked(Package)`
  - `remove_clicked(Package)`
- **Features**:
  - Package name, repo, version display
  - Description and details text areas
  - Installation log output
  - Install/Remove buttons with conditional enabling
  - Scroll area for large content

## Module Dependencies

```
Imports Structure:
main.py
  ├── pacman_gui.ui.MainWindow
  │   ├── pacman_gui.utils.PackageManager
  │   ├── pacman_gui.utils.CacheManager
  │   ├── pacman_gui.ui.SearchWidget
  │   ├── pacman_gui.ui.PackageListWidget
  │   └── pacman_gui.ui.PackageDetailsWidget
  │
  └── PyQt6.QtWidgets
  └── PyQt6.QtCore
  └── PyQt6.QtGui

Standard Python modules used:
  - subprocess (system commands)
  - json (cache storage)
  - logging (debug output)
  - pathlib (file handling)
  - dataclasses (Package data)
  - enum (Repository enum)
  - typing (type hints)
  - datetime (timestamps)
```

## Code Quality

All files:
- ✅ Have correct Python syntax (validated with py_compile)
- ✅ Use type hints for better readability
- ✅ Include docstrings for classes and methods
- ✅ Follow PEP 8 style guidelines
- ✅ Have proper error handling
- ✅ Use logging for debugging

## System Integration

System commands used:
- `which yay` - Check if yay is installed
- `pacman -Q` - List installed packages
- `pacman -Sl` - List official packages
- `yay -Sl` - List AUR packages
- `pacman -Qi` - Get package details
- `pkexec pacman -S` - Install packages (with privilege escalation)
- `pkexec pacman -R` - Remove packages (with privilege escalation)
- `pkexec yay -S` - Install AUR packages

## Configuration

Cache location: `~/.cache/pacman-gui/packages.json`
Cache timeout: 3600 seconds (1 hour)

Can be modified in `pacman_gui/utils/cache_manager.py`:
```python
CACHE_DIR = Path.home() / '.cache' / 'pacman-gui'
CACHE_FILE = CACHE_DIR / 'packages.json'
CACHE_TIMEOUT = 3600
```

## Building & Distribution

### Development
```bash
python3 main.py
```

### Installation
```bash
./install.sh
```

### Testing
```bash
bash test.sh
```

### AppImage Build
```bash
bash build_appimage.sh
```
Creates: `pacman-gui-x86_64.AppImage`

## Future Enhancements

Potential additions:
- [ ] Progress bar during installation
- [ ] Installation history
- [ ] Package statistics
- [ ] Package dependencies graph
- [ ] Batch operations
- [ ] Update checker
- [ ] Custom themes
- [ ] Terminal output window
