"""
Package List Widget - Display packages in a table/list format
"""

from typing import List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor, QFont

from ..utils import PackageManager, Package


class PackageListWidget(QWidget):
    """Widget displaying list of packages"""

    package_selected = pyqtSignal(Package)

    def __init__(self, package_manager: PackageManager):
        super().__init__()
        self.package_manager = package_manager
        self.packages: List[Package] = []
        self.package_map = {}  # Map row to package

        self._setup_ui()

    def _setup_ui(self):
        """Setup package list UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Package table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Name", "Repository", "Version", "Description", "Status"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table)

    def set_packages(self, packages: List[Package]):
        """Set packages to display"""
        self.packages = packages
        self._populate_table()

    def _populate_table(self):
        """Populate table with packages"""
        self.table.setRowCount(len(self.packages))
        self.package_map.clear()

        for row, package in enumerate(self.packages):
            # Name
            name_item = QTableWidgetItem(package.name)
            if package.installed:
                font = QFont()
                font.setBold(True)
                name_item.setFont(font)
            self.table.setItem(row, 0, name_item)

            # Repository
            repo_item = QTableWidgetItem(package.repo)
            if package.repo == 'aur':
                repo_item.setBackground(QColor(100, 150, 200))
            self.table.setItem(row, 1, repo_item)

            # Version
            version_item = QTableWidgetItem(package.version)
            self.table.setItem(row, 2, version_item)

            # Description
            desc_item = QTableWidgetItem(package.description[:50])
            desc_item.setToolTip(package.description)
            self.table.setItem(row, 3, desc_item)

            # Status
            status_item = QTableWidgetItem(
                "Installed" if package.installed else "Available"
            )
            if package.installed:
                status_item.setBackground(QColor(100, 200, 100))
            else:
                status_item.setBackground(QColor(200, 100, 100))
            self.table.setItem(row, 4, status_item)

            self.package_map[row] = package

    def _on_selection_changed(self):
        """Handle package selection"""
        selected_rows = self.table.selectedIndexes()
        if selected_rows:
            row = selected_rows[0].row()
            if row in self.package_map:
                package = self.package_map[row]
                self.package_selected.emit(package)

    def get_selected_package(self) -> Package:
        """Get currently selected package"""
        selected_rows = self.table.selectedIndexes()
        if selected_rows:
            row = selected_rows[0].row()
            return self.package_map.get(row)
        return None
