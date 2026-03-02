"""
Package Classifier - Categorizes packages based on name and metadata
"""

import logging
import re
from typing import Optional, Dict
from .package_manager import Package


logger = logging.getLogger(__name__)


class PackageClassifier:
    """Classifies packages into user-friendly categories"""

    # Category definitions
    CATEGORIES = {
        'System': ['systemd', 'base', 'linux', 'kernel', 'grub', 'boot', 'firmware', 'udev'],
        'Development': ['git', 'gcc', 'clang', 'cmake', 'make', 'python', 'rust', 'go', 'node', 'npm', 
                       'java', 'jdk', 'maven', 'gradle', 'docker', 'podman', 'kubernetes', 'vscode',
                       'code', 'vim', 'neovim', 'emacs', 'eclipse', 'intellij', 'android-studio'],
        'Graphics': ['gimp', 'inkscape', 'blender', 'krita', 'darktable', 'rawtherapee', 'imagemagick',
                    'graphviz', 'dia', 'scribus', 'mypaint'],
        'Multimedia': ['vlc', 'ffmpeg', 'mpv', 'pipewire', 'pulseaudio', 'alsa', 'jack', 'audacity',
                      'obs', 'kdenlive', 'shotcut', 'handbrake', 'spotify', 'rhythmbox', 'clementine',
                      'cmus', 'mpd', 'ncmpcpp'],
        'Gaming': ['steam', 'lutris', 'wine', 'proton', 'gamemode', 'gamescope', 'mangohud',
                  'discord', 'teamspeak', 'mumble', 'minecraft', 'dolphin-emu', 'retroarch'],
        'Internet': ['firefox', 'chromium', 'chrome', 'brave', 'vivaldi', 'opera', 'qutebrowser',
                    'thunderbird', 'evolution', 'transmission', 'qbittorrent', 'wget', 'curl',
                    'filezilla', 'remmina', 'anydesk'],
        'Office': ['libreoffice', 'openoffice', 'calligra', 'abiword', 'gnumeric', 'evince',
                  'okular', 'zathura', 'calibre', 'scribus'],
        'Network': ['networkmanager', 'nm-connection', 'dhcp', 'bind', 'dnsmasq', 'openssh', 'ssh',
                   'openvpn', 'wireguard', 'iptables', 'nftables', 'firewalld', 'wireshark',
                   'nmap', 'tcpdump', 'netcat', 'rsync'],
        'Utilities': ['htop', 'btop', 'bashtop', 'ranger', 'mc', 'nnn', 'fzf', 'ripgrep', 'fd',
                     'bat', 'exa', 'procs', 'dust', 'duf', 'ncdu', 'tmux', 'screen', 'kitty',
                     'alacritty', 'terminator', 'gnome-terminal', 'konsole'],
        'Desktop Environment': ['gnome', 'kde', 'plasma', 'xfce', 'lxde', 'lxqt', 'mate', 'cinnamon',
                               'budgie', 'i3', 'sway', 'awesome', 'bspwm', 'dwm', 'xmonad'],
        'Drivers': ['nvidia', 'mesa', 'vulkan', 'amdgpu', 'intel', 'nouveau', 'xf86-video',
                   'libva', 'vdpau', 'opencl', 'cuda'],
        'Libraries': ['lib', 'glibc', 'libx', 'libgtk', 'libqt', 'libsdl', 'libgl', 'libpng',
                     'libjpeg', 'libxml', 'libcurl', 'libssl', 'libcrypto']
    }

    # Repository display names
    REPO_NAMES = {
        'aur': 'AUR (Community)',
        'core': 'System Core',
        'extra': 'Official',
        'multilib': 'Multilib (32-bit)',
        'community': 'Community',
        'testing': 'Testing',
        'multilib-testing': 'Multilib Testing'
    }

    def __init__(self):
        """Initialize classifier"""
        self._cache: Dict[str, str] = {}
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for faster matching"""
        self._patterns = {}
        for category, keywords in self.CATEGORIES.items():
            # Create regex pattern that matches any keyword
            pattern = '|'.join([re.escape(kw) for kw in keywords])
            self._patterns[category] = re.compile(f'({pattern})', re.IGNORECASE)

    def get_category(self, package: Package, detailed_info: Optional[str] = None) -> str:
        """
        Classify package into a category
        
        Args:
            package: Package object
            detailed_info: Optional output from pacman -Si or yay -Si
            
        Returns:
            Category name (e.g., 'Gaming', 'Development')
        """
        # Check cache first
        cache_key = f"{package.name}:{package.repo}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        category = self._classify_package(package, detailed_info)
        self._cache[cache_key] = category
        return category

    def _classify_package(self, package: Package, detailed_info: Optional[str]) -> str:
        """Internal classification logic"""
        name_lower = package.name.lower()
        desc_lower = package.description.lower()
        
        # Try to extract category from detailed info if available
        if detailed_info:
            category = self._extract_category_from_details(detailed_info)
            if category:
                return category

        # Check if package name matches any pattern
        for category, pattern in self._patterns.items():
            if pattern.search(name_lower) or pattern.search(desc_lower):
                return category

        # Special case: lib* packages
        if name_lower.startswith('lib'):
            return 'Libraries'

        # Special case: python/perl/ruby modules
        if any(name_lower.startswith(prefix) for prefix in ['python-', 'python2-', 'python3-', 
                                                              'perl-', 'ruby-', 'nodejs-']):
            return 'Development'

        # Special case: fonts
        if 'font' in name_lower or 'ttf-' in name_lower or name_lower.startswith('noto-'):
            return 'Fonts'

        # Special case: themes and icons
        if any(kw in name_lower for kw in ['theme', 'icon', 'cursor', 'gtk-engine']):
            return 'Themes & Icons'

        # Default category
        return 'Other'

    def _extract_category_from_details(self, details: str) -> Optional[str]:
        """Extract category from pacman -Si output"""
        try:
            for line in details.split('\n'):
                if line.startswith('Groups'):
                    groups = line.split(':', 1)[1].strip()
                    if groups and groups != 'None':
                        # Map pacman groups to our categories
                        group_lower = groups.lower()
                        if 'base' in group_lower or 'system' in group_lower:
                            return 'System'
                        elif 'xorg' in group_lower or 'wayland' in group_lower:
                            return 'Desktop Environment'
                        elif 'gnome' in group_lower or 'kde' in group_lower or 'plasma' in group_lower:
                            return 'Desktop Environment'
                        # Add more group mappings as needed
        except Exception as e:
            logger.debug(f"Failed to extract category from details: {e}")
        return None

    def get_repo_display_name(self, repo: str) -> str:
        """Get human-friendly repository name"""
        return self.REPO_NAMES.get(repo.lower(), repo.capitalize())

    def get_all_categories(self) -> list:
        """Get list of all available categories"""
        return ['All Packages', 'Installed', 'Updates'] + sorted(self.CATEGORIES.keys()) + ['Other', 'Fonts', 'Themes & Icons']

    def clear_cache(self):
        """Clear classification cache"""
        self._cache.clear()
        logger.info("Classification cache cleared")
