"""
YayHub - Theme Manager (v3.0)
"""

import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt


logger = logging.getLogger(__name__)


class ThemeManager:
    """Manages application themes and custom styles"""

    # Color scheme for dark mode
    DARK_COLORS = {
        'bg_primary': '#1e1e2e',       # Main background
        'bg_secondary': '#2a2a3e',     # Secondary background (cards, panels)
        'bg_hover': '#3a3a4e',         # Hover state
        'bg_selected': '#4a4a5e',      # Selected state
        'text_primary': '#e0e0e0',     # Main text
        'text_secondary': '#b0b0b0',   # Secondary text
        'text_disabled': '#707070',    # Disabled text
        'accent': '#6c71c4',           # Accent color (buttons, links)
        'success': '#50fa7b',          # Success/Installed (green)
        'info': '#8be9fd',             # Info/Available (blue)
        'warning': '#ffb86c',          # Warning/Update (orange)
        'error': '#ff5555',            # Error/Problem (red)
        'border': '#44475a',           # Borders
        'scrollbar': '#424252',        # Scrollbar
    }

    @classmethod
    def apply_dark_theme(cls, app: QApplication):
        """Apply dark theme to the application"""
        logger.info("Applying dark theme")

        # Set application style
        app.setStyle('Fusion')

        # Create dark palette
        palette = cls._create_dark_palette()
        app.setPalette(palette)

        # Apply custom stylesheet
        stylesheet = cls._get_dark_stylesheet()
        app.setStyleSheet(stylesheet)

    @classmethod
    def _create_dark_palette(cls) -> QPalette:
        """Create dark color palette"""
        palette = QPalette()
        
        # Window
        palette.setColor(QPalette.ColorRole.Window, QColor(cls.DARK_COLORS['bg_primary']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(cls.DARK_COLORS['text_primary']))
        
        # Base (input fields)
        palette.setColor(QPalette.ColorRole.Base, QColor(cls.DARK_COLORS['bg_secondary']))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(cls.DARK_COLORS['bg_hover']))
        palette.setColor(QPalette.ColorRole.Text, QColor(cls.DARK_COLORS['text_primary']))
        
        # Tooltips
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(cls.DARK_COLORS['bg_secondary']))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(cls.DARK_COLORS['text_primary']))
        
        # Buttons
        palette.setColor(QPalette.ColorRole.Button, QColor(cls.DARK_COLORS['bg_secondary']))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(cls.DARK_COLORS['text_primary']))
        
        # Bright text
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.white)
        
        # Links
        palette.setColor(QPalette.ColorRole.Link, QColor(cls.DARK_COLORS['accent']))
        
        # Highlight
        palette.setColor(QPalette.ColorRole.Highlight, QColor(cls.DARK_COLORS['accent']))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        
        # Disabled
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText,
                        QColor(cls.DARK_COLORS['text_disabled']))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text,
                        QColor(cls.DARK_COLORS['text_disabled']))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText,
                        QColor(cls.DARK_COLORS['text_disabled']))
        
        return palette

    @classmethod
    def _get_dark_stylesheet(cls) -> str:
        """Get custom dark theme stylesheet"""
        c = cls.DARK_COLORS
        
        return f"""
            /* Global */
            * {{
                outline: none;
            }}
            
            /* Main Window */
            QMainWindow {{
                background-color: {c['bg_primary']};
            }}
            
            /* Scroll Areas */
            QScrollArea {{
                background-color: {c['bg_primary']};
                border: none;
            }}
            
            /* Scroll Bars */
            QScrollBar:vertical {{
                background-color: {c['bg_secondary']};
                width: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {c['scrollbar']};
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {c['bg_hover']};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                background-color: {c['bg_secondary']};
                height: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {c['scrollbar']};
                border-radius: 6px;
                min-width: 20px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background-color: {c['bg_hover']};
            }}
            
            /* Line Edit (Search) */
            QLineEdit {{
                background-color: {c['bg_secondary']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                padding: 8px 12px;
                color: {c['text_primary']};
                font-size: 14px;
            }}
            
            QLineEdit:focus {{
                border: 1px solid {c['accent']};
            }}
            
            /* Buttons */
            QPushButton {{
                background-color: {c['bg_secondary']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                padding: 8px 16px;
                color: {c['text_primary']};
                font-size: 13px;
                font-weight: 500;
            }}
            
            QPushButton:hover {{
                background-color: {c['bg_hover']};
                border: 1px solid {c['accent']};
            }}
            
            QPushButton:pressed {{
                background-color: {c['bg_selected']};
            }}
            
            QPushButton:disabled {{
                background-color: {c['bg_secondary']};
                color: {c['text_disabled']};
                border: 1px solid {c['border']};
            }}
            
            /* Primary Button (Install, etc.) */
            QPushButton[class="primary"] {{
                background-color: {c['accent']};
                border: none;
                color: white;
                font-weight: 600;
            }}
            
            QPushButton[class="primary"]:hover {{
                background-color: #7c81d4;
            }}
            
            /* Success Button (Installed) */
            QPushButton[class="success"] {{
                background-color: {c['success']};
                border: none;
                color: {c['bg_primary']};
                font-weight: 600;
            }}
            
            QPushButton[class="success"]:hover {{
                background-color: #60ff8b;
            }}
            
            /* Warning Button (Update) */
            QPushButton[class="warning"] {{
                background-color: {c['warning']};
                border: none;
                color: {c['bg_primary']};
                font-weight: 600;
            }}
            
            QPushButton[class="warning"]:hover {{
                background-color: #ffc87c;
            }}
            
            /* Combo Box */
            QComboBox {{
                background-color: {c['bg_secondary']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                padding: 6px 12px;
                color: {c['text_primary']};
                font-size: 13px;
            }}
            
            QComboBox:hover {{
                border: 1px solid {c['accent']};
            }}
            
            QComboBox::drop-down {{
                border: none;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {c['bg_secondary']};
                border: 1px solid {c['border']};
                selection-background-color: {c['accent']};
                color: {c['text_primary']};
            }}
            
            /* Labels */
            QLabel {{
                color: {c['text_primary']};
            }}
            
            /* Status Bar */
            QStatusBar {{
                background-color: {c['bg_secondary']};
                color: {c['text_secondary']};
                border-top: 1px solid {c['border']};
            }}
            
            /* Text Edit */
            QTextEdit {{
                background-color: {c['bg_secondary']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                color: {c['text_primary']};
                padding: 8px;
                font-family: monospace;
                font-size: 12px;
            }}
            
            /* Splitter */
            QSplitter::handle {{
                background-color: {c['border']};
            }}
            
            QSplitter::handle:horizontal {{
                width: 1px;
            }}
            
            QSplitter::handle:vertical {{
                height: 1px;
            }}
            
            /* Progress Bar */
            QProgressBar {{
                background-color: {c['bg_secondary']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                text-align: center;
                color: {c['text_primary']};
                height: 20px;
            }}
            
            QProgressBar::chunk {{
                background-color: {c['accent']};
                border-radius: 7px;
            }}
            
            /* Package Card Widget */
            QFrame[class="package-card"] {{
                background-color: {c['bg_secondary']};
                border: 1px solid {c['border']};
                border-radius: 12px;
                padding: 12px;
            }}
            
            QFrame[class="package-card"]:hover {{
                background-color: {c['bg_hover']};
                border: 1px solid {c['accent']};
            }}
            
            /* Badge Labels */
            QLabel[class="badge-installed"] {{
                background-color: {c['success']};
                color: {c['bg_primary']};
                border-radius: 8px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: 600;
            }}
            
            QLabel[class="badge-available"] {{
                background-color: {c['info']};
                color: {c['bg_primary']};
                border-radius: 8px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: 600;
            }}
            
            QLabel[class="badge-update"] {{
                background-color: {c['warning']};
                color: {c['bg_primary']};
                border-radius: 8px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: 600;
            }}
        """

    @classmethod
    def get_color(cls, key: str) -> str:
        """Get color by key"""
        return cls.DARK_COLORS.get(key, '#ffffff')
