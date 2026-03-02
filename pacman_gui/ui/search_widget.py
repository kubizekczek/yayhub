"""
YayHub - Search Widget
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
from PyQt6.QtCore import pyqtSignal


class SearchWidget(QWidget):
    """Search input widget with live search capability"""

    search_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """Setup search widget UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Search input with modern style
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search packages…")
        self.search_input.setFixedHeight(38)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a40, stop:1 #252535);
                color: #e8e8e8;
                border: 1px solid #44475a;
                border-radius: 10px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #6c71c4;
                background: #2e2e48;
            }
            QLineEdit::placeholder {
                color: #666;
            }
        """)
        self.search_input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.search_input)

    def _on_text_changed(self, text: str):
        """Handle text changed"""
        self.search_changed.emit(text)

    def _clear_search(self):
        """Clear search input"""
        self.search_input.clear()

    def clear_search(self):
        """Public: clear search input"""
        self.search_input.clear()

    def get_search_text(self) -> str:
        """Get current search text"""
        return self.search_input.text()

    def set_search_text(self, text: str):
        """Set search text"""
        self.search_input.setText(text)
