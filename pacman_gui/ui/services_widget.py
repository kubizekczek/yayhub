"""
YayHub — System Services Manager
List, start, stop, enable, disable systemd services.
"""

import logging
import subprocess
from typing import List, Dict
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor

logger = logging.getLogger(__name__)


class ServiceLoaderThread(QThread):
    """Load systemd services in the background."""
    services_loaded = pyqtSignal(list)

    def run(self):
        try:
            # Get all services with their status
            r = subprocess.run(
                ['systemctl', 'list-unit-files', '--type=service', '--no-pager', '--no-legend'],
                capture_output=True, text=True, timeout=15
            )
            services = []
            for line in r.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    name = parts[0].replace('.service', '')
                    state = parts[1]  # enabled, disabled, static, masked
                    services.append({'name': name, 'state': state})

            # Get running status
            r2 = subprocess.run(
                ['systemctl', 'list-units', '--type=service', '--no-pager', '--no-legend'],
                capture_output=True, text=True, timeout=15
            )
            running = set()
            for line in r2.stdout.strip().split('\n'):
                if 'running' in line.lower():
                    parts = line.split()
                    if parts:
                        name = parts[0].replace('.service', '')
                        running.add(name)

            for s in services:
                s['running'] = s['name'] in running

            self.services_loaded.emit(services)
        except Exception as e:
            logger.error(f"Failed to load services: {e}")
            self.services_loaded.emit([])


class ServiceActionThread(QThread):
    """Run a systemctl action."""
    finished = pyqtSignal(bool, str)

    def __init__(self, service_name, action):
        super().__init__()
        self.service_name = service_name
        self.action = action  # start, stop, restart, enable, disable

    def run(self):
        try:
            cmd = ['sudo', 'systemctl', self.action, self.service_name]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if r.returncode == 0:
                self.finished.emit(True, f"{self.action} {self.service_name}: OK")
            else:
                self.finished.emit(False, r.stderr or r.stdout)
        except Exception as e:
            self.finished.emit(False, str(e))


def _svc_btn(text, bg, fg, hover):
    btn = QPushButton(text)
    btn.setFixedHeight(26)
    btn.setMinimumWidth(60)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: {bg}; color: {fg};
            border: none; border-radius: 5px;
            font-size: 11px; font-weight: 600;
            padding: 2px 10px;
        }}
        QPushButton:hover {{ background: {hover}; }}
    """)
    return btn


class ServicesWidget(QWidget):
    """System services management view."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._services: List[Dict] = []
        self._thread = None
        self._action_thread = None
        self._build()
        self._load()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)

        # Search
        search_row = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText("🔍  Szukaj usług...")
        self._search.setFixedHeight(38)
        self._search.setStyleSheet("""
            QLineEdit {
                background: #1e1e2e; color: #e8e8e8;
                border: 1px solid #3a3a50; border-radius: 8px;
                padding: 0 14px; font-size: 13px;
            }
            QLineEdit:focus { border-color: #6c71c4; }
        """)
        self._search.textChanged.connect(self._apply_filter)
        search_row.addWidget(self._search)

        refresh_btn = QPushButton("Odśwież")
        refresh_btn.setFixedHeight(38)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: #2a2a3e; color: #ddd;
                border: 1px solid #3a3a50; border-radius: 8px;
                font-size: 13px; padding: 0 16px;
            }
            QPushButton:hover { background: #3a3a4e; border-color: #6c71c4; }
        """)
        refresh_btn.clicked.connect(self._load)
        search_row.addWidget(refresh_btn)
        lay.addLayout(search_row)

        # Info
        self._info = QLabel("Ładowanie usług...")
        self._info.setStyleSheet("color: #888; font-size: 12px;")
        lay.addWidget(self._info)

        # Table
        self.tbl = QTableWidget()
        self.tbl.setColumnCount(5)
        self.tbl.setHorizontalHeaderLabels(["Usługa", "Stan", "Status", "Autostart", "Akcje"])
        h = self.tbl.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        h.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.tbl.setColumnWidth(1, 100)
        self.tbl.setColumnWidth(2, 100)
        self.tbl.setColumnWidth(3, 100)
        self.tbl.setColumnWidth(4, 260)
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.verticalHeader().setDefaultSectionSize(38)
        self.tbl.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.setShowGrid(False)
        self.tbl.setSortingEnabled(True)
        self.tbl.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e2e;
                alternate-background-color: #23233a;
                border: 1px solid #2a2a3e;
                border-radius: 8px;
                font-size: 13px;
            }
            QTableWidget::item {
                color: #e8e8e8;
                padding: 8px 12px;
                border-bottom: 1px solid #28283e;
            }
            QTableWidget::item:selected {
                background: #6c71c4;
                color: #ffffff;
            }
            QHeaderView::section {
                background: #252535;
                color: #b8b8c0;
                border: none;
                border-bottom: 2px solid #6c71c4;
                border-right: 1px solid #2a2a3e;
                padding: 10px 12px;
                font-size: 12px;
                font-weight: 600;
            }
        """)
        lay.addWidget(self.tbl, stretch=1)

    def _load(self):
        self._info.setText("Ładowanie usług...")
        self._thread = ServiceLoaderThread()
        self._thread.services_loaded.connect(self._on_loaded)
        self._thread.start()

    def _on_loaded(self, services):
        self._services = services
        self._apply_filter()

    def _apply_filter(self):
        q = self._search.text().lower() if self._search.text() else ""
        filtered = self._services
        if q:
            filtered = [s for s in filtered if q in s['name'].lower()]

        self.tbl.setSortingEnabled(False)
        self.tbl.setRowCount(len(filtered))

        for row, svc in enumerate(filtered):
            # Name
            name_item = QTableWidgetItem(svc['name'])
            name_item.setData(Qt.ItemDataRole.UserRole, svc['name'])
            self.tbl.setItem(row, 0, name_item)

            # Running status
            running = svc.get('running', False)
            run_item = QTableWidgetItem("🟢 Działa" if running else "⚫ Zatrzymana")
            run_item.setForeground(QColor("#50fa7b") if running else QColor("#888"))
            self.tbl.setItem(row, 1, run_item)

            # State
            state = svc.get('state', '')
            state_colors = {
                'enabled': '#50fa7b', 'disabled': '#888',
                'static': '#8be9fd', 'masked': '#ff5555'
            }
            state_item = QTableWidgetItem(state)
            state_item.setForeground(QColor(state_colors.get(state, '#888')))
            self.tbl.setItem(row, 2, state_item)

            # Autostart
            is_enabled = state == 'enabled'
            auto_item = QTableWidgetItem("✅ Tak" if is_enabled else "❌ Nie")
            self.tbl.setItem(row, 3, auto_item)

            # Action buttons
            actions_w = QWidget()
            actions_l = QHBoxLayout(actions_w)
            actions_l.setContentsMargins(4, 2, 4, 2)
            actions_l.setSpacing(4)

            name = svc['name']

            if running:
                stop_btn = _svc_btn("Stop", "#ff5555", "#fff", "#ff6e6e")
                stop_btn.clicked.connect(lambda _, n=name: self._do_action(n, "stop"))
                actions_l.addWidget(stop_btn)

                restart_btn = _svc_btn("Restart", "#f1fa8c", "#111", "#f5fc9a")
                restart_btn.clicked.connect(lambda _, n=name: self._do_action(n, "restart"))
                actions_l.addWidget(restart_btn)
            else:
                start_btn = _svc_btn("Start", "#50fa7b", "#111", "#69ffab")
                start_btn.clicked.connect(lambda _, n=name: self._do_action(n, "start"))
                actions_l.addWidget(start_btn)

            if is_enabled:
                dis_btn = _svc_btn("Disable", "#bd93f9", "#fff", "#caa4fa")
                dis_btn.clicked.connect(lambda _, n=name: self._do_action(n, "disable"))
                actions_l.addWidget(dis_btn)
            elif state not in ('static', 'masked'):
                en_btn = _svc_btn("Enable", "#6c71c4", "#fff", "#7c81d4")
                en_btn.clicked.connect(lambda _, n=name: self._do_action(n, "enable"))
                actions_l.addWidget(en_btn)

            self.tbl.setCellWidget(row, 4, actions_w)

        self.tbl.setSortingEnabled(True)
        self._info.setText(f"{len(filtered)} usług" + (f" (filtr: {q})" if q else ""))

    def _do_action(self, service_name, action):
        self._info.setText(f"{action} {service_name}...")
        self._action_thread = ServiceActionThread(service_name, action)

        def done(ok, msg):
            if ok:
                self._info.setText(f"✅ {action} {service_name} — OK")
            else:
                self._info.setText(f"❌ {action} {service_name} — błąd")
                QMessageBox.warning(self, "Błąd", f"{action} {service_name} nie powiodło się:\n{msg}")
            QTimer.singleShot(500, self._load)

        self._action_thread.finished.connect(done)
        self._action_thread.start()
