# YayHub

A GUI package manager for Arch Linux (pacman + yay).

---

## Install on any Arch Linux machine

Open a terminal and paste this one command:

```bash
bash <(curl -sL https://raw.githubusercontent.com/kubizekczek/yayhub/main/install.sh)
```

Done. The app installs itself and appears in your app menu.

---

## What it does

- Install / remove packages from pacman repos
- Install / remove AUR packages via yay
- App Store with 300+ curated apps in categories
- Manage systemd services (start, stop, enable, disable)
- Detect broken packages and missing files
- Check for updates
- Dark theme, fast search, clean UI

---

## Requirements

- Arch Linux (or any Arch-based distro like CachyOS, EndeavourOS, Manjaro)
- `git` and `python3` (the installer checks for these)
- `yay` (optional, for AUR support)

If you don't have yay:

```bash
sudo pacman -S --needed git base-devel
git clone https://aur.archlinux.org/yay.git
cd yay
makepkg -si
```

---

## Run manually (if already cloned)

```bash
cd yayhub
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python3 main.py
```

---

## Author

**kubizz** — [github.com/kubizekczek](https://github.com/kubizekczek)

## License

MIT
