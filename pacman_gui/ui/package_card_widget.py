"""
Package Card Widget - Modern card-style display for a single package
"""

import logging
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QCursor

from ..utils import Package


logger = logging.getLogger(__name__)


class PackageCardWidget(QFrame):
    """Modern card widget for displaying a package"""

    # Signals
    install_clicked = pyqtSignal(Package)
    remove_clicked = pyqtSignal(Package)
    update_clicked = pyqtSignal(Package)
    details_clicked = pyqtSignal(Package)

    def __init__(self, package: Package, parent=None):
        super().__init__(parent)
        self.package = package
        self._setup_ui()

    def _setup_ui(self):
        """Setup card UI"""
        # Set frame properties
        self.setProperty("class", "package-card")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumHeight(100)
        self.setMaximumHeight(120)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(12)

        # Left side: Package info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        # Package name with repo icon
        name_layout = QHBoxLayout()
        name_layout.setSpacing(8)
        
        self.name_label = QLabel(self.package.name)
        font = QFont()
        font.setPointSize(13)
        font.setBold(True)
        self.name_label.setFont(font)
        name_layout.addWidget(self.name_label)

        # Repo badge
        self.repo_label = QLabel(self._get_repo_display())
        self.repo_label.setStyleSheet(self._get_repo_style())
        name_layout.addWidget(self.repo_label)

        # Status badge
        self.status_label = QLabel(self._get_status_text())
        self.status_label.setProperty("class", self._get_status_class())
        name_layout.addWidget(self.status_label)

        name_layout.addStretch()
        info_layout.addLayout(name_layout)

        # Version
        version_text = f"Version: {self.package.version}" if self.package.version else "Version: N/A"
        self.version_label = QLabel(version_text)
        font_small = QFont()
        font_small.setPointSize(10)
        self.version_label.setFont(font_small)
        self.version_label.setStyleSheet("color: #b0b0b0;")
        info_layout.addWidget(self.version_label)

        # Description (truncated)
        desc_text = self.package.description[:80] + "..." if len(self.package.description) > 80 else self.package.description
        self.desc_label = QLabel(desc_text)
        self.desc_label.setFont(font_small)
        self.desc_label.setStyleSheet("color: #b0b0b0;")
        self.desc_label.setWordWrap(True)
        info_layout.addWidget(self.desc_label)

        info_layout.addStretch()
        main_layout.addLayout(info_layout, stretch=3)

        # Right side: Action buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(8)

        # Install/Remove/Update button
        self.action_button = QPushButton(self._get_action_button_text())
        self.action_button.setProperty("class", self._get_action_button_class())
        self.action_button.setMinimumWidth(100)
        self.action_button.clicked.connect(self._on_action_clicked)
        button_layout.addWidget(self.action_button)

        # Details button
        self.details_button = QPushButton("Details")
        self.details_button.setMinimumWidth(100)
        self.details_button.clicked.connect(self._on_details_clicked)
        button_layout.addWidget(self.details_button)

        button_layout.addStretch()
        main_layout.addLayout(button_layout, stretch=1)

    def _get_repo_display(self) -> str:
        """Get display name for repository"""
        repo_map = {
            'aur': 'AUR',
            'core': 'Core',
            'extra': 'Extra',
            'multilib': 'Multilib'
        }
        return repo_map.get(self.package.repo.lower(), self.package.repo.upper())

    def _get_repo_style(self) -> str:
        """Get style for repo label"""
        if self.package.repo.lower() == 'aur':
            return """
                background-color: #8be9fd;
                color: #1e1e2e;
                border-radius: 6px;
                padding: 2px 6px;
                font-size: 10px;
                font-weight: 600;
            """
        else:
            return """
                background-color: #6c71c4;
                color: white;
                border-radius: 6px;
                padding: 2px 6px;
                font-size: 10px;
                font-weight: 600;
            """

    def _get_status_text(self) -> str:
        """Get status text"""
        if self.package.installed:
            return "Installed"
        else:
            return "Available"

    def _get_status_class(self) -> str:
        """Get status class for styling"""
        if self.package.installed:
            return "badge-installed"
        else:
            return "badge-available"

    def _get_action_button_text(self) -> str:
        """Get text for action button"""
        if self.package.installed:
            return "Remove"
        else:
            return "Install"

    def _get_action_button_class(self) -> str:
        """Get class for action button"""
        if self.package.installed:
            return "success"  # Green for installed/removable
        else:
            return "primary"  # Accent color for install

    def _on_action_clicked(self):
        """Handle action button click"""
        if self.package.installed:
            self.remove_clicked.emit(self.package)
        else:
            self.install_clicked.emit(self.package)

    def _on_details_clicked(self):
        """Handle details button click"""
        self.details_clicked.emit(self.package)

    def update_package(self, package: Package):
        """Update card with new package data"""
        self.package = package
        
        # Update labels
        self.name_label.setText(package.name)
        self.repo_label.setText(self._get_repo_display())
        self.repo_label.setStyleSheet(self._get_repo_style())
        self.status_label.setText(self._get_status_text())
        self.status_label.setProperty("class", self._get_status_class())
        
        version_text = f"Version: {package.version}" if package.version else "Version: N/A"
        self.version_label.setText(version_text)
        
        desc_text = package.description[:80] + "..." if len(package.description) > 80 else package.description
        self.desc_label.setText(desc_text)
        
        # Update button
        self.action_button.setText(self._get_action_button_text())
        self.action_button.setProperty("class", self._get_action_button_class())
        
        # Force style refresh
        self.style().unpolish(self.action_button)
        self.style().polish(self.action_button)
        self.style().unpolish(self.status_label)
        self.style().polish(self.status_label)
