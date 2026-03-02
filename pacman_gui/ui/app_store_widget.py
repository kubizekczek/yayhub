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
    # ── Messengers ──
    ("Discord",         "discord",              "pacman",  "💬",  "Messengers",      "Voice & text chat for gamers"),
    ("Telegram",        "telegram-desktop",     "pacman",  "✈️",  "Messengers",      "Fast and secure messenger"),
    ("Signal",          "signal-desktop",       "yay",     "🔒",  "Messengers",      "Private messenger with E2E encryption"),
    ("Element",         "element-desktop",      "pacman",  "🟢",  "Messengers",      "Matrix client — decentralized chat"),
    ("Slack",           "slack-desktop",        "yay",     "💼",  "Messengers",      "Team communication platform"),
    ("Teams",           "teams-for-linux",      "yay",     "👥",  "Messengers",      "Microsoft Teams for Linux"),
    ("Vesktop",         "vesktop-bin",          "yay",     "🎧",  "Messengers",      "Discord with Vencord — improved"),
    ("WhatsApp",        "whatsapp-for-linux",   "yay",     "📱",  "Messengers",      "WhatsApp on Linux desktop"),
    ("Revolt",          "revolt-desktop",       "yay",     "🔴",  "Messengers",      "Open-source Discord alternative"),
    ("Mumble",          "mumble",               "pacman",  "🎙️",  "Messengers",      "Low-latency voice chat"),
    ("Pidgin",          "pidgin",               "pacman",  "🐦",  "Messengers",      "Multi-protocol messenger"),
    ("Hexchat",         "hexchat",              "pacman",  "💬",  "Messengers",      "IRC client"),
    ("Thunderbird",     "thunderbird",          "pacman",  "📧",  "Messengers",      "Email client by Mozilla"),
    ("Skype",           "skypeforlinux-bin",    "yay",     "📞",  "Messengers",      "Video calls and messenger"),
    ("Zoom",            "zoom",                 "yay",     "📹",  "Messengers",      "Zoom video conferencing"),
    ("Jitsi Meet",      "jitsi-meet-desktop-bin","yay",    "🤝",  "Messengers",      "Open-source video conferencing"),
    ("Wire",            "wire-desktop",         "yay",     "🔗",  "Messengers",      "Secure business messenger"),
    ("Keybase",         "keybase-gui",          "yay",     "🔑",  "Messengers",      "Encrypted chat + files"),

    # ── Browsers ──
    ("Firefox",         "firefox",              "pacman",  "🦊",  "Browsers",        "Fast browser by Mozilla"),
    ("Chromium",        "chromium",             "pacman",  "🌐",  "Browsers",        "Open-source browser by Google"),
    ("Brave",           "brave-bin",            "yay",     "🦁",  "Browsers",        "Browser with built-in ad blocker"),
    ("Vivaldi",         "vivaldi",              "yay",     "🎭",  "Browsers",        "Highly customizable browser"),
    ("Google Chrome",   "google-chrome",        "yay",     "🔵",  "Browsers",        "Google Chrome browser"),
    ("Tor Browser",     "torbrowser-launcher",  "pacman",  "🧅",  "Browsers",        "Anonymous web browsing"),
    ("LibreWolf",       "librewolf-bin",        "yay",     "🐺",  "Browsers",        "Privacy-focused Firefox fork"),
    ("Zen Browser",     "zen-browser-bin",      "yay",     "🧘",  "Browsers",        "Minimalist browser"),
    ("Floorp",          "floorp-bin",           "yay",     "🌊",  "Browsers",        "Firefox with tab tree & panels"),
    ("Epiphany",        "epiphany",             "pacman",  "🌍",  "Browsers",        "Simple GNOME browser (Web)"),
    ("Falkon",          "falkon",               "pacman",  "🦅",  "Browsers",        "Lightweight KDE browser"),
    ("Midori",          "midori",               "pacman",  "🟩",  "Browsers",        "Ultra-lightweight browser"),
    ("Waterfox",        "waterfox-bin",         "yay",     "💧",  "Browsers",        "Firefox fork — fast & private"),
    ("Opera",           "opera",                "yay",     "🅾️",  "Browsers",        "Browser with VPN and AI"),
    ("Microsoft Edge",  "microsoft-edge-stable-bin","yay",  "🟦",  "Browsers",        "Microsoft Edge for Linux"),
    ("Min",             "min",                  "yay",     "➖",  "Browsers",        "Minimalist browser"),

    # ── Code Editors ──
    ("VS Code",         "code",                 "pacman",  "💻",  "Code Editors",    "Code editor by Microsoft"),
    ("VS Codium",       "vscodium-bin",         "yay",     "🟦",  "Code Editors",    "VS Code without MS telemetry"),
    ("Neovim",          "neovim",               "pacman",  "📝",  "Code Editors",    "Advanced text editor"),
    ("Sublime Text",    "sublime-text-4",       "yay",     "🔶",  "Code Editors",    "Fast text editor"),
    ("Zed",             "zed",                  "pacman",  "⚡",  "Code Editors",    "Ultra-fast editor by Atom creators"),
    ("Kate",            "kate",                 "pacman",  "📄",  "Code Editors",    "Advanced KDE editor"),
    ("Geany",           "geany",                "pacman",  "📋",  "Code Editors",    "Lightweight IDE with syntax highlight"),
    ("Emacs",           "emacs",                "pacman",  "🔮",  "Code Editors",    "Extensible editor — almost an OS"),
    ("Vim",             "vim",                  "pacman",  "📗",  "Code Editors",    "Classic terminal editor"),
    ("Helix",           "helix",                "pacman",  "🌀",  "Code Editors",    "Modern modal editor in Rust"),
    ("Lapce",           "lapce",                "pacman",  "⚙️",  "Code Editors",    "Fast code editor in Rust"),
    ("Micro",           "micro",                "pacman",  "🔬",  "Code Editors",    "Simple terminal editor (nano++)"),
    ("Cursor",          "cursor-bin",           "yay",     "🤖",  "Code Editors",    "AI-powered IDE — VS Code fork"),
    ("Arduino IDE",     "arduino-ide-bin",      "yay",     "🔌",  "Code Editors",    "Arduino programming IDE"),
    ("JetBrains Toolbox","jetbrains-toolbox",   "yay",     "🧰",  "Code Editors",    "JetBrains IDE manager"),

    # ── Music & Streaming ──
    ("Spotify",         "spotify",              "yay",     "🎵",  "Music",           "Music streaming — millions of tracks"),
    ("YouTube Music",   "youtube-music-bin",    "yay",     "🎶",  "Music",           "YouTube Music on desktop"),
    ("Tidal",           "tidal-hifi-bin",       "yay",     "🌊",  "Music",           "HiFi music — lossless quality"),
    ("Deezer",          "deezer",               "yay",     "🎧",  "Music",           "Deezer music streaming"),
    ("Cider",           "cider",                "yay",     "🍎",  "Music",           "Apple Music for Linux"),
    ("Strawberry",      "strawberry",           "pacman",  "🍓",  "Music",           "Music player (Clementine fork)"),
    ("Rhythmbox",       "rhythmbox",            "pacman",  "🎼",  "Music",           "GNOME music player"),
    ("Elisa",           "elisa",                "pacman",  "🎹",  "Music",           "Elegant KDE music player"),
    ("Lollypop",        "lollypop",             "pacman",  "🍭",  "Music",           "Modern GNOME music player"),
    ("Amberol",         "amberol",              "pacman",  "🟠",  "Music",           "Simple GNOME music player"),
    ("Nuclear",         "nuclear-player-bin",   "yay",     "☢️",  "Music",           "Free streaming from many sources"),
    ("Spotube",         "spotube-bin",          "yay",     "🟢",  "Music",           "Spotify client — audio via YouTube"),
    ("Sunamu",          "sunamu-bin",           "yay",     "☀️",  "Music",           "Beautiful Now Playing widget"),
    ("Spicetify",       "spicetify-cli",        "yay",     "🌶️",  "Music",           "Themes & extensions for Spotify"),
    ("MPD",             "mpd",                  "pacman",  "🎵",  "Music",           "Music Player Daemon — music server"),
    ("ncmpcpp",         "ncmpcpp",              "pacman",  "🎹",  "Music",           "Terminal MPD client"),

    # ── Video & Streaming ──
    ("VLC",             "vlc",                  "pacman",  "🎬",  "Video",           "Universal media player"),
    ("MPV",             "mpv",                  "pacman",  "▶️",  "Video",           "Lightweight video player"),
    ("OBS Studio",      "obs-studio",           "pacman",  "🎥",  "Video",           "Recording and streaming"),
    ("Kdenlive",        "kdenlive",             "pacman",  "🎞️",  "Video",           "Professional video editor"),
    ("Stremio",         "stremio",              "yay",     "📺",  "Video",           "Streaming hub for movies & series"),
    ("FreeTube",        "freetube-bin",         "yay",     "📺",  "Video",           "Private YouTube client"),
    ("Celluloid",       "celluloid",            "pacman",  "🎞️",  "Video",           "Simple GNOME video player (MPV)"),
    ("Haruna",          "haruna",               "pacman",  "🎬",  "Video",           "KDE video player (MPV)"),
    ("Totem",           "totem",                "pacman",  "🎥",  "Video",           "Default GNOME video player"),
    ("Shotcut",         "shotcut",              "pacman",  "✂️",  "Video",           "Open-source video editor"),
    ("DaVinci Resolve", "davinci-resolve",      "yay",     "🎬",  "Video",           "Professional Blackmagic video editor"),
    ("Pitivi",          "pitivi",               "pacman",  "🎬",  "Video",           "Simple GNOME video editor"),
    ("Olive",           "olive-editor",         "yay",     "🫒",  "Video",           "Open-source NLE video editor"),
    ("Handbrake",       "handbrake",            "pacman",  "🔄",  "Video",           "Video format converter"),
    ("Peek",            "peek",                 "pacman",  "👀",  "Video",           "Screen GIF recorder"),
    ("Kodi",            "kodi",                 "pacman",  "🏠",  "Video",           "Media center"),
    ("Plex",            "plex-media-player",    "yay",     "🟠",  "Video",           "Plex Media Server client"),
    ("Jellyfin",        "jellyfin-media-player","pacman",  "🟣",  "Video",           "Open-source media server client"),

    # ── Audio & Production ──
    ("Audacity",        "audacity",             "pacman",  "🎤",  "Audio",           "Audio editor and recorder"),
    ("Ardour",          "ardour",               "pacman",  "🎛️",  "Audio",           "DAW — professional workstation"),
    ("LMMS",            "lmms",                 "pacman",  "🎹",  "Audio",           "Electronic music production"),
    ("Hydrogen",        "hydrogen",             "pacman",  "🥁",  "Audio",           "Drum machine"),
    ("PipeWire",        "pipewire",             "pacman",  "🔊",  "Audio",           "New audio server (PulseAudio replacement)"),
    ("PulseAudio",      "pulseaudio",           "pacman",  "🔉",  "Audio",           "Classic sound server"),
    ("EasyEffects",     "easyeffects",          "pacman",  "🎚️",  "Audio",           "Audio effects for PipeWire"),
    ("Helvum",          "helvum",               "pacman",  "🔗",  "Audio",           "Graphical PipeWire patchbay"),
    ("QjackCtl",        "qjackctl",             "pacman",  "🎧",  "Audio",           "JACK audio controller"),
    ("Carla",           "carla",                "pacman",  "🎵",  "Audio",           "Audio plugin host"),
    ("Tenacity",        "tenacity-git",         "yay",     "🎤",  "Audio",           "Audacity fork without telemetry"),
    ("SoundConverter",  "soundconverter",       "pacman",  "🔊",  "Audio",           "Audio format converter"),

    # ── Graphics & Photos ──
    ("GIMP",            "gimp",                 "pacman",  "🎨",  "Graphics",        "Raster graphics editor"),
    ("Inkscape",        "inkscape",             "pacman",  "✒️",  "Graphics",        "Vector graphics editor"),
    ("Blender",         "blender",              "pacman",  "🧊",  "Graphics",        "3D modeling and animation"),
    ("Krita",           "krita",                "pacman",  "🖌️",  "Graphics",        "Digital drawing and painting"),
    ("Flameshot",       "flameshot",            "pacman",  "📸",  "Graphics",        "Powerful screenshot tool"),
    ("Darktable",       "darktable",            "pacman",  "📷",  "Graphics",        "RAW photo processing"),
    ("RawTherapee",     "rawtherapee",          "pacman",  "📸",  "Graphics",        "Advanced RAW processing"),
    ("digiKam",         "digikam",              "pacman",  "📷",  "Graphics",        "Photo collection manager"),
    ("Shotwell",        "shotwell",             "pacman",  "🖼️",  "Graphics",        "GNOME photo manager"),
    ("Gwenview",        "gwenview",             "pacman",  "🖼️",  "Graphics",        "KDE image viewer"),
    ("Eye of GNOME",    "eog",                  "pacman",  "👁️",  "Graphics",        "GNOME image viewer"),
    ("Pinta",           "pinta",                "pacman",  "🎨",  "Graphics",        "Simple editor (like Paint.NET)"),
    ("Drawio",          "drawio-desktop",       "yay",     "📐",  "Graphics",        "Diagram drawing (draw.io)"),
    ("Figma",           "figma-linux",          "yay",     "🟣",  "Graphics",        "Figma on Linux desktop"),
    ("Upscayl",         "upscayl-bin",          "yay",     "🔍",  "Graphics",        "AI image upscaling"),
    ("FreeCAD",         "freecad",              "pacman",  "📐",  "Graphics",        "Parametric 3D CAD modeling"),
    ("OpenSCAD",        "openscad",             "pacman",  "🔧",  "Graphics",        "Programmatic 3D modeling"),
    ("Aseprite",        "aseprite",             "yay",     "🎮",  "Graphics",        "Pixel art & animation editor"),

    # ── Games ──
    ("Steam",           "steam",                "pacman",  "🎮",  "Games",           "Valve gaming platform"),
    ("Lutris",          "lutris",               "pacman",  "🕹️",  "Games",           "Linux game manager"),
    ("Heroic Launcher", "heroic-games-launcher-bin", "yay","⚔️",  "Games",           "Launcher for Epic/GOG/Amazon"),
    ("ProtonUp-Qt",     "protonup-qt",          "yay",     "🍷",  "Games",           "Proton/Wine version manager"),
    ("Minecraft",       "minecraft-launcher",   "yay",     "⛏️",  "Games",           "Minecraft launcher"),
    ("Bottles",         "bottles",              "pacman",  "🍾",  "Games",           "Run Windows apps/games"),
    ("MangoHud",        "mangohud",             "pacman",  "📊",  "Games",           "In-game performance overlay"),
    ("Gamemode",        "gamemode",             "pacman",  "🚀",  "Games",           "System optimization for gaming"),
    ("RetroArch",       "retroarch",            "pacman",  "🎲",  "Games",           "Retro emulator frontend"),
    ("PCSX2",           "pcsx2",                "pacman",  "🎮",  "Games",           "PlayStation 2 emulator"),
    ("Dolphin Emu",     "dolphin-emu",          "pacman",  "🐬",  "Games",           "GameCube/Wii emulator"),
    ("RPCS3",           "rpcs3-bin",            "yay",     "🎮",  "Games",           "PlayStation 3 emulator"),
    ("Yuzu",            "yuzu-mainline-bin",    "yay",     "🟡",  "Games",           "Nintendo Switch emulator"),
    ("PPSSPP",          "ppsspp",               "pacman",  "🎮",  "Games",           "PSP emulator"),
    ("Cemu",            "cemu",                 "pacman",  "🎮",  "Games",           "Wii U emulator"),
    ("PrismLauncher",   "prismlauncher",        "pacman",  "🟩",  "Games",           "Open-source Minecraft launcher"),
    ("GameHub",         "gamehub",              "yay",     "🎮",  "Games",           "Unified game launcher"),
    ("Goverlay",        "goverlay",             "yay",     "📊",  "Games",           "GUI for MangoHud/vkBasalt"),
    ("SC Controller",   "sc-controller",        "yay",     "🎮",  "Games",           "Controller configuration"),
    ("ProtonGE",        "proton-ge-custom-bin", "yay",     "🍷",  "Games",           "Custom Proton with game fixes"),
    ("Wine",            "wine",                 "pacman",  "🍷",  "Games",           "Run Windows applications"),
    ("Winetricks",      "winetricks",           "pacman",  "🔧",  "Games",           "Windows component installer"),

    # ── System Tools ──
    ("Timeshift",       "timeshift",            "pacman",  "⏰",  "System",          "System backup & restore"),
    ("GParted",         "gparted",              "pacman",  "💽",  "System",          "Partition manager"),
    ("Htop",            "htop",                 "pacman",  "📈",  "System",          "Process monitor"),
    ("Btop",            "btop",                 "pacman",  "📊",  "System",          "Beautiful resource monitor"),
    ("Neofetch",        "neofetch",             "pacman",  "🖥️",  "System",          "System information display"),
    ("Fastfetch",       "fastfetch",            "pacman",  "⚡",  "System",          "Fast neofetch written in C"),
    ("Ventoy",          "ventoy-bin",           "yay",     "💿",  "System",          "Bootable USB with multiple ISOs"),
    ("Baobab",          "baobab",               "pacman",  "🌳",  "System",          "Disk usage analyzer"),
    ("KDE Partition",   "partitionmanager",     "pacman",  "💽",  "System",          "KDE partition manager"),
    ("Stacer",          "stacer",               "yay",     "🧹",  "System",          "System optimizer and monitor"),
    ("BleachBit",       "bleachbit",            "pacman",  "🧽",  "System",          "System junk cleaner"),
    ("Terminator",      "terminator",           "pacman",  "🖥️",  "System",          "Terminal with split screen"),
    ("Gnome Tweaks",    "gnome-tweaks",         "pacman",  "🔧",  "System",          "Advanced GNOME settings"),
    ("GNOME Extensions","gnome-shell-extensions","pacman",  "🧩",  "System",          "GNOME Shell extensions"),
    ("Kvantum",         "kvantum",              "pacman",  "🎨",  "System",          "Qt theme manager"),
    ("Dconf Editor",    "dconf-editor",         "pacman",  "⚙️",  "System",          "GNOME settings editor (dconf)"),
    ("Systemd Manager", "systemd-manager",      "yay",     "🔧",  "System",          "GUI for managing systemd"),
    ("ClamAV",          "clamav",               "pacman",  "🛡️",  "System",          "Antivirus for Linux"),
    ("Firewalld",       "firewalld",            "pacman",  "🧱",  "System",          "Firewall with GUI"),
    ("Snapper",         "snapper",              "pacman",  "📸",  "System",          "BTRFS snapshot manager"),
    ("Grub Customizer", "grub-customizer",      "yay",     "🔧",  "System",          "GUI for GRUB configuration"),

    # ── Terminal & Shell ──
    ("Kitty",           "kitty",                "pacman",  "🐱",  "Terminal",        "Fast GPU terminal emulator"),
    ("Alacritty",       "alacritty",            "pacman",  "🖤",  "Terminal",        "Fastest terminal — GPU-based"),
    ("Fish",            "fish",                 "pacman",  "🐠",  "Terminal",        "Friendly interactive shell"),
    ("Zsh",             "zsh",                  "pacman",  "🔧",  "Terminal",        "Feature-rich Z Shell"),
    ("Tmux",            "tmux",                 "pacman",  "🪟",  "Terminal",        "Terminal multiplexer"),
    ("Starship",        "starship",             "pacman",  "🚀",  "Terminal",        "Beautiful prompt for any shell"),
    ("Wezterm",         "wezterm",              "pacman",  "🔲",  "Terminal",        "GPU terminal with multiplexer"),
    ("Foot",            "foot",                 "pacman",  "👣",  "Terminal",        "Fast Wayland terminal"),
    ("Yakuake",         "yakuake",              "pacman",  "⬇️",  "Terminal",        "KDE drop-down terminal (F12)"),
    ("Guake",           "guake",                "pacman",  "⬇️",  "Terminal",        "GNOME drop-down terminal (F12)"),
    ("Tilix",           "tilix",                "pacman",  "🔲",  "Terminal",        "GTK tiling terminal"),
    ("Konsole",         "konsole",              "pacman",  "🖥️",  "Terminal",        "Default KDE terminal"),
    ("Oh My Zsh",       "oh-my-zsh-git",        "yay",     "🎩",  "Terminal",        "Zsh configuration framework"),
    ("Nushell",         "nushell",              "pacman",  "🐚",  "Terminal",        "Modern shell with data structures"),
    ("Atuin",           "atuin",                "pacman",  "🔍",  "Terminal",        "Magical shell history"),
    ("Zoxide",          "zoxide",               "pacman",  "📂",  "Terminal",        "Faster directory navigation (cd++)"),
    ("Bat",             "bat",                  "pacman",  "🦇",  "Terminal",        "cat with syntax highlighting"),
    ("Eza",             "eza",                  "pacman",  "📋",  "Terminal",        "Modern ls with icons"),
    ("Fzf",             "fzf",                  "pacman",  "🔍",  "Terminal",        "Fuzzy finder for terminal"),
    ("Ripgrep",         "ripgrep",              "pacman",  "🔎",  "Terminal",        "Ultra-fast grep in Rust"),
    ("Fd",              "fd",                   "pacman",  "📂",  "Terminal",        "Faster find in Rust"),

    # ── Office & Productivity ──
    ("LibreOffice",     "libreoffice-fresh",    "pacman",  "📊",  "Office",          "Office suite (Writer, Calc, Impress)"),
    ("OnlyOffice",      "onlyoffice-bin",       "yay",     "📄",  "Office",          "MS Office-compatible office suite"),
    ("Obsidian",        "obsidian",             "pacman",  "🗒️",  "Office",          "Markdown notes with linking"),
    ("Logseq",          "logseq-desktop-bin",   "yay",     "📓",  "Office",          "Open-source notes & knowledge base"),
    ("Notion",          "notion-app-electron",  "yay",     "📒",  "Office",          "Notes, databases, project management"),
    ("Okular",          "okular",               "pacman",  "📕",  "Office",          "PDF & document reader (KDE)"),
    ("Zathura",         "zathura",              "pacman",  "📖",  "Office",          "Minimalist PDF reader"),
    ("Evince",          "evince",               "pacman",  "📄",  "Office",          "GNOME PDF reader"),
    ("Calibre",         "calibre",              "pacman",  "📚",  "Office",          "E-book manager"),
    ("KeePassXC",       "keepassxc",            "pacman",  "🔐",  "Office",          "Offline password manager"),
    ("Bitwarden",       "bitwarden",            "pacman",  "🔒",  "Office",          "Cloud password manager"),
    ("Standard Notes",  "standardnotes-bin",    "yay",     "📝",  "Office",          "Encrypted notes"),
    ("Joplin",          "joplin-appimage",      "yay",     "📓",  "Office",          "Notes with sync"),
    ("Anytype",         "anytype-bin",          "yay",     "🧩",  "Office",          "Open-source Notion alternative"),
    ("Todoist",         "todoist-electron",     "yay",     "✅",  "Office",          "Task manager"),
    ("Planner",         "planner",              "yay",     "📋",  "Office",          "Task planner (Todoist-like)"),
    ("GnuCash",         "gnucash",              "pacman",  "💰",  "Office",          "Personal finance manager"),
    ("GNOME Calendar",  "gnome-calendar",       "pacman",  "📅",  "Office",          "GNOME calendar"),
    ("GNOME Contacts",  "gnome-contacts",       "pacman",  "👤",  "Office",          "GNOME contacts"),

    # ── Network & VPN ──
    ("qBittorrent",     "qbittorrent",          "pacman",  "📥",  "Network",         "Torrent client"),
    ("Transmission",    "transmission-gtk",     "pacman",  "🔄",  "Network",         "Lightweight torrent client"),
    ("Deluge",          "deluge",               "pacman",  "🌊",  "Network",         "Feature-rich torrent client"),
    ("Wireshark",       "wireshark-qt",         "pacman",  "🦈",  "Network",         "Network traffic analyzer"),
    ("FileZilla",       "filezilla",            "pacman",  "📂",  "Network",         "FTP/SFTP client"),
    ("Nmap",            "nmap",                 "pacman",  "🔍",  "Network",         "Network scanner"),
    ("Wireguard",       "wireguard-tools",      "pacman",  "🔐",  "Network",         "Modern VPN"),
    ("OpenVPN",         "openvpn",              "pacman",  "🛡️",  "Network",         "VPN client"),
    ("ProtonVPN",       "protonvpn-gui",        "yay",     "🔏",  "Network",         "Secure VPN by Proton"),
    ("NordVPN",         "nordvpn-bin",          "yay",     "🌍",  "Network",         "Popular VPN — NordVPN"),
    ("Mullvad VPN",     "mullvad-vpn-bin",      "yay",     "🟡",  "Network",         "Private Mullvad VPN"),
    ("Remmina",         "remmina",              "pacman",  "🖥️",  "Network",         "RDP/VNC/SSH client"),
    ("AnyDesk",         "anydesk-bin",          "yay",     "🔴",  "Network",         "Remote desktop — AnyDesk"),
    ("RustDesk",        "rustdesk-bin",         "yay",     "🟧",  "Network",         "Open-source remote desktop"),
    ("Syncthing",       "syncthing",            "pacman",  "🔃",  "Network",         "P2P file synchronization"),
    ("Nextcloud",       "nextcloud-client",     "pacman",  "☁️",  "Network",         "Nextcloud cloud client"),
    ("Insomnia",        "insomnia-bin",         "yay",     "🟣",  "Network",         "REST/GraphQL API testing"),
    ("Postman",         "postman-bin",          "yay",     "🟠",  "Network",         "Popular API client"),
    ("Angry IP Scanner","ipscan",               "yay",     "😡",  "Network",         "Fast network IP scanner"),
    ("Etcher",          "balena-etcher",        "yay",     "💿",  "Network",         "Flash images to USB/SD"),

    # ── Virtualization & Containers ──
    ("VirtualBox",      "virtualbox",           "pacman",  "📦",  "Virtualization",  "Oracle virtual machines"),
    ("Virt-Manager",    "virt-manager",         "pacman",  "🖥️",  "Virtualization",  "KVM/QEMU manager"),
    ("Docker",          "docker",               "pacman",  "🐳",  "Virtualization",  "Application containers"),
    ("Podman",          "podman",               "pacman",  "🦭",  "Virtualization",  "Rootless containers"),
    ("Distrobox",       "distrobox",            "pacman",  "📤",  "Virtualization",  "Other distros in a container"),
    ("GNOME Boxes",     "gnome-boxes",          "pacman",  "📦",  "Virtualization",  "Simple GNOME virtual machines"),
    ("Lazydocker",      "lazydocker",           "pacman",  "🐳",  "Virtualization",  "TUI for Docker management"),
    ("Portainer",       "portainer-bin",        "yay",     "🚢",  "Virtualization",  "Web GUI for Docker"),
    ("Docker Compose",  "docker-compose",       "pacman",  "🐙",  "Virtualization",  "Container orchestration"),

    # ── Files & Managers ──
    ("Thunar",          "thunar",               "pacman",  "📁",  "Files",           "Lightweight file manager (XFCE)"),
    ("Dolphin",         "dolphin",              "pacman",  "🐬",  "Files",           "KDE file manager"),
    ("Nemo",            "nemo",                 "pacman",  "🗂️",  "Files",           "Cinnamon file manager"),
    ("Nautilus",        "nautilus",             "pacman",  "📂",  "Files",           "GNOME file manager (Files)"),
    ("PCManFM",         "pcmanfm",              "pacman",  "📁",  "Files",           "Ultra-lightweight file manager"),
    ("Ranger",          "ranger",               "pacman",  "🌲",  "Files",           "Terminal file manager"),
    ("Yazi",            "yazi",                 "pacman",  "🦆",  "Files",           "Blazing fast terminal file manager"),
    ("Double Commander","doublecmd-qt6",        "pacman",  "📂",  "Files",           "Dual-pane file manager"),
    ("Krusader",        "krusader",             "pacman",  "⚔️",  "Files",           "Advanced KDE dual-pane manager"),
    ("Midnight Cmd",    "mc",                   "pacman",  "🌙",  "Files",           "Midnight Commander — terminal classic"),
    ("7-Zip",           "7zip",                 "pacman",  "📦",  "Files",           "7z/zip/rar archiver"),
    ("Ark",             "ark",                  "pacman",  "📦",  "Files",           "KDE archive manager"),
    ("File Roller",     "file-roller",          "pacman",  "📦",  "Files",           "GNOME archive manager"),

    # ── Downloads & Torrents ──
    ("yt-dlp",          "yt-dlp",               "pacman",  "⬇️",  "Downloads",       "Download videos from YouTube etc."),
    ("Motrix",          "motrix-bin",           "yay",     "🟦",  "Downloads",       "Full-featured download manager"),
    ("Parabolic",       "parabolic",            "yay",     "⬇️",  "Downloads",       "Beautiful GNOME video downloader"),
    ("JDownloader",     "jdownloader2",         "yay",     "📦",  "Downloads",       "File download manager"),
    ("Persepolis",      "persepolis",           "yay",     "🔽",  "Downloads",       "GUI for aria2 — download manager"),
    ("Aria2",           "aria2",                "pacman",  "⬇️",  "Downloads",       "Ultra-light CLI download manager"),
    ("Wget",            "wget",                 "pacman",  "📥",  "Downloads",       "Classic HTTP/FTP downloader"),
    ("Curl",            "curl",                 "pacman",  "🔗",  "Downloads",       "Versatile URL data transfer"),
    ("Video Downloader","video-downloader",     "yay",     "📹",  "Downloads",       "GUI for downloading YouTube videos"),
    ("Parabolic",       "parabolic",            "yay",     "⬇️",  "Downloads",       "Beautiful GNOME video downloader"),
    ("Motrix",          "motrix-bin",           "yay",     "🟦",  "Downloads",       "Full-featured download manager"),
    ("Fragments",       "fragments",            "pacman",  "🧩",  "Downloads",       "GNOME BitTorrent client"),

    # ── Appearance & Customization ──
    ("Latte Dock",      "latte-dock",           "pacman",  "☕",  "Appearance",      "Elegant KDE dock"),
    ("Plank",           "plank",                "pacman",  "🔲",  "Appearance",      "Simple dock (macOS-like)"),
    ("Conky",           "conky",                "pacman",  "📊",  "Appearance",      "Desktop system widget"),
    ("Variety",         "variety",              "pacman",  "🖼️",  "Appearance",      "Automatic wallpaper changer"),
    ("Papirus Icons",   "papirus-icon-theme",   "pacman",  "🎨",  "Appearance",      "Beautiful Papirus icon set"),
    ("Nordic Theme",    "nordic-theme",         "yay",     "❄️",  "Appearance",      "Dark Nordic GTK theme"),
    ("Dracula Theme",   "dracula-gtk-theme-git","yay",     "🧛",  "Appearance",      "Popular Dracula theme"),
    ("Catppuccin GTK",  "catppuccin-gtk-theme-mocha","yay","🐱",  "Appearance",      "Pastel Catppuccin theme"),
    ("Nwg-look",        "nwg-look",             "pacman",  "👀",  "Appearance",      "GTK config for Wayland/Sway"),
    ("Kvantum",         "kvantum",              "pacman",  "🎨",  "Appearance",      "Qt theme manager"),
    ("Wallpaper Engine","linux-wallpaperengine-git","yay",  "🌄",  "Appearance",      "Animated wallpapers (Steam)"),
    ("Hyprpaper",       "hyprpaper",            "pacman",  "🖼️",  "Appearance",      "Wallpapers for Hyprland"),
    ("Waybar",          "waybar",               "pacman",  "📊",  "Appearance",      "Wayland status bar"),
    ("Polybar",         "polybar",              "pacman",  "📊",  "Appearance",      "Customizable X11 status bar"),
    ("Rofi",            "rofi",                 "pacman",  "🔍",  "Appearance",      "App launcher (dmenu replacement)"),
    ("Wofi",            "wofi",                 "pacman",  "🔍",  "Appearance",      "Wayland app launcher"),

    # ── Programming & DevTools ──
    ("Git",             "git",                  "pacman",  "📦",  "DevTools",        "Version control system"),
    ("GitHub CLI",      "github-cli",           "pacman",  "🐙",  "DevTools",        "Official GitHub CLI"),
    ("GitKraken",       "gitkraken",            "yay",     "🐙",  "DevTools",        "Beautiful Git GUI client"),
    ("Lazygit",         "lazygit",              "pacman",  "💤",  "DevTools",        "TUI for Git — fast and simple"),
    ("Python",          "python",               "pacman",  "🐍",  "DevTools",        "Python programming language"),
    ("Node.js",         "nodejs",               "pacman",  "🟩",  "DevTools",        "JavaScript runtime"),
    ("Rust",            "rust",                 "pacman",  "🦀",  "DevTools",        "Rust programming language"),
    ("Go",              "go",                   "pacman",  "🔵",  "DevTools",        "Go programming language"),
    ("GCC",             "gcc",                  "pacman",  "🔧",  "DevTools",        "C/C++ compiler"),
    ("CMake",           "cmake",                "pacman",  "🔨",  "DevTools",        "Project build system"),
    ("Meson",           "meson",                "pacman",  "🔧",  "DevTools",        "Modern build system"),
    ("DBeaver",         "dbeaver",              "pacman",  "🗄️",  "DevTools",        "Universal database client"),
    ("Beekeeper Studio","beekeeper-studio-bin", "yay",     "🐝",  "DevTools",        "Beautiful database GUI"),
    ("Bruno",           "bruno-bin",            "yay",     "🟤",  "DevTools",        "Open-source Postman alternative"),
    ("Meld",            "meld",                 "pacman",  "🔀",  "DevTools",        "File comparison tool"),
    ("Ghidra",          "ghidra",               "pacman",  "🔍",  "DevTools",        "Reverse engineering (NSA)"),

    # ── Social Media & Content ──
    ("Freetube",        "freetube-bin",         "yay",     "📺",  "Social",          "Private YouTube client"),
    ("NewPipe",         "newpipe-bin",          "yay",     "🟠",  "Social",          "Ad-free YouTube (Android bridge)"),
    ("Newsflash",       "newsflash",            "pacman",  "📰",  "Social",          "GNOME RSS reader"),
    ("Akregator",       "akregator",            "pacman",  "📰",  "Social",          "KDE RSS reader"),
    ("Cawbird",         "cawbird",              "yay",     "🐦",  "Social",          "Twitter client"),
    ("Tuba",            "tuba",                 "pacman",  "🐘",  "Social",          "GNOME Mastodon client"),
    ("Reddit",          "redlib",               "yay",     "🟠",  "Social",          "Private Reddit frontend"),

    # ── NO INTERESING ──
    ("Protontricks",    "protontricks",         "pacman",  "🔧",  "NO INTERESING",   "Load components for Wine/Proton games"),
    ("Winetricks",      "winetricks",           "pacman",  "🍷",  "NO INTERESING",   "Windows component installer for Wine"),
    ("DosBox",          "dosbox",               "pacman",  "💾",  "NO INTERESING",   "DOS emulator — retro games"),
    ("ScummVM",         "scummvm",              "pacman",  "🎮",  "NO INTERESING",   "Adventure game virtual machine"),
    ("GameHub",         "gamehub",              "yay",     "🕹️",  "NO INTERESING",   "Unified game & mod launcher"),
    ("Conky",           "conky",                "pacman",  "📊",  "NO INTERESING",   "System overlay and debugger"),
]

# Categories in display order
APP_CATEGORIES = [
    "Messengers", "Browsers", "Music", "Video", "Audio",
    "Graphics", "Games", "Code Editors", "DevTools",
    "System", "Terminal", "Office", "Network",
    "Virtualization", "Files", "Downloads", "Appearance", "Social", "NO INTERESING"
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
            self.btn.setText("Remove")
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
            self.btn.setText("Install")
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
        self._search.setPlaceholderText("🔍  Search apps...")
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
        label = "Installing" if action == "install" else "Removing"
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
