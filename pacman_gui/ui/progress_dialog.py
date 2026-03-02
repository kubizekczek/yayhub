"""
Progress Dialog - Shows installation/removal progress
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTextEdit,
    QPushButton, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


logger = logging.getLogger(__name__)


class InstallProgressDialog(QDialog):
    """Dialog showing package installation/removal progress"""

    def __init__(self, package_name: str, operation: str = "Installing", parent=None):
        super().__init__(parent)
        self.package_name = package_name
        self.operation = operation
        self.is_completed = False
        self._setup_ui()

    def _setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle(f"{self.operation} Package")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Title
        title_label = QLabel(f"{self.operation} {self.package_name}")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title_label.setFont(font)
        layout.addWidget(title_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Initializing...")
        layout.addWidget(self.status_label)

        # Log output
        log_label = QLabel("Output:")
        layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("monospace", 10))
        layout.addWidget(self.log_text)

        # Close button (initially disabled)
        self.close_button = QPushButton("Close")
        self.close_button.setEnabled(False)
        self.close_button.clicked.connect(self.accept)
        layout.addWidget(self.close_button)

    def append_output(self, text: str):
        """Append text to log output"""
        self.log_text.append(text.rstrip())
        
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def set_status(self, status: str):
        """Update status label"""
        self.status_label.setText(status)

    def set_completed(self, success: bool):
        """Mark operation as completed"""
        self.is_completed = True
        
        if success:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
            self.status_label.setText(f"✓ {self.operation} completed successfully!")
            self.status_label.setStyleSheet("color: #50fa7b; font-weight: bold;")
        else:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
            self.status_label.setText(f"✗ {self.operation} failed!")
            self.status_label.setStyleSheet("color: #ff5555; font-weight: bold;")
        
        self.close_button.setEnabled(True)
        
        # Auto-close after successful installation
        if success:
            QTimer.singleShot(2000, self.accept)

    def closeEvent(self, event):
        """Handle close event"""
        if not self.is_completed:
            # Don't allow closing during operation
            event.ignore()
        else:
            event.accept()
