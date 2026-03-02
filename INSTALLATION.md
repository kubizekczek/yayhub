# YayHub - Installation Guide

Quick and easy installation from Git.

## Requirements

- **Arch Linux** or derivatives (Manjaro, EndeavourOS, CachyOS, etc.)
- **Python 3.8+**
- **Git**

## Quick Install (1 command)

```bash
bash <(curl -sL https://github.com/kubizekczek/yayhub/raw/main/install.sh)
```

Or if you have the `install.sh` file locally:

```bash
chmod +x install.sh
./install.sh
```

## Step by step

### 1. Download the repository
```bash
git clone https://github.com/kubizekczek/yayhub.git
cd yayhub
```

### 2. Run the installer
```bash
chmod +x install.sh
./install.sh
```

The script will automatically:
- ✅ Check required dependencies (Python, Git)
- ✅ Clone the repository to `~/.local/opt/yayhub`
- ✅ Create a Python virtual environment
- ✅ Install all dependencies
- ✅ Create a launcher in the app menu

### 3. Run the app

**Method 1 - App menu:**
- Open app menu
- Search "YayHub"
- Click to launch

**Method 2 - Command line:**
```bash
~/.local/opt/yayhub/venv/bin/python3 ~/.local/opt/yayhub/main.py
```

## Install paths

- **Install directory:** `~/.local/opt/yayhub`
- **App launcher:** `~/.local/share/applications/yayhub.desktop`
- **Python venv:** `~/.local/opt/yayhub/venv`

## Uninstall

```bash
rm -rf ~/.local/opt/yayhub
rm ~/.local/share/applications/yayhub.desktop
```

## Troubleshooting

### "Git is not installed!"
```bash
sudo pacman -S git
```

### "Python3 is not installed!"
```bash
sudo pacman -S python
```

### App won't start
Try running manually to see the error:
```bash
~/.local/opt/yayhub/venv/bin/python3 ~/.local/opt/yayhub/main.py
```

### Update to the latest version
```bash
cd ~/.local/opt/yayhub
git pull origin main
./venv/bin/pip install -r requirements.txt
```

## Support

If you have issues, open an issue on GitHub: https://github.com/kubizekczek/yayhub/issues

---

**Version:** 1.0  
**Author:** kubizz
