"""
YayHub — App Store / Curated Applications Grid
Beautiful card-based view for popular applications.
"""

import logging
import subprocess
from typing import List, Dict, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGridLayout, QFrame, QLineEdit, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QFont, QFontDatabase, QColor, QIcon

from .progress_dialog import InstallProgressDialog

logger = logging.getLogger(__name__)

# ── Curated application catalog ───────────────────────────────────
# Each entry: (name, package_name, source, emoji, category, description)
# source: "pacman" or "yay" (AUR)

APP_CATALOG = [
    # ── Komunikatory ──
    ("Discord",         "discord",              "pacman",  "💬",  "Komunikatory",    "Komunikator głosowy i tekstowy dla graczy"),
    ("Telegram",        "telegram-desktop",     "pacman",  "✈️",  "Komunikatory",    "Szybki i bezpieczny komunikator"),
    ("Signal",          "signal-desktop",       "yay",     "🔒",  "Komunikatory",    "Prywatny komunikator z szyfrowaniem E2E"),
    ("Element",         "element-desktop",      "pacman",  "🟢",  "Komunikatory",    "Klient Matrix — zdecentralizowany czat"),
    ("Slack",           "slack-desktop",        "yay",     "💼",  "Komunikatory",    "Komunikator dla zespołów"),
    ("Teams",           "teams-for-linux",      "yay",     "👥",  "Komunikatory",    "Microsoft Teams dla Linux"),
    ("Vesktop",         "vesktop-bin",          "yay",     "🎧",  "Komunikatory",    "Discord z Vencord — lepsza wersja"),
    ("WhatsApp",        "whatsapp-for-linux",   "yay",     "📱",  "Komunikatory",    "WhatsApp na desktopie Linux"),
    ("Revolt",          "revolt-desktop",       "yay",     "🔴",  "Komunikatory",    "Open-source alternatywa Discorda"),
    ("Mumble",          "mumble",               "pacman",  "🎙️",  "Komunikatory",    "Czat głosowy o niskim opóźnieniu"),
    ("Pidgin",          "pidgin",               "pacman",  "🐦",  "Komunikatory",    "Wieloprotokołowy komunikator"),
    ("Hexchat",         "hexchat",              "pacman",  "💬",  "Komunikatory",    "Klient IRC"),
    ("Thunderbird",     "thunderbird",          "pacman",  "📧",  "Komunikatory",    "Klient e-mail od Mozilli"),
    ("Skype",           "skypeforlinux-bin",    "yay",     "📞",  "Komunikatory",    "Wideorozmowy i komunikator"),
    ("Zoom",            "zoom",                 "yay",     "📹",  "Komunikatory",    "Wideokonferencje Zoom"),
    ("Jitsi Meet",      "jitsi-meet-desktop-bin","yay",    "🤝",  "Komunikatory",    "Otwarte wideokonferencje"),
    ("Wire",            "wire-desktop",         "yay",     "🔗",  "Komunikatory",    "Bezpieczny komunikator biznesowy"),
    ("Keybase",         "keybase-gui",          "yay",     "🔑",  "Komunikatory",    "Szyfrowany czat + pliki"),

    # ── Przeglądarki ──
    ("Firefox",         "firefox",              "pacman",  "🦊",  "Przeglądarki",    "Szybka przeglądarka od Mozilli"),
    ("Chromium",        "chromium",             "pacman",  "🌐",  "Przeglądarki",    "Otwarta przeglądarka od Google"),
    ("Brave",           "brave-bin",            "yay",     "🦁",  "Przeglądarki",    "Przeglądarka z blokerem reklam"),
    ("Vivaldi",         "vivaldi",              "yay",     "🎭",  "Przeglądarki",    "Konfigurowalna przeglądarka"),
    ("Google Chrome",   "google-chrome",        "yay",     "🔵",  "Przeglądarki",    "Przeglądarka Google Chrome"),
    ("Tor Browser",     "torbrowser-launcher",  "pacman",  "🧅",  "Przeglądarki",    "Anonimowe przeglądanie internetu"),
    ("LibreWolf",       "librewolf-bin",        "yay",     "🐺",  "Przeglądarki",    "Firefox skupiony na prywatności"),
    ("Zen Browser",     "zen-browser-bin",      "yay",     "🧘",  "Przeglądarki",    "Minimalistyczna przeglądarka"),
    ("Floorp",          "floorp-bin",           "yay",     "🌊",  "Przeglądarki",    "Firefox z drzewem kart i wieloma panelami"),
    ("Epiphany",        "epiphany",             "pacman",  "🌍",  "Przeglądarki",    "Prosta przeglądarka GNOME (Web)"),
    ("Falkon",          "falkon",               "pacman",  "🦅",  "Przeglądarki",    "Lekka przeglądarka KDE"),
    ("Midori",          "midori",               "pacman",  "🟩",  "Przeglądarki",    "Ultralekka przeglądarka"),
    ("Waterfox",        "waterfox-bin",         "yay",     "💧",  "Przeglądarki",    "Firefox fork — szybki i prywatny"),
    ("Opera",           "opera",                "yay",     "🅾️",  "Przeglądarki",    "Przeglądarka z VPN i AI"),
    ("Microsoft Edge",  "microsoft-edge-stable-bin","yay",  "🟦",  "Przeglądarki",    "Edge od Microsoftu na Linuxa"),
    ("Min",             "min",                  "yay",     "➖",  "Przeglądarki",    "Minimalistyczna przeglądarka"),

    # ── Edytory kodu ──
    ("VS Code",         "code",                 "pacman",  "💻",  "Edytory kodu",    "Edytor kodu od Microsoft"),
    ("VS Codium",       "vscodium-bin",         "yay",     "🟦",  "Edytory kodu",    "VS Code bez telemetrii Microsoft"),
    ("Neovim",          "neovim",               "pacman",  "📝",  "Edytory kodu",    "Zaawansowany edytor tekstu"),
    ("Sublime Text",    "sublime-text-4",       "yay",     "🔶",  "Edytory kodu",    "Szybki edytor tekstu"),
    ("Zed",             "zed",                  "pacman",  "⚡",  "Edytory kodu",    "Ultraszybki edytor od twórców Atom"),
    ("Kate",            "kate",                 "pacman",  "📄",  "Edytory kodu",    "Zaawansowany edytor KDE"),
    ("Geany",           "geany",                "pacman",  "📋",  "Edytory kodu",    "Lekkie IDE z kolorowaniem składni"),
    ("Emacs",           "emacs",                "pacman",  "🔮",  "Edytory kodu",    "Rozszerzalny edytor — prawie OS"),
    ("Vim",             "vim",                  "pacman",  "📗",  "Edytory kodu",    "Klasyczny edytor w terminalu"),
    ("Helix",           "helix",                "pacman",  "🌀",  "Edytory kodu",    "Nowoczesny edytor modalny w Rust"),
    ("Lapce",           "lapce",                "pacman",  "⚙️",  "Edytory kodu",    "Szybki edytor kodu w Rust"),
    ("Micro",           "micro",                "pacman",  "🔬",  "Edytory kodu",    "Prosty edytor terminala (jak nano++)"),
    ("Cursor",          "cursor-bin",           "yay",     "🤖",  "Edytory kodu",    "IDE z AI — fork VS Code"),
    ("Arduino IDE",     "arduino-ide-bin",      "yay",     "🔌",  "Edytory kodu",    "Programowanie Arduino"),
    ("JetBrains Toolbox","jetbrains-toolbox",   "yay",     "🧰",  "Edytory kodu",    "Menedżer IDE od JetBrains"),

    # ── Muzyka & Streaming ──
    ("Spotify",         "spotify",              "yay",     "🎵",  "Muzyka",          "Strumieniowanie muzyki — miliony utworów"),
    ("YouTube Music",   "youtube-music-bin",    "yay",     "🎶",  "Muzyka",          "YouTube Music na desktopie"),
    ("Tidal",           "tidal-hifi-bin",       "yay",     "🌊",  "Muzyka",          "Muzyka HiFi — jakość bezstratna"),
    ("Deezer",          "deezer",               "yay",     "🎧",  "Muzyka",          "Strumieniowanie muzyki Deezer"),
    ("Cider",           "cider",                "yay",     "🍎",  "Muzyka",          "Apple Music na Linuxa"),
    ("Strawberry",      "strawberry",           "pacman",  "🍓",  "Muzyka",          "Odtwarzacz muzyki (fork Clementine)"),
    ("Rhythmbox",       "rhythmbox",            "pacman",  "🎼",  "Muzyka",          "Odtwarzacz muzyki GNOME"),
    ("Elisa",           "elisa",                "pacman",  "🎹",  "Muzyka",          "Elegancki odtwarzacz KDE"),
    ("Lollypop",        "lollypop",             "pacman",  "🍭",  "Muzyka",          "Nowoczesny odtwarzacz GNOME"),
    ("Amberol",         "amberol",              "pacman",  "🟠",  "Muzyka",          "Prosty odtwarzacz muzyki GNOME"),
    ("Nuclear",         "nuclear-player-bin",   "yay",     "☢️",  "Muzyka",          "Darmowy streaming z wielu źródeł"),
    ("Spotube",         "spotube-bin",          "yay",     "🟢",  "Muzyka",          "Spotify klient — dźwięk z YouTube"),
    ("Sunamu",          "sunamu-bin",           "yay",     "☀️",  "Muzyka",          "Piękny widget Now Playing"),
    ("Spicetify",       "spicetify-cli",        "yay",     "🌶️",  "Muzyka",          "Motywy i rozszerzenia do Spotify"),
    ("MPD",             "mpd",                  "pacman",  "🎵",  "Muzyka",          "Music Player Daemon — serwer muzyki"),
    ("ncmpcpp",         "ncmpcpp",              "pacman",  "🎹",  "Muzyka",          "Klient MPD w terminalu"),

    # ── Wideo & Streaming ──
    ("VLC",             "vlc",                  "pacman",  "🎬",  "Wideo",           "Uniwersalny odtwarzacz multimedialny"),
    ("MPV",             "mpv",                  "pacman",  "▶️",  "Wideo",           "Lekki odtwarzacz wideo"),
    ("OBS Studio",      "obs-studio",           "pacman",  "🎥",  "Wideo",           "Nagrywanie i streaming"),
    ("Kdenlive",        "kdenlive",             "pacman",  "🎞️",  "Wideo",           "Profesjonalny edytor wideo"),
    ("Stremio",         "stremio",              "yay",     "📺",  "Wideo",           "Centrum streamingowe filmów i seriali"),
    ("FreeTube",        "freetube-bin",         "yay",     "📺",  "Wideo",           "Prywatny klient YouTube"),
    ("Celluloid",       "celluloid",            "pacman",  "🎞️",  "Wideo",           "Prosty odtwarzacz wideo GNOME (MPV)"),
    ("Haruna",          "haruna",               "pacman",  "🎬",  "Wideo",           "Odtwarzacz wideo KDE (MPV)"),
    ("Totem",           "totem",                "pacman",  "🎥",  "Wideo",           "Domyślny odtwarzacz GNOME"),
    ("Shotcut",         "shotcut",              "pacman",  "✂️",  "Wideo",           "Otwarty edytor wideo"),
    ("DaVinci Resolve", "davinci-resolve",      "yay",     "🎬",  "Wideo",           "Profesjonalny edytor wideo Blackmagic"),
    ("Pitivi",          "pitivi",               "pacman",  "🎬",  "Wideo",           "Prosty edytor wideo GNOME"),
    ("Olive",           "olive-editor",         "yay",     "🫒",  "Wideo",           "Otwarty NLE edytor wideo"),
    ("Handbrake",       "handbrake",            "pacman",  "🔄",  "Wideo",           "Konwerter formatów wideo"),
    ("Peek",            "peek",                 "pacman",  "👀",  "Wideo",           "Nagrywanie GIF-ów z ekranu"),
    ("Kodi",            "kodi",                 "pacman",  "🏠",  "Wideo",           "Centrum multimedialne"),
    ("Plex",            "plex-media-player",    "yay",     "🟠",  "Wideo",           "Klient Plex Media Server"),
    ("Jellyfin",        "jellyfin-media-player","pacman",  "🟣",  "Wideo",           "Otwarty klient serwera mediów"),

    # ── Audio & Produkcja ──
    ("Audacity",        "audacity",             "pacman",  "🎤",  "Audio",           "Edytor i nagrywarka dźwięku"),
    ("Ardour",          "ardour",               "pacman",  "🎛️",  "Audio",           "DAW — profesjonalna stacja robocza"),
    ("LMMS",            "lmms",                 "pacman",  "🎹",  "Audio",           "Tworzenie muzyki elektronicznej"),
    ("Hydrogen",        "hydrogen",             "pacman",  "🥁",  "Audio",           "Automat perkusyjny"),
    ("PipeWire",        "pipewire",             "pacman",  "🔊",  "Audio",           "Nowy serwer audio (zamiennik PulseAudio)"),
    ("PulseAudio",      "pulseaudio",           "pacman",  "🔉",  "Audio",           "Klasyczny serwer dźwięku"),
    ("EasyEffects",     "easyeffects",          "pacman",  "🎚️",  "Audio",           "Efekty audio dla PipeWire"),
    ("Helvum",          "helvum",               "pacman",  "🔗",  "Audio",           "Graficzny patchbay PipeWire"),
    ("QjackCtl",        "qjackctl",             "pacman",  "🎧",  "Audio",           "Kontroler JACK audio"),
    ("Carla",           "carla",                "pacman",  "🎵",  "Audio",           "Host pluginów audio"),
    ("Tenacity",        "tenacity-git",         "yay",     "🎤",  "Audio",           "Fork Audacity bez telemetrii"),
    ("SoundConverter",  "soundconverter",       "pacman",  "🔊",  "Audio",           "Konwerter formatów audio"),

    # ── Grafika & Zdjęcia ──
    ("GIMP",            "gimp",                 "pacman",  "🎨",  "Grafika",         "Edytor grafiki rastrowej"),
    ("Inkscape",        "inkscape",             "pacman",  "✒️",  "Grafika",         "Edytor grafiki wektorowej"),
    ("Blender",         "blender",              "pacman",  "🧊",  "Grafika",         "Modelowanie i animacje 3D"),
    ("Krita",           "krita",                "pacman",  "🖌️",  "Grafika",         "Rysowanie cyfrowe i malarstwo"),
    ("Flameshot",       "flameshot",            "pacman",  "📸",  "Grafika",         "Potężne narzędzie do screenshotów"),
    ("Darktable",       "darktable",            "pacman",  "📷",  "Grafika",         "Obróbka zdjęć RAW"),
    ("RawTherapee",     "rawtherapee",          "pacman",  "📸",  "Grafika",         "Zaawansowana obróbka RAW"),
    ("digiKam",         "digikam",              "pacman",  "📷",  "Grafika",         "Zarządzanie kolekcją zdjęć"),
    ("Shotwell",        "shotwell",             "pacman",  "🖼️",  "Grafika",         "Menedżer zdjęć GNOME"),
    ("Gwenview",        "gwenview",             "pacman",  "🖼️",  "Grafika",         "Przeglądarka zdjęć KDE"),
    ("Eye of GNOME",    "eog",                  "pacman",  "👁️",  "Grafika",         "Przeglądarka obrazów GNOME"),
    ("Pinta",           "pinta",                "pacman",  "🎨",  "Grafika",         "Prosty edytor grafiki (jak Paint.NET)"),
    ("Drawio",          "drawio-desktop",       "yay",     "📐",  "Grafika",         "Rysowanie diagramów (draw.io)"),
    ("Figma",           "figma-linux",          "yay",     "🟣",  "Grafika",         "Figma na desktopie Linux"),
    ("Upscayl",         "upscayl-bin",          "yay",     "🔍",  "Grafika",         "Powiększanie zdjęć AI"),
    ("FreeCAD",         "freecad",              "pacman",  "📐",  "Grafika",         "Parametryczne modelowanie 3D CAD"),
    ("OpenSCAD",        "openscad",             "pacman",  "🔧",  "Grafika",         "Programistyczne modelowanie 3D"),
    ("Aseprite",        "aseprite",             "yay",     "🎮",  "Grafika",         "Edytor pixel art i animacji"),

    # ── Gry ──
    ("Steam",           "steam",                "pacman",  "🎮",  "Gry",             "Platforma gier Valve"),
    ("Lutris",          "lutris",               "pacman",  "🕹️",  "Gry",             "Menedżer gier dla Linuxa"),
    ("Heroic Launcher", "heroic-games-launcher-bin", "yay","⚔️",  "Gry",             "Launcher do Epic/GOG/Amazon"),
    ("ProtonUp-Qt",     "protonup-qt",          "yay",     "🍷",  "Gry",             "Menedżer wersji Proton/Wine"),
    ("Minecraft",       "minecraft-launcher",   "yay",     "⛏️",  "Gry",             "Launcher Minecrafta"),
    ("Bottles",         "bottles",              "pacman",  "🍾",  "Gry",             "Uruchamianie Windows apps/gier"),
    ("MangoHud",        "mangohud",             "pacman",  "📊",  "Gry",             "Overlay wydajności w grach"),
    ("Gamemode",        "gamemode",             "pacman",  "🚀",  "Gry",             "Optymalizacja systemu podczas gier"),
    ("RetroArch",       "retroarch",            "pacman",  "🎲",  "Gry",             "Frontend emulatorów retro"),
    ("PCSX2",           "pcsx2",                "pacman",  "🎮",  "Gry",             "Emulator PlayStation 2"),
    ("Dolphin Emu",     "dolphin-emu",          "pacman",  "🐬",  "Gry",             "Emulator GameCube/Wii"),
    ("RPCS3",           "rpcs3-bin",            "yay",     "🎮",  "Gry",             "Emulator PlayStation 3"),
    ("Yuzu",            "yuzu-mainline-bin",    "yay",     "🟡",  "Gry",             "Emulator Nintendo Switch"),
    ("PPSSPP",          "ppsspp",               "pacman",  "🎮",  "Gry",             "Emulator PSP"),
    ("Cemu",            "cemu",                 "pacman",  "🎮",  "Gry",             "Emulator Wii U"),
    ("PrismLauncher",   "prismlauncher",        "pacman",  "🟩",  "Gry",             "Launcher Minecraft (otwarty)"),
    ("GameHub",         "gamehub",              "yay",     "🎮",  "Gry",             "Ujednolicony launcher gier"),
    ("Goverlay",        "goverlay",             "yay",     "📊",  "Gry",             "GUI do MangoHud/vkBasalt"),
    ("SC Controller",   "sc-controller",        "yay",     "🎮",  "Gry",             "Konfiguracja kontrolerów"),
    ("ProtonGE",        "proton-ge-custom-bin", "yay",     "🍷",  "Gry",             "Custom Proton z poprawkami gier"),
    ("Wine",            "wine",                 "pacman",  "🍷",  "Gry",             "Uruchamianie aplikacji Windows"),
    ("Winetricks",      "winetricks",           "pacman",  "🔧",  "Gry",             "Instalator komponentów Windows"),

    # ── Narzędzia systemowe ──
    ("Timeshift",       "timeshift",            "pacman",  "⏰",  "System",          "Tworzenie kopii zapasowych systemu"),
    ("GParted",         "gparted",              "pacman",  "💽",  "System",          "Menedżer partycji"),
    ("Htop",            "htop",                 "pacman",  "📈",  "System",          "Monitor procesów"),
    ("Btop",            "btop",                 "pacman",  "📊",  "System",          "Piękny monitor zasobów"),
    ("Neofetch",        "neofetch",             "pacman",  "🖥️",  "System",          "Informacje o systemie"),
    ("Fastfetch",       "fastfetch",            "pacman",  "⚡",  "System",          "Szybki neofetch w C"),
    ("Ventoy",          "ventoy-bin",           "yay",     "💿",  "System",          "Bootowalne USB z wieloma ISO"),
    ("Baobab",          "baobab",               "pacman",  "🌳",  "System",          "Analiza użycia dysku"),
    ("KDE Partition",   "partitionmanager",     "pacman",  "💽",  "System",          "Menedżer partycji KDE"),
    ("Stacer",          "stacer",               "yay",     "🧹",  "System",          "Optymalizator i monitor systemu"),
    ("BleachBit",       "bleachbit",            "pacman",  "🧽",  "System",          "Czyszczenie systemu z śmieci"),
    ("Terminator",      "terminator",           "pacman",  "🖥️",  "System",          "Terminal z podziałem ekranu"),
    ("Gnome Tweaks",    "gnome-tweaks",         "pacman",  "🔧",  "System",          "Zaawansowane ustawienia GNOME"),
    ("GNOME Extensions","gnome-shell-extensions","pacman",  "🧩",  "System",          "Rozszerzenia do GNOME Shell"),
    ("Kvantum",         "kvantum",              "pacman",  "🎨",  "System",          "Menedżer motywów Qt"),
    ("Dconf Editor",    "dconf-editor",         "pacman",  "⚙️",  "System",          "Edytor ustawień GNOME (dconf)"),
    ("Systemd Manager", "systemd-manager",      "yay",     "🔧",  "System",          "GUI do zarządzania systemd"),
    ("ClamAV",          "clamav",               "pacman",  "🛡️",  "System",          "Antywirus dla Linuxa"),
    ("Firewalld",       "firewalld",            "pacman",  "🧱",  "System",          "Firewall z GUI"),
    ("Snapper",         "snapper",              "pacman",  "📸",  "System",          "Zarządzanie snapshotami BTRFS"),
    ("Grub Customizer", "grub-customizer",      "yay",     "🔧",  "System",          "GUI do konfiguracji GRUB"),

    # ── Terminal & Shell ──
    ("Kitty",           "kitty",                "pacman",  "🐱",  "Terminal",        "Szybki emulator terminala GPU"),
    ("Alacritty",       "alacritty",            "pacman",  "🖤",  "Terminal",        "Najszybszy terminal — GPU"),
    ("Fish",            "fish",                 "pacman",  "🐠",  "Terminal",        "Przyjazna powłoka interaktywna"),
    ("Zsh",             "zsh",                  "pacman",  "🔧",  "Terminal",        "Rozbudowana powłoka Z Shell"),
    ("Tmux",            "tmux",                 "pacman",  "🪟",  "Terminal",        "Multiplekser terminali"),
    ("Starship",        "starship",             "pacman",  "🚀",  "Terminal",        "Piękny prompt dla każdej powłoki"),
    ("Wezterm",         "wezterm",              "pacman",  "🔲",  "Terminal",        "Terminal z GPU i multiplekserem"),
    ("Foot",            "foot",                 "pacman",  "👣",  "Terminal",        "Szybki terminal Wayland"),
    ("Yakuake",         "yakuake",              "pacman",  "⬇️",  "Terminal",        "Rozwijany terminal KDE (F12)"),
    ("Guake",           "guake",                "pacman",  "⬇️",  "Terminal",        "Rozwijany terminal GNOME (F12)"),
    ("Tilix",           "tilix",                "pacman",  "🔲",  "Terminal",        "Terminal GTK z kafelkami"),
    ("Konsole",         "konsole",              "pacman",  "🖥️",  "Terminal",        "Domyślny terminal KDE"),
    ("Oh My Zsh",       "oh-my-zsh-git",        "yay",     "🎩",  "Terminal",        "Framework konfiguracji Zsh"),
    ("Nushell",         "nushell",              "pacman",  "🐚",  "Terminal",        "Nowoczesna powłoka ze strukturami"),
    ("Atuin",           "atuin",                "pacman",  "🔍",  "Terminal",        "Magiczna historia poleceń"),
    ("Zoxide",          "zoxide",               "pacman",  "📂",  "Terminal",        "Szybsza nawigacja katalogów (cd++)"),
    ("Bat",             "bat",                  "pacman",  "🦇",  "Terminal",        "cat z kolorowaniem składni"),
    ("Eza",             "eza",                  "pacman",  "📋",  "Terminal",        "Nowoczesny ls z ikonami"),
    ("Fzf",             "fzf",                  "pacman",  "🔍",  "Terminal",        "Fuzzy finder — szukanie w terminalu"),
    ("Ripgrep",         "ripgrep",              "pacman",  "🔎",  "Terminal",        "Ultraszybki grep w Rust"),
    ("Fd",              "fd",                   "pacman",  "📂",  "Terminal",        "Szybsze find w Rust"),

    # ── Biuro & Produktywność ──
    ("LibreOffice",     "libreoffice-fresh",    "pacman",  "📊",  "Biuro",           "Pakiet biurowy (Writer, Calc, Impress)"),
    ("OnlyOffice",      "onlyoffice-bin",       "yay",     "📄",  "Biuro",           "Pakiet biurowy kompatybilny z MS Office"),
    ("Obsidian",        "obsidian",             "pacman",  "🗒️",  "Biuro",           "Notatki w Markdown z linkami"),
    ("Logseq",          "logseq-desktop-bin",   "yay",     "📓",  "Biuro",           "Otwarte notatki i baza wiedzy"),
    ("Notion",          "notion-app-electron",  "yay",     "📒",  "Biuro",           "Notatki, bazy, zarządzanie projektami"),
    ("Okular",          "okular",               "pacman",  "📕",  "Biuro",           "Czytnik PDF i dokumentów (KDE)"),
    ("Zathura",         "zathura",              "pacman",  "📖",  "Biuro",           "Minimalistyczny czytnik PDF"),
    ("Evince",          "evince",               "pacman",  "📄",  "Biuro",           "Czytnik PDF GNOME"),
    ("Calibre",         "calibre",              "pacman",  "📚",  "Biuro",           "Zarządzanie e-bookami"),
    ("KeePassXC",       "keepassxc",            "pacman",  "🔐",  "Biuro",           "Menedżer haseł offline"),
    ("Bitwarden",       "bitwarden",            "pacman",  "🔒",  "Biuro",           "Menedżer haseł w chmurze"),
    ("Standard Notes",  "standardnotes-bin",    "yay",     "📝",  "Biuro",           "Szyfrowane notatki"),
    ("Joplin",          "joplin-appimage",      "yay",     "📓",  "Biuro",           "Notatki z synchronizacją"),
    ("Anytype",         "anytype-bin",          "yay",     "🧩",  "Biuro",           "Otwarta alternatywa Notion"),
    ("Todoist",         "todoist-electron",     "yay",     "✅",  "Biuro",           "Menedżer zadań"),
    ("Planner",         "planner",              "yay",     "📋",  "Biuro",           "Planowanie zadań (Todoist-like)"),
    ("GnuCash",         "gnucash",              "pacman",  "💰",  "Biuro",           "Zarządzanie finansami"),
    ("GNOME Calendar",  "gnome-calendar",       "pacman",  "📅",  "Biuro",           "Kalendarz GNOME"),
    ("GNOME Contacts",  "gnome-contacts",       "pacman",  "👤",  "Biuro",           "Kontakty GNOME"),

    # ── Sieć & VPN ──
    ("qBittorrent",     "qbittorrent",          "pacman",  "📥",  "Sieć",            "Klient torrentów"),
    ("Transmission",    "transmission-gtk",     "pacman",  "🔄",  "Sieć",            "Lekki klient torrentów"),
    ("Deluge",          "deluge",               "pacman",  "🌊",  "Sieć",            "Rozbudowany klient torrentów"),
    ("Wireshark",       "wireshark-qt",         "pacman",  "🦈",  "Sieć",            "Analizator ruchu sieciowego"),
    ("FileZilla",       "filezilla",            "pacman",  "📂",  "Sieć",            "Klient FTP/SFTP"),
    ("Nmap",            "nmap",                 "pacman",  "🔍",  "Sieć",            "Skaner sieci"),
    ("Wireguard",       "wireguard-tools",      "pacman",  "🔐",  "Sieć",            "Nowoczesny VPN"),
    ("OpenVPN",         "openvpn",              "pacman",  "🛡️",  "Sieć",            "Klient VPN"),
    ("ProtonVPN",       "protonvpn-gui",        "yay",     "🔏",  "Sieć",            "Bezpieczny VPN od Proton"),
    ("NordVPN",         "nordvpn-bin",          "yay",     "🌍",  "Sieć",            "Popularny VPN — NordVPN"),
    ("Mullvad VPN",     "mullvad-vpn-bin",      "yay",     "🟡",  "Sieć",            "Prywatny VPN Mullvad"),
    ("Remmina",         "remmina",              "pacman",  "🖥️",  "Sieć",            "Klient RDP/VNC/SSH"),
    ("AnyDesk",         "anydesk-bin",          "yay",     "🔴",  "Sieć",            "Zdalny pulpit — AnyDesk"),
    ("RustDesk",        "rustdesk-bin",         "yay",     "🟧",  "Sieć",            "Otwarty zdalny pulpit"),
    ("Syncthing",       "syncthing",            "pacman",  "🔃",  "Sieć",            "Synchronizacja plików P2P"),
    ("Nextcloud",       "nextcloud-client",     "pacman",  "☁️",  "Sieć",            "Klient chmury Nextcloud"),
    ("Insomnia",        "insomnia-bin",         "yay",     "🟣",  "Sieć",            "Testowanie API REST/GraphQL"),
    ("Postman",         "postman-bin",          "yay",     "🟠",  "Sieć",            "Popularny klient API"),
    ("Angry IP Scanner","ipscan",               "yay",     "😡",  "Sieć",            "Szybki skaner IP w sieci"),
    ("Etcher",          "balena-etcher",        "yay",     "💿",  "Sieć",            "Nagrywanie obrazów na USB/SD"),

    # ── Wirtualizacja & Kontenery ──
    ("VirtualBox",      "virtualbox",           "pacman",  "📦",  "Wirtualizacja",   "Maszyny wirtualne Oracle"),
    ("Virt-Manager",    "virt-manager",         "pacman",  "🖥️",  "Wirtualizacja",   "Menedżer KVM/QEMU"),
    ("Docker",          "docker",               "pacman",  "🐳",  "Wirtualizacja",   "Kontenery aplikacji"),
    ("Podman",          "podman",               "pacman",  "🦭",  "Wirtualizacja",   "Kontenery bez roota"),
    ("Distrobox",       "distrobox",            "pacman",  "📤",  "Wirtualizacja",   "Inne dystrybucje w kontenerze"),
    ("GNOME Boxes",     "gnome-boxes",          "pacman",  "📦",  "Wirtualizacja",   "Proste maszyny wirtualne GNOME"),
    ("Lazydocker",      "lazydocker",           "pacman",  "🐳",  "Wirtualizacja",   "TUI do zarządzania Dockerem"),
    ("Portainer",       "portainer-bin",        "yay",     "🚢",  "Wirtualizacja",   "Web GUI do Dockera"),
    ("Docker Compose",  "docker-compose",       "pacman",  "🐙",  "Wirtualizacja",   "Orkiestracja kontenerów"),

    # ── Pliki & Menedżery ──
    ("Thunar",          "thunar",               "pacman",  "📁",  "Pliki",           "Lekki menedżer plików (XFCE)"),
    ("Dolphin",         "dolphin",              "pacman",  "🐬",  "Pliki",           "Menedżer plików KDE"),
    ("Nemo",            "nemo",                 "pacman",  "🗂️",  "Pliki",           "Menedżer plików Cinnamon"),
    ("Nautilus",        "nautilus",             "pacman",  "📂",  "Pliki",           "Menedżer plików GNOME (Files)"),
    ("PCManFM",         "pcmanfm",              "pacman",  "📁",  "Pliki",           "Ultralekki menedżer plików"),
    ("Ranger",          "ranger",               "pacman",  "🌲",  "Pliki",           "Menedżer plików w terminalu"),
    ("Yazi",            "yazi",                 "pacman",  "🦆",  "Pliki",           "Blazing fast terminal file manager"),
    ("Double Commander","doublecmd-qt6",        "pacman",  "📂",  "Pliki",           "Dwupanelowy menedżer plików"),
    ("Krusader",        "krusader",             "pacman",  "⚔️",  "Pliki",           "Zaawansowany menedżer dwupanelowy KDE"),
    ("Midnight Cmd",    "mc",                   "pacman",  "🌙",  "Pliki",           "Midnight Commander — klasyka terminala"),
    ("7-Zip",           "7zip",                 "pacman",  "📦",  "Pliki",           "Archiwizer 7z/zip/rar"),
    ("Ark",             "ark",                  "pacman",  "📦",  "Pliki",           "Menedżer archiwów KDE"),
    ("File Roller",     "file-roller",          "pacman",  "📦",  "Pliki",           "Menedżer archiwów GNOME"),

    # ── Pobieranie & Torrenty ──
    ("yt-dlp",          "yt-dlp",               "pacman",  "⬇️",  "Pobieranie",      "Pobieranie filmów z YouTube itp."),
    ("Motrix",          "motrix-bin",           "yay",     "🟦",  "Pobieranie",      "Pełnowartościowy menedżer pobierania"),
    ("Parabolic",       "parabolic",            "yay",     "⬇️",  "Pobieranie",      "Piękny downloader wideo GNOME"),
    ("JDownloader",     "jdownloader2",         "yay",     "📦",  "Pobieranie",      "Menedżer pobierania plików"),
    ("Persepolis",      "persepolis",           "yay",     "🔽",  "Pobieranie",      "GUI dla aria2 — menedżer pobierania"),
    ("Aria2",           "aria2",                "pacman",  "⬇️",  "Pobieranie",      "Ultralekki menedżer pobierania CLI"),
    ("Wget",            "wget",                 "pacman",  "📥",  "Pobieranie",      "Klasyczny downloader HTTP/FTP"),
    ("Curl",            "curl",                 "pacman",  "🔗",  "Pobieranie",      "Transfer danych URL — wszechstronny"),
    ("Video Downloader","video-downloader",     "yay",     "📹",  "Pobieranie",      "GUI do pobierania filmów z YouTube"),
    ("Parabolic",       "parabolic",            "yay",     "⬇️",  "Pobieranie",      "Piękny downloader wideo GNOME"),
    ("Motrix",          "motrix-bin",           "yay",     "🟦",  "Pobieranie",      "Pełnowartościowy menedżer pobierania"),
    ("Fragments",       "fragments",            "pacman",  "🧩",  "Pobieranie",      "Klient BitTorrent GNOME"),

    # ── Personalizacja & Wygląd ──
    ("Latte Dock",      "latte-dock",           "pacman",  "☕",  "Wygląd",          "Elegancki dock KDE"),
    ("Plank",           "plank",                "pacman",  "🔲",  "Wygląd",          "Prosty dock (jak macOS)"),
    ("Conky",           "conky",                "pacman",  "📊",  "Wygląd",          "Widget systemowy na pulpicie"),
    ("Variety",         "variety",              "pacman",  "🖼️",  "Wygląd",          "Automatyczna zmiana tapet"),
    ("Papirus Icons",   "papirus-icon-theme",   "pacman",  "🎨",  "Wygląd",          "Piękny zestaw ikon Papirus"),
    ("Nordic Theme",    "nordic-theme",         "yay",     "❄️",  "Wygląd",          "Ciemny motyw Nordic GTK"),
    ("Dracula Theme",   "dracula-gtk-theme-git","yay",     "🧛",  "Wygląd",          "Popularny motyw Dracula"),
    ("Catppuccin GTK",  "catppuccin-gtk-theme-mocha","yay","🐱",  "Wygląd",          "Pastelowy motyw Catppuccin"),
    ("Nwg-look",        "nwg-look",             "pacman",  "👀",  "Wygląd",          "Konfiguracja GTK Wayland/Sway"),
    ("Kvantum",         "kvantum",              "pacman",  "🎨",  "Wygląd",          "Menedżer motywów Qt"),
    ("Wallpaper Engine","linux-wallpaperengine-git","yay",  "🌄",  "Wygląd",          "Animowane tapety (Steam)"),
    ("Hyprpaper",       "hyprpaper",            "pacman",  "🖼️",  "Wygląd",          "Tapety dla Hyprland"),
    ("Waybar",          "waybar",               "pacman",  "📊",  "Wygląd",          "Pasek statusu Wayland"),
    ("Polybar",         "polybar",              "pacman",  "📊",  "Wygląd",          "Konfigurowalny pasek X11"),
    ("Rofi",            "rofi",                 "pacman",  "🔍",  "Wygląd",          "Launcher aplikacji (zamiennik dmenu)"),
    ("Wofi",            "wofi",                 "pacman",  "🔍",  "Wygląd",          "Launcher aplikacji Wayland"),

    # ── Programowanie & DevTools ──
    ("Git",             "git",                  "pacman",  "📦",  "DevTools",        "System kontroli wersji"),
    ("GitHub CLI",      "github-cli",           "pacman",  "🐙",  "DevTools",        "Oficjalne CLI GitHuba"),
    ("GitKraken",       "gitkraken",            "yay",     "🐙",  "DevTools",        "Piękny GUI klient Git"),
    ("Lazygit",         "lazygit",              "pacman",  "💤",  "DevTools",        "TUI do Gita — szybki i prosty"),
    ("Python",          "python",               "pacman",  "🐍",  "DevTools",        "Język programowania Python"),
    ("Node.js",         "nodejs",               "pacman",  "🟩",  "DevTools",        "Środowisko JavaScript"),
    ("Rust",            "rust",                 "pacman",  "🦀",  "DevTools",        "Język programowania Rust"),
    ("Go",              "go",                   "pacman",  "🔵",  "DevTools",        "Język programowania Go"),
    ("GCC",             "gcc",                  "pacman",  "🔧",  "DevTools",        "Kompilator C/C++"),
    ("CMake",           "cmake",                "pacman",  "🔨",  "DevTools",        "System budowy projektów"),
    ("Meson",           "meson",                "pacman",  "🔧",  "DevTools",        "Nowoczesny system budowy"),
    ("DBeaver",         "dbeaver",              "pacman",  "🗄️",  "DevTools",        "Uniwersalny klient baz danych"),
    ("Beekeeper Studio","beekeeper-studio-bin", "yay",     "🐝",  "DevTools",        "Piękny GUI do baz danych"),
    ("Bruno",           "bruno-bin",            "yay",     "🟤",  "DevTools",        "Otwarta alternatywa Postmana"),
    ("Meld",            "meld",                 "pacman",  "🔀",  "DevTools",        "Narzędzie do porównywania plików"),
    ("Ghidra",          "ghidra",               "pacman",  "🔍",  "DevTools",        "Reverse engineering (NSA)"),

    # ── Social Media & Content ──
    ("Freetube",        "freetube-bin",         "yay",     "📺",  "Social",          "Prywatny klient YouTube"),
    ("NewPipe",         "newpipe-bin",          "yay",     "🟠",  "Social",          "YouTube bez reklam (Android bridge)"),
    ("Newsflash",       "newsflash",            "pacman",  "📰",  "Social",          "Czytnik RSS GNOME"),
    ("Akregator",       "akregator",            "pacman",  "📰",  "Social",          "Czytnik RSS KDE"),
    ("Cawbird",         "cawbird",              "yay",     "🐦",  "Social",          "Klient Twittera"),
    ("Tuba",            "tuba",                 "pacman",  "🐘",  "Social",          "Klient Mastodon GNOME"),
    ("Reddit",          "redlib",               "yay",     "🟠",  "Social",          "Prywatny frontend Reddita"),

    # ── NO INTERESING ──
    ("Protontricks",    "protontricks",         "pacman",  "🔧",  "NO INTERESING",   "Ładowanie componentów do gier Wine/Proton"),
    ("Winetricks",      "winetricks",           "pacman",  "🍷",  "NO INTERESING",   "Instalator componentów Windows dla Wine"),
    ("DosBox",          "dosbox",               "pacman",  "💾",  "NO INTERESING",   "Emulator DOS — stare gry"),
    ("ScummVM",         "scummvm",              "pacman",  "🎮",  "NO INTERESING",   "Maszyna wirtualna gier przygodowych"),
    ("GameHub",         "gamehub",              "yay",     "🕹️",  "NO INTERESING",   "Ujednolicony launcher gier + modów"),
    ("Conky",           "conky",                "pacman",  "📊",  "NO INTERESING",   "Overlay systemowy i debuger"),
]

# Categories in display order
APP_CATEGORIES = [
    "Komunikatory", "Przeglądarki", "Muzyka", "Wideo", "Audio",
    "Grafika", "Gry", "Edytory kodu", "DevTools",
    "System", "Terminal", "Biuro", "Sieć",
    "Wirtualizacja", "Pliki", "Pobieranie", "Wygląd", "Social", "NO INTERESING"
]


class InstallThread(QThread):
    """Thread for installing/removing an app."""
    finished = pyqtSignal(bool, str)
    output_line = pyqtSignal(str)

    def __init__(self, pkg_name: str, source: str, action: str):
        super().__init__()
        self.pkg_name = pkg_name
        self.source = source
        self.action = action

    def run(self):
        try:
            if self.action == "install":
                if self.source == "yay":
                    # yay should NOT run with sudo - it will handle elevation internally
                    cmd = ['yay', '-S', '--noconfirm', self.pkg_name]
                else:
                    cmd = ['sudo', 'pacman', '-S', '--noconfirm', self.pkg_name]
            else:
                cmd = ['sudo', 'pacman', '-R', '--noconfirm', self.pkg_name]

            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1
            )
            output = []
            for line in iter(process.stdout.readline, ''):
                if line:
                    output.append(line)
                    self.output_line.emit(line)
            process.wait(timeout=300)
            self.finished.emit(process.returncode == 0, ''.join(output))
        except Exception as e:
            self.finished.emit(False, str(e))


class AppCard(QFrame):
    """A single app card in the grid."""
    install_requested = pyqtSignal(str, str, str)  # pkg_name, source, action

    def __init__(self, name, pkg_name, source, emoji, category, description, installed=False):
        super().__init__()
        self.pkg_name = pkg_name
        self.source = source
        self.app_name = name
        self._installed = installed

        self.setFixedSize(260, 160)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_style()

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 12)
        lay.setSpacing(6)

        # Top row: emoji + name
        top = QHBoxLayout()
        top.setSpacing(10)
        icon_lbl = QLabel(emoji)
        icon_lbl.setStyleSheet("font-size: 28px; background: transparent;")
        top.addWidget(icon_lbl)

        name_lbl = QLabel(name)
        nf = QFont()
        nf.setPointSize(13)
        nf.setBold(True)
        name_lbl.setFont(nf)
        name_lbl.setStyleSheet("color: #fff; background: transparent;")
        top.addWidget(name_lbl)
        top.addStretch()
        lay.addLayout(top)

        # Description
        desc_lbl = QLabel(description)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("color: #aaa; font-size: 11px; background: transparent;")
        desc_lbl.setMaximumHeight(34)
        lay.addWidget(desc_lbl)

        # Source badge + button
        bottom = QHBoxLayout()
        bottom.setSpacing(8)

        source_tag = source.upper()
        tag_color = "#ff79c6" if source == "yay" else "#8be9fd"
        src_lbl = QLabel(f"via {source_tag}")
        src_lbl.setStyleSheet(f"""
            color: {tag_color};
            font-size: 10px;
            font-weight: 700;
            background: rgba(255,255,255,0.05);
            border-radius: 4px;
            padding: 3px 8px;
        """)
        src_lbl.setFixedHeight(22)
        bottom.addWidget(src_lbl)
        bottom.addStretch()

        self.btn = QPushButton()
        self.btn.setFixedSize(90, 28)
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_button()
        self.btn.clicked.connect(self._on_click)
        bottom.addWidget(self.btn)

        lay.addStretch()
        lay.addLayout(bottom)

    def _update_style(self):
        border = "#3a3a50" if not self._installed else "#50fa7b"
        self.setStyleSheet(f"""
            AppCard {{
                background: #1e1e2e;
                border: 1px solid {border};
                border-radius: 12px;
            }}
            AppCard:hover {{
                background: #252540;
                border-color: #6c71c4;
            }}
        """)

    def _update_button(self):
        if self._installed:
            self.btn.setText("Usuń")
            self.btn.setStyleSheet("""
                QPushButton {
                    background: #444;
                    color: #aaa;
                    border: none;
                    border-radius: 6px;
                    font-weight: 600;
                    font-size: 11px;
                }
                QPushButton:hover { background: #555; color: #fff; }
            """)
        else:
            self.btn.setText("Zainstaluj")
            self.btn.setStyleSheet("""
                QPushButton {
                    background: #6c71c4;
                    color: #fff;
                    border: none;
                    border-radius: 6px;
                    font-weight: 600;
                    font-size: 11px;
                }
                QPushButton:hover { background: #7c81d4; }
            """)

    def set_installed(self, val: bool):
        self._installed = val
        self._update_style()
        self._update_button()

    def _on_click(self):
        action = "remove" if self._installed else "install"
        self.install_requested.emit(self.pkg_name, self.source, action)


class AppStoreWidget(QWidget):
    """Grid view of curated applications."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cards: Dict[str, AppCard] = {}
        self._thread: Optional[InstallThread] = None
        self._installed_set = set()
        self._filter_category = None  # If set, only show this category
        self._load_installed()
        self._build()

    def _load_installed(self):
        try:
            r = subprocess.run(['pacman', '-Q'], capture_output=True, text=True, timeout=10)
            self._installed_set = {
                line.split()[0] for line in r.stdout.strip().split('\n') if line.strip()
            }
        except Exception:
            self._installed_set = set()

    def _build(self):
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        # Search bar
        search_area = QHBoxLayout()
        search_area.setContentsMargins(0, 0, 0, 14)
        self._search = QLineEdit()
        self._search.setPlaceholderText("🔍  Szukaj aplikacji...")
        self._search.setFixedHeight(38)
        self._search.setStyleSheet("""
            QLineEdit {
                background: #1e1e2e;
                color: #e8e8e8;
                border: 1px solid #3a3a50;
                border-radius: 8px;
                padding: 0 14px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #6c71c4;
            }
        """)
        self._search.textChanged.connect(self._on_search)
        search_area.addWidget(self._search)
        main_lay.addLayout(search_area)

        # Scroll area for the grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)

        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        self._grid_lay = QVBoxLayout(self._container)
        self._grid_lay.setContentsMargins(0, 0, 10, 0)
        self._grid_lay.setSpacing(20)

        self._populate_grid()

        scroll.setWidget(self._container)
        main_lay.addWidget(scroll, stretch=1)

    def _populate_grid(self, filter_text=""):
        # Clear existing
        while self._grid_lay.count():
            child = self._grid_lay.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())

        self._cards.clear()
        ft = filter_text.lower()

        # Determine which categories to show
        categories_to_show = [self._filter_category] if self._filter_category else APP_CATEGORIES

        for cat in categories_to_show:
            apps = [a for a in APP_CATALOG if a[4] == cat]
            if ft:
                apps = [a for a in apps if ft in a[0].lower() or ft in a[5].lower() or ft in a[1].lower()]
            if not apps:
                continue

            # Category header
            hdr = QLabel(f"  {cat}")
            hf = QFont()
            hf.setPointSize(14)
            hf.setBold(True)
            hdr.setFont(hf)
            hdr.setStyleSheet("color: #e8e8e8; background: transparent; padding: 4px 0; margin-top: 6px;")
            self._grid_lay.addWidget(hdr)

            # Cards in rows of 4
            row_lay = None
            for i, (name, pkg, src, emoji, _cat, desc) in enumerate(apps):
                if i % 4 == 0:
                    row_lay = QHBoxLayout()
                    row_lay.setSpacing(14)
                    self._grid_lay.addLayout(row_lay)

                installed = pkg in self._installed_set
                card = AppCard(name, pkg, src, emoji, _cat, desc, installed)
                card.install_requested.connect(self._on_install)
                self._cards[pkg] = card
                row_lay.addWidget(card)

            # Fill remaining space in last row
            if row_lay and len(apps) % 4 != 0:
                for _ in range(4 - len(apps) % 4):
                    spacer = QWidget()
                    spacer.setFixedSize(260, 160)
                    spacer.setStyleSheet("background: transparent;")
                    row_lay.addWidget(spacer)

        self._grid_lay.addStretch()

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())

    def _on_search(self, text):
        self._populate_grid(text)

    def _on_install(self, pkg_name, source, action):
        label = "Instalowanie" if action == "install" else "Usuwanie"
        dlg = InstallProgressDialog(pkg_name, label, self)
        self._thread = InstallThread(pkg_name, source, action)
        self._thread.output_line.connect(dlg.append_output)

        def done(ok, msg):
            dlg.set_completed(ok)
            if ok:
                if action == "install":
                    self._installed_set.add(pkg_name)
                else:
                    self._installed_set.discard(pkg_name)
                # Refresh grid with current search to show updated status immediately
                current_search = self._search.text()
                self._populate_grid(current_search)

        self._thread.finished.connect(done)
        self._thread.start()
        dlg.exec()

    def refresh_installed(self):
        """Refresh installed status of all cards."""
        self._load_installed()
        for pkg, card in self._cards.items():
            card.set_installed(pkg in self._installed_set)
