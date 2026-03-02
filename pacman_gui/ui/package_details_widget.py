"""
Package Details Widget - Show detailed information about selected package
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QScrollArea
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from ..utils import Package


class PackageDetailsWidget(QWidget):
    """Widget showing package details"""

    install_clicked = pyqtSignal(Package)
    remove_clicked = pyqtSignal(Package)

    def __init__(self):
        super().__init__()
        self.current_package: Package = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup details widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Package name and repo
        self.name_label = QLabel("No package selected")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.name_label.setFont(font)
        content_layout.addWidget(self.name_label)

        # Repository and version info
        self.info_label = QLabel("")
        content_layout.addWidget(self.info_label)

        # Description
        content_layout.addWidget(QLabel("Description:"))
        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        self.description_text.setMaximumHeight(100)
        content_layout.addWidget(self.description_text)

        # Additional info
        content_layout.addWidget(QLabel("Details:"))
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(100)
        content_layout.addWidget(self.details_text)

        # Installation log/output
        content_layout.addWidget(QLabel("Log:"))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(100)
        content_layout.addWidget(self.log_text)

        content_layout.addStretch()
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        # Action buttons
        button_layout = QHBoxLayout()

        self.install_btn = QPushButton("Install")
        self.install_btn.clicked.connect(self._on_install_clicked)
        button_layout.addWidget(self.install_btn)

        self.remove_btn = QPushButton("Remove")
        self.remove_btn.clicked.connect(self._on_remove_clicked)
        button_layout.addWidget(self.remove_btn)

        layout.addLayout(button_layout)

        # Initial state
        self._update_ui_state()

    def show_package(self, package: Package):
        """Show package details"""
        self.current_package = package

        self.name_label.setText(f"{package.name}")
        self.info_label.setText(
            f"Repository: {package.repo} | Version: {package.version} | "
            f"Status: {'Installed' if package.installed else 'Available'}"
        )
        self.description_text.setText(package.description)

        # Show basic details
        details = f"Package: {package.name}\n"
        details += f"Repository: {package.repo}\n"
        details += f"Version: {package.version}\n"
        details += f"Installed: {'Yes' if package.installed else 'No'}\n"
        if package.size:
            details += f"Size: {package.size}\n"
        self.details_text.setText(details)

        self.log_text.clear()

        self._update_ui_state()

    def _update_ui_state(self):
        """Update button states based on package status"""
        if not self.current_package:
            self.install_btn.setEnabled(False)
            self.remove_btn.setEnabled(False)
        else:
            self.install_btn.setEnabled(not self.current_package.installed)
            self.remove_btn.setEnabled(self.current_package.installed)

    def _on_install_clicked(self):
        """Handle install button click"""
        if self.current_package:
            self.install_clicked.emit(self.current_package)

    def _on_remove_clicked(self):
        """Handle remove button click"""
        if self.current_package:
            self.remove_clicked.emit(self.current_package)

    def show_installation_output(self, output: str):
        """Show installation output in log"""
        self.log_text.append(output)

    def show_installation_error(self, error: str):
        """Show installation error"""
        self.log_text.append(f"ERROR: {error}")
