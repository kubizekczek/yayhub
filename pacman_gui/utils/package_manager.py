"""
YayHub - Package Manager
Wrapper for pacman and yay commands
"""

import subprocess
import json
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Repository(Enum):
    """Available package repositories"""
    CORE = "core"
    EXTRA = "extra"
    MULTILIB = "multilib"
    AUR = "aur"


@dataclass
class Package:
    """Package data class"""
    name: str
    repo: str
    version: str = ""
    description: str = ""
    installed: bool = False
    size: str = ""

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'repo': self.repo,
            'version': self.version,
            'description': self.description,
            'installed': self.installed,
            'size': self.size
        }


class PackageManager:
    """Wrapper for pacman and yay commands"""

    def __init__(self):
        self.installed_packages = set()
        self.aur_available = False
        self.descriptions_cache = {}  # name -> description
        self._check_aur_availability()
        self._load_installed_packages()
        self._load_descriptions()

    def _check_aur_availability(self) -> bool:
        """Check if yay is installed"""
        try:
            subprocess.run(
                ['which', 'yay'],
                capture_output=True,
                timeout=5,
                check=True
            )
            self.aur_available = True
            logger.info("yay found - AUR support enabled")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.aur_available = False
            logger.warning("yay not found - AUR support disabled")
            return False

    def _load_installed_packages(self) -> None:
        """Load list of installed packages"""
        try:
            result = subprocess.run(
                ['pacman', '-Q'],
                capture_output=True,
                text=True,
                timeout=10,
                check=True
            )
            self.installed_packages = set(
                line.split()[0] for line in result.stdout.strip().split('\n')
                if line.strip()
            )
            logger.info(f"Loaded {len(self.installed_packages)} installed packages")
        except Exception as e:
            logger.error(f"Failed to load installed packages: {e}")
            self.installed_packages = set()

    def _load_descriptions(self) -> None:
        """Load package descriptions using expac"""
        try:
            # Try expac first for all sync database packages
            result = subprocess.run(
                ['expac', '-S', '%n\t%d'],
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )
            for line in result.stdout.strip().split('\n'):
                if '\t' in line:
                    name, desc = line.split('\t', 1)
                    self.descriptions_cache[name.strip()] = desc.strip()
            logger.info(f"Loaded {len(self.descriptions_cache)} package descriptions via expac")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.warning(f"expac not available, descriptions will be limited: {e}")
            # Fallback: load descriptions for installed packages only via pacman -Qi
            try:
                for pkg_name in self.installed_packages:
                    result = subprocess.run(
                        ['pacman', '-Qi', pkg_name],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if line.startswith('Description'):
                                desc = line.split(':', 1)[1].strip()
                                self.descriptions_cache[pkg_name] = desc
                                break
                logger.info(f"Loaded {len(self.descriptions_cache)} descriptions via fallback")
            except Exception as fallback_err:
                logger.error(f"Failed to load descriptions: {fallback_err}")

    def get_official_packages(self) -> List[Package]:
        """Get packages from official repositories (core, extra, multilib)"""
        packages = []
        try:
            result = subprocess.run(
                ['pacman', '-Sl'],
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )
            
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                
                parts = line.split(None, 3)
                if len(parts) < 3:
                    continue
                
                repo = parts[0]
                name = parts[1]
                version = parts[2]
                # Get description from cache (loaded via expac)
                description = self.descriptions_cache.get(name, "")
                
                # Only include main repos
                if repo in ['core', 'extra', 'multilib']:
                    pkg = Package(
                        name=name,
                        repo=repo,
                        version=version,
                        description=description,
                        installed=name in self.installed_packages
                    )
                    packages.append(pkg)
            
            logger.info(f"Retrieved {len(packages)} official packages")
            return packages
        except Exception as e:
            logger.error(f"Failed to get official packages: {e}")
            return []

    def get_aur_packages(self) -> List[Package]:
        """Get packages from AUR"""
        if not self.aur_available:
            logger.warning("yay not available - AUR packages cannot be retrieved")
            return []
        
        packages = []
        try:
            result = subprocess.run(
                ['yay', '-Sl', 'aur'],
                capture_output=True,
                text=True,
                timeout=60,
                check=True
            )
            
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                
                parts = line.split(None, 3)
                if len(parts) < 3:
                    continue
                
                repo = parts[0]
                name = parts[1]
                version = parts[2]
                # Get description from cache or leave empty for AUR
                description = self.descriptions_cache.get(name, "")
                
                if repo == 'aur':
                    pkg = Package(
                        name=name,
                        repo='aur',
                        version=version,
                        description=description,
                        installed=name in self.installed_packages
                    )
                    packages.append(pkg)
            
            logger.info(f"Retrieved {len(packages)} AUR packages")
            return packages
        except Exception as e:
            logger.error(f"Failed to get AUR packages: {e}")
            return []

    def get_all_packages(self) -> List[Package]:
        """Get all available packages (official + AUR)"""
        packages = self.get_official_packages()
        packages.extend(self.get_aur_packages())
        return packages

    def install_package(self, package_name: str, is_aur: bool = False) -> Tuple[bool, str]:
        """
        Install a package
        Returns: (success, output)
        """
        try:
            if is_aur:
                if not self.aur_available:
                    return False, "yay is not installed"
                # yay should NOT run with sudo - it handles elevation internally
                cmd = ['yay', '-S', '--noconfirm', package_name]
            else:
                cmd = ['sudo', 'pacman', '-S', '--noconfirm', package_name]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                self.installed_packages.add(package_name)
                logger.info(f"Successfully installed {package_name}")
                return True, result.stdout
            else:
                logger.error(f"Failed to install {package_name}: {result.stderr}")
                return False, result.stderr
        except Exception as e:
            logger.error(f"Installation error: {e}")
            return False, str(e)

    def remove_package(self, package_name: str) -> Tuple[bool, str]:
        """
        Remove a package
        Returns: (success, output)
        """
        try:
            cmd = ['sudo', 'pacman', '-R', '--noconfirm', package_name]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                self.installed_packages.discard(package_name)
                logger.info(f"Successfully removed {package_name}")
                return True, result.stdout
            else:
                logger.error(f"Failed to remove {package_name}: {result.stderr}")
                return False, result.stderr
        except Exception as e:
            logger.error(f"Removal error: {e}")
            return False, str(e)

    def is_installed(self, package_name: str) -> bool:
        """Check if a package is installed"""
        return package_name in self.installed_packages

    def refresh_installed_packages(self) -> None:
        """Refresh the list of installed packages"""
        self._load_installed_packages()

    def get_package_info(self, package_name: str) -> Optional[Dict]:
        """Get detailed information about a package"""
        try:
            if self.is_installed(package_name):
                result = subprocess.run(
                    ['pacman', '-Qi', package_name],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=True
                )
                info = self._parse_pacman_info(result.stdout)
                return info
            return None
        except Exception as e:
            logger.error(f"Failed to get package info: {e}")
            return None

    @staticmethod
    def _parse_pacman_info(info_text: str) -> Dict:
        """Parse pacman -Qi output"""
        info = {}
        for line in info_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                info[key.strip().lower()] = value.strip()
        return info

    def get_package_details(self, package_name: str, is_aur: bool = False) -> Optional[str]:
        """
        Get detailed package information from pacman -Si or yay -Si
        Returns full output text for parsing
        """
        try:
            if is_aur and self.aur_available:
                cmd = ['yay', '-Si', package_name]
            else:
                cmd = ['pacman', '-Si', package_name]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15,
                check=True
            )
            return result.stdout
        except Exception as e:
            logger.error(f"Failed to get package details: {e}")
            return None

    def check_updates(self) -> List[Package]:
        """
        Check for available updates
        Returns list of packages that have updates available
        """
        updates = []
        try:
            # Check official repos
            result = subprocess.run(
                ['pacman', '-Qu'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                
                parts = line.split()
                if len(parts) >= 4:
                    name = parts[0]
                    current_version = parts[1]
                    new_version = parts[3]
                    
                    pkg = Package(
                        name=name,
                        repo='update',
                        version=new_version,
                        description=f"Update available: {current_version} → {new_version}",
                        installed=True
                    )
                    updates.append(pkg)
            
            # Check AUR if available
            if self.aur_available:
                try:
                    result = subprocess.run(
                        ['yay', '-Qua'],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    for line in result.stdout.strip().split('\n'):
                        if not line.strip():
                            continue
                        
                        parts = line.split()
                        if len(parts) >= 4:
                            name = parts[0]
                            current_version = parts[1]
                            new_version = parts[3]
                            
                            pkg = Package(
                                name=name,
                                repo='aur',
                                version=new_version,
                                description=f"Update available: {current_version} → {new_version}",
                                installed=True
                            )
                            updates.append(pkg)
                except Exception as e:
                    logger.warning(f"Failed to check AUR updates: {e}")
            
            logger.info(f"Found {len(updates)} updates")
            return updates
        except Exception as e:
            logger.error(f"Failed to check updates: {e}")
            return []

    def check_broken_packages(self) -> List[Dict]:
        """
        Check for packages with missing or modified files using pacman -Qk.
        Returns list of dicts: {name, missing_files, total_files, details}
        """
        broken = []
        try:
            result = subprocess.run(
                ['pacman', '-Qk'],
                capture_output=True,
                text=True,
                timeout=120
            )
            # pacman -Qk prints warnings for missing files to stderr,
            # and also returns non-zero if any files are missing.
            # Parse both stdout and stderr for missing file info
            output = result.stdout + '\n' + result.stderr
            for line in output.strip().split('\n'):
                if not line.strip():
                    continue
                # Lines with problems look like:
                # package: /path/to/file (No such file or directory)
                # Summary lines: package: N total files, M missing files
                if 'brak pliku' in line.lower() or 'missing file' in line.lower() or 'no such file' in line.lower():
                    # This is a specific missing file line
                    continue
                if 'missing' in line.lower() or 'brak' in line.lower():
                    # Summary line: "pkgname: X total files, Y missing files"
                    parts = line.split(':')
                    if len(parts) >= 2:
                        pkg_name = parts[0].strip().split()[-1] if ' ' in parts[0] else parts[0].strip()
                        detail = ':'.join(parts[1:]).strip()
                        # Extract missing count
                        import re
                        m = re.search(r'(\d+)\s+(?:missing|brak)', detail, re.IGNORECASE)
                        missing = int(m.group(1)) if m else 1
                        if missing > 0:
                            broken.append({
                                'name': pkg_name,
                                'missing_files': missing,
                                'details': detail
                            })
            logger.info(f"Found {len(broken)} broken packages")
            return broken
        except Exception as e:
            logger.error(f"Failed to check broken packages: {e}")
            return []

    def fix_broken_package(self, package_name: str) -> Tuple[bool, str]:
        """Reinstall a broken package to restore its files."""
        try:
            cmd = ['sudo', 'pacman', '-S', '--noconfirm', package_name]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                logger.info(f"Successfully fixed {package_name}")
                return True, result.stdout
            else:
                logger.error(f"Failed to fix {package_name}: {result.stderr}")
                return False, result.stderr
        except Exception as e:
            logger.error(f"Fix error: {e}")
            return False, str(e)

    def install_package_with_callback(self, package_name: str, is_aur: bool, 
                                     callback=None) -> Tuple[bool, str]:
        """
        Install package with progress callback
        callback(line: str) is called for each output line
        """
        try:
            if is_aur:
                if not self.aur_available:
                    return False, "yay is not installed"
                # yay should NOT run with sudo - it handles elevation internally
                cmd = ['yay', '-S', '--noconfirm', package_name]
            else:
                cmd = ['sudo', 'pacman', '-S', '--noconfirm', package_name]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            output_lines = []
            for line in iter(process.stdout.readline, ''):
                if line:
                    output_lines.append(line)
                    if callback:
                        callback(line)
            
            process.wait(timeout=300)
            
            if process.returncode == 0:
                self.installed_packages.add(package_name)
                logger.info(f"Successfully installed {package_name}")
                return True, ''.join(output_lines)
            else:
                logger.error(f"Failed to install {package_name}")
                return False, ''.join(output_lines)
        except Exception as e:
            logger.error(f"Installation error: {e}")
            return False, str(e)

