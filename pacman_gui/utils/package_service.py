"""
YayHub - Package Service
Facade for all package-related operations
"""

import logging
from typing import List, Optional, Dict, Callable
from .package_manager import PackageManager, Package
from .cache_manager import CacheManager
from .classifier import PackageClassifier


logger = logging.getLogger(__name__)


class PackageService:
    """High-level service for package operations"""

    def __init__(self):
        """Initialize service with all managers"""
        self.package_manager = PackageManager()
        self.cache_manager = CacheManager()
        self.classifier = PackageClassifier()

    def get_all_packages_with_categories(self, use_cache: bool = True) -> List[Package]:
        """
        Get all packages with categories assigned
        
        Args:
            use_cache: Whether to use cache if available
            
        Returns:
            List of Package objects with category attribute
        """
        logger.info("Loading packages with categories...")
        
        # Try cache first
        if use_cache and self.cache_manager.is_cache_valid():
            packages = self.cache_manager.load_packages()
            if packages:
                logger.info(f"Loaded {len(packages)} packages from cache")
                return packages
        
        # Load from system
        logger.info("Loading packages from system...")
        packages = self.package_manager.get_all_packages()
        
        # Classify packages
        logger.info("Classifying packages...")
        for pkg in packages:
            category = self.classifier.get_category(pkg)
            pkg.category = category
        
        # Save to cache
        self.cache_manager.save_packages(packages)
        
        logger.info(f"Loaded and classified {len(packages)} packages")
        return packages

    def get_packages_by_category(self, category: str) -> List[Package]:
        """Get packages filtered by category"""
        return self.cache_manager.get_packages_by_category(category)

    def get_category_counts(self) -> Dict[str, int]:
        """Get package count for each category"""
        counts = self.cache_manager.get_category_counts()
        
        # Add update count (check for available updates)
        updates = self.package_manager.check_updates()
        counts['Updates'] = len(updates)
        
        return counts

    def search_packages(self, query: str, packages: List[Package]) -> List[Package]:
        """
        Search packages by query
        
        Args:
            query: Search string
            packages: List of packages to search in
            
        Returns:
            Filtered list of packages
        """
        if not query:
            return packages
        
        query_lower = query.lower()
        results = []
        
        for pkg in packages:
            if (query_lower in pkg.name.lower() or 
                query_lower in pkg.description.lower()):
                results.append(pkg)
        
        logger.info(f"Search '{query}' returned {len(results)} results")
        return results

    def install_package(self, package: Package, callback: Optional[Callable] = None) -> tuple[bool, str]:
        """
        Install a package
        
        Args:
            package: Package to install
            callback: Optional callback for progress updates
            
        Returns:
            (success, output_message)
        """
        is_aur = package.repo.lower() == 'aur'
        
        if callback:
            return self.package_manager.install_package_with_callback(
                package.name, is_aur, callback
            )
        else:
            return self.package_manager.install_package(package.name, is_aur)

    def remove_package(self, package: Package) -> tuple[bool, str]:
        """
        Remove a package
        
        Returns:
            (success, output_message)
        """
        return self.package_manager.remove_package(package.name)

    def get_package_details(self, package: Package) -> Optional[str]:
        """Get detailed information about a package"""
        is_aur = package.repo.lower() == 'aur'
        return self.package_manager.get_package_details(package.name, is_aur)

    def check_updates(self) -> List[Package]:
        """Check for available package updates"""
        return self.package_manager.check_updates()

    def refresh_packages(self) -> List[Package]:
        """Force refresh all packages from system"""
        logger.info("Refreshing packages...")
        self.cache_manager.clear_cache()
        self.classifier.clear_cache()
        return self.get_all_packages_with_categories(use_cache=False)

    def is_package_installed(self, package_name: str) -> bool:
        """Check if a package is installed"""
        return self.package_manager.is_installed(package_name)

    def refresh_installed_packages(self):
        """Refresh the list of installed packages"""
        self.package_manager.refresh_installed_packages()

    def get_repo_display_name(self, repo: str) -> str:
        """Get human-friendly repository name"""
        return self.classifier.get_repo_display_name(repo)

    def get_all_categories(self) -> List[str]:
        """Get list of all available categories"""
        return self.classifier.get_all_categories()
