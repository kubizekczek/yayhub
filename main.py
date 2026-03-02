#!/usr/bin/env python3
"""
YayHub - PyQt6 frontend for pacman and yay
Main entry point for the application
"""

import sys
import logging
import os
import subprocess
import threading

# Ensure we can import the pacman_gui package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def _sudo_keepalive(stop_event: threading.Event):
    """Background thread that refreshes sudo credentials every 60s"""
    while not stop_event.wait(60):
        try:
            subprocess.run(['sudo', '-v', '-n'], capture_output=True, timeout=5)
        except Exception:
            pass


def _acquire_sudo() -> bool:
    """Acquire sudo credentials, showing a graphical password dialog if needed."""
    # First check if we already have cached credentials
    try:
        r = subprocess.run(['sudo', '-v', '-n'], capture_output=True, timeout=5)
        if r.returncode == 0:
            return True
    except Exception:
        pass

    # No cached creds – show graphical password prompt
    from PyQt6.QtWidgets import QApplication, QInputDialog, QLineEdit, QMessageBox

    # Ensure QApplication exists for the dialog
    _app = QApplication.instance() or QApplication(sys.argv)

    for attempt in range(3):
        password, ok = QInputDialog.getText(
            None, "YayHub – Autoryzacja",
            "Podaj hasło sudo aby zarządzać pakietami:",
            QLineEdit.EchoMode.Password
        )
        if not ok:
            return False
        try:
            r = subprocess.run(
                ['sudo', '-S', '-v'],
                input=password + '\n',
                capture_output=True,
                text=True,
                timeout=10
            )
            if r.returncode == 0:
                return True
            QMessageBox.warning(None, "YayHub", "Nieprawidłowe hasło. Spróbuj ponownie.")
        except Exception as e:
            logger.error(f"sudo auth error: {e}")
            return False
    return False


def main():
    """Main application entry point"""

    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        from PyQt6.QtGui import QIcon
        from pacman_gui.ui import MainWindow
        from pacman_gui.ui.theme_manager import ThemeManager

        # Create application (or reuse from _acquire_sudo)
        app = QApplication.instance() or QApplication(sys.argv)

        # --- Acquire sudo once at startup ---
        if not _acquire_sudo():
            QMessageBox.critical(None, "YayHub", "Autoryzacja sudo nie powiodła się.\nAplikacja zostanie zamknięta.")
            sys.exit(1)

        # Keep sudo alive in background so the password isn't asked again
        _stop = threading.Event()
        _keepalive = threading.Thread(target=_sudo_keepalive, args=(_stop,), daemon=True)
        _keepalive.start()
        
        # Set application metadata
        app.setApplicationName("YayHub")
        app.setApplicationVersion("3.0.0")
        
        # Apply dark theme
        ThemeManager.apply_dark_theme(app)
        
        # Create main window
        window = MainWindow()
        window.show()
        
        # Run application
        sys.exit(app.exec())

    except ImportError as e:
        logger.error(f"Import error: {e}")
        print(f"Error: Missing dependencies. Please run: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        from PyQt6.QtWidgets import QMessageBox, QApplication
        app = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(None, "Fatal Error", f"An error occurred:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
