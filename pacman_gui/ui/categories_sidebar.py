"""
YayHub - Categories Sidebar (v3.0)
Readable, high-contrast category list.
"""

import logging
from typing import Dict
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QColor, QIcon

logger = logging.getLogger(__name__)

# (internal_name, emoji, label)
_CATS = [
    ("Apps",                "🛒", "Apps"),
    ("Services",            "🔧", "Services"),
    ("---sep1", "", ""),
    ("All Packages",        "📦", "All Packages"),
    ("Installed",           "✅", "Installed"),
    ("Updates",             "🔄", "Updates"),
    ("Broken",              "🔴", "Broken Files"),
    ("---", "", ""),
    ("System",              "⚙️",  "System"),
    ("Development",         "💻", "Development"),
    ("Graphics",            "🎨", "Graphics"),
    ("Multimedia",          "🎵", "Multimedia"),
    ("Gaming",              "🎮", "Gaming"),
    ("Internet",            "🌐", "Internet"),
    ("Office",              "📄", "Office"),
    ("Network",             "🔌", "Network"),
    ("Utilities",           "🛠️",  "Utilities"),
    ("Desktop Environment", "🖥️",  "Desktop Env"),
    ("Drivers",             "🔧", "Drivers"),
    ("Libraries",           "📚", "Libraries"),
    ("Fonts",               "🔤", "Fonts"),
    ("Themes & Icons",      "🎭", "Themes"),
    ("Other",               "📁", "Other"),
    ("---sep2", "", ""),
    ("NO INTERESING",       "🎲", "NO INTERESING"),
]


class CategoriesSidebar(QWidget):
    category_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.counts: Dict[str, int] = {}
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        
        # Simple dark background
        self.setStyleSheet("""
            QWidget {
                background: #191928;
                border-right: 1px solid #2a2a3e;
            }
        """)

        # Header with padding
        hdr = QWidget()
        hdr.setStyleSheet("background: transparent;")
        hl = QVBoxLayout(hdr)
        hl.setContentsMargins(16, 16, 16, 12)
        
        title = QLabel("Categories")
        f = QFont()
        f.setPointSize(14)
        f.setBold(True)
        title.setFont(f)
        title.setStyleSheet("color: #ffffff; padding-bottom: 6px; background: transparent;")
        hl.addWidget(title)
        lay.addWidget(hdr)

        # List container with padding
        list_container = QWidget()
        list_container.setStyleSheet("background: transparent;")
        lc = QVBoxLayout(list_container)
        lc.setContentsMargins(10, 0, 10, 10)
        
        self.list = QListWidget()
        self.list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                color: #ccc;
                background: transparent;
                border: none;
                border-radius: 6px;
                padding: 10px 14px;
                margin: 2px 0;
                font-size: 13px;
            }
            QListWidget::item:hover {
                background: #2a2a3e;
                color: #fff;
            }
            QListWidget::item:selected {
                background: #6c71c4;
                color: #ffffff;
                font-weight: 600;
            }
        """)
        self.list.itemClicked.connect(self._clicked)
        lc.addWidget(self.list)
        lay.addWidget(list_container)

        self._populate()

    def _populate(self):
        for key, emoji, label in _CATS:
            if key.startswith("---"):
                sep = QListWidgetItem()
                sep.setSizeHint(sep.sizeHint().__class__(0, 6))
                sep.setFlags(Qt.ItemFlag.NoItemFlags)
                self.list.addItem(sep)
                continue
            text = f"{emoji}  {label}"
            it = QListWidgetItem(text)
            it.setData(Qt.ItemDataRole.UserRole, key)
            font = QFont()
            font.setPointSize(12)
            it.setFont(font)
            self.list.addItem(it)
        self.list.setCurrentRow(0)

    def _clicked(self, item: QListWidgetItem):
        cat = item.data(Qt.ItemDataRole.UserRole)
        if cat:
            self.category_selected.emit(cat)

    def update_counts(self, counts: Dict[str, int]):
        self.counts = counts
        for i in range(self.list.count()):
            it = self.list.item(i)
            key = it.data(Qt.ItemDataRole.UserRole)
            if not key:
                continue
            # find original label
            for k, emoji, label in _CATS:
                if k == key:
                    c = counts.get(key, 0)
                    it.setText(f"{emoji}  {label}  ({c})" if c else f"{emoji}  {label}")
                    break

    def get_selected_category(self) -> str:
        cur = self.list.currentItem()
        return cur.data(Qt.ItemDataRole.UserRole) if cur else "All Packages"

    def set_selected_category(self, cat: str):
        for i in range(self.list.count()):
            it = self.list.item(i)
            if it.data(Qt.ItemDataRole.UserRole) == cat:
                self.list.setCurrentItem(it)
                break
