"""
YayHub - Cache Manager
Stores and retrieves package information from local SQLite database
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from .package_manager import Package


logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching of package lists using SQLite"""

    CACHE_DIR = Path.home() / '.cache' / 'yayhub'
    CACHE_FILE = CACHE_DIR / 'packages.db'
    CACHE_TIMEOUT = 3600  # 1 hour in seconds

    def __init__(self):
        """Initialize cache manager"""
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Cache directory: {self.CACHE_DIR}")
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database"""
        try:
            conn = sqlite3.connect(self.CACHE_FILE)
            cursor = conn.cursor()
            
            # Create packages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS packages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    repo TEXT NOT NULL,
                    version TEXT,
                    description TEXT,
                    category TEXT,
                    installed INTEGER DEFAULT 0,
                    size TEXT,
                    timestamp TEXT,
                    UNIQUE(name, repo)
                )
            ''')
            
            # Create index for faster queries
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_name ON packages(name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON packages(category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_installed ON packages(installed)')
            
            # Create metadata table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

    def save_packages(self, packages: List[Package]) -> bool:
        """Save packages to cache"""
        try:
            conn = sqlite3.connect(self.CACHE_FILE)
            cursor = conn.cursor()
            
            # Clear existing packages
            cursor.execute('DELETE FROM packages')
            
            # Insert packages
            for pkg in packages:
                cursor.execute('''
                    INSERT OR REPLACE INTO packages 
                    (name, repo, version, description, category, installed, size, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pkg.name,
                    pkg.repo,
                    pkg.version,
                    pkg.description,
                    getattr(pkg, 'category', 'Other'),
                    1 if pkg.installed else 0,
                    pkg.size,
                    datetime.now().isoformat()
                ))
            
            # Update metadata
            cursor.execute('''
                INSERT OR REPLACE INTO metadata (key, value)
                VALUES ('last_update', ?)
            ''', (datetime.now().isoformat(),))
            
            conn.commit()
            conn.close()
            logger.info(f"Saved {len(packages)} packages to cache")
            return True
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
            return False

    def load_packages(self) -> Optional[List[Package]]:
        """Load packages from cache"""
        try:
            if not self.CACHE_FILE.exists():
                logger.info("Cache file not found")
                return None
            
            # Check if cache is expired
            if not self.is_cache_valid():
                logger.info("Cache expired")
                return None
            
            conn = sqlite3.connect(self.CACHE_FILE)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name, repo, version, description, category, installed, size
                FROM packages
            ''')
            
            packages = []
            for row in cursor.fetchall():
                pkg = Package(
                    name=row[0],
                    repo=row[1],
                    version=row[2] or '',
                    description=row[3] or '',
                    installed=bool(row[5]),
                    size=row[6] or ''
                )
                # Add category as attribute
                pkg.category = row[4] or 'Other'
                packages.append(pkg)
            
            conn.close()
            logger.info(f"Loaded {len(packages)} packages from cache")
            return packages
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
            return None

    def get_packages_by_category(self, category: str) -> List[Package]:
        """Get packages filtered by category"""
        try:
            conn = sqlite3.connect(self.CACHE_FILE)
            cursor = conn.cursor()
            
            if category == 'All Packages':
                cursor.execute('SELECT name, repo, version, description, category, installed, size FROM packages')
            elif category == 'Installed':
                cursor.execute('SELECT name, repo, version, description, category, installed, size FROM packages WHERE installed = 1')
            elif category == 'Updates':
                # For now, just return installed packages - update checking will be implemented later
                cursor.execute('SELECT name, repo, version, description, category, installed, size FROM packages WHERE installed = 1')
            else:
                cursor.execute('SELECT name, repo, version, description, category, installed, size FROM packages WHERE category = ?', (category,))
            
            packages = []
            for row in cursor.fetchall():
                pkg = Package(
                    name=row[0],
                    repo=row[1],
                    version=row[2] or '',
                    description=row[3] or '',
                    installed=bool(row[5]),
                    size=row[6] or ''
                )
                pkg.category = row[4] or 'Other'
                packages.append(pkg)
            
            conn.close()
            return packages
        except Exception as e:
            logger.error(f"Failed to get packages by category: {e}")
            return []

    def get_category_counts(self) -> Dict[str, int]:
        """Get package count for each category"""
        try:
            conn = sqlite3.connect(self.CACHE_FILE)
            cursor = conn.cursor()
            
            counts = {}
            
            # All packages
            cursor.execute('SELECT COUNT(*) FROM packages')
            counts['All Packages'] = cursor.fetchone()[0]
            
            # Installed
            cursor.execute('SELECT COUNT(*) FROM packages WHERE installed = 1')
            counts['Installed'] = cursor.fetchone()[0]
            
            # Updates (placeholder - same as installed for now)
            counts['Updates'] = 0
            
            # By category
            cursor.execute('SELECT category, COUNT(*) FROM packages GROUP BY category')
            for row in cursor.fetchall():
                counts[row[0]] = row[1]
            
            conn.close()
            return counts
        except Exception as e:
            logger.error(f"Failed to get category counts: {e}")
            return {}

    def is_cache_valid(self) -> bool:
        """Check if cache exists and is valid"""
        if not self.CACHE_FILE.exists():
            return False
        
        try:
            conn = sqlite3.connect(self.CACHE_FILE)
            cursor = conn.cursor()
            
            cursor.execute('SELECT value FROM metadata WHERE key = "last_update"')
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return False
            
            timestamp = datetime.fromisoformat(result[0])
            age = (datetime.now() - timestamp).total_seconds()
            return age < self.CACHE_TIMEOUT
        except Exception as e:
            logger.error(f"Cache validation error: {e}")
            return False

    def clear_cache(self) -> bool:
        """Clear the cache"""
        try:
            if self.CACHE_FILE.exists():
                self.CACHE_FILE.unlink()
                logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False

    def get_cache_age(self) -> Optional[int]:
        """Get age of cache in seconds"""
        try:
            if not self.CACHE_FILE.exists():
                return None
            
            conn = sqlite3.connect(self.CACHE_FILE)
            cursor = conn.cursor()
            
            cursor.execute('SELECT value FROM metadata WHERE key = "last_update"')
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return None
            
            timestamp = datetime.fromisoformat(result[0])
            age = (datetime.now() - timestamp).total_seconds()
            return int(age)
        except Exception as e:
            logger.error(f"Failed to get cache age: {e}")
            return None

    def get_cache_package_count(self) -> Optional[int]:
        """Get number of packages in cache"""
        try:
            if not self.CACHE_FILE.exists():
                return None
            
            conn = sqlite3.connect(self.CACHE_FILE)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM packages')
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
        except Exception as e:
            logger.error(f"Failed to get package count: {e}")
            return None

