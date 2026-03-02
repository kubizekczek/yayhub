"""
YayHub — Main Window v4
Fast table with inline action buttons per row.
"""

import logging
from typing import List, Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStatusBar, QProgressBar,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QColor, QFontDatabase

from ..utils import PackageService, Package
from .search_widget import SearchWidget
from .categories_sidebar import CategoriesSidebar
from .progress_dialog import InstallProgressDialog
from .app_store_widget import AppStoreWidget
from .services_widget import ServicesWidget

logger = logging.getLogger(__name__)


# ── Threads ────────────────────────────────────────────────────────

class PackageLoaderThread(QThread):
    packages_loaded = pyqtSignal(list, dict)
    progress_update = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, svc, use_cache=True):
        super().__init__()
        self.svc, self.use_cache = svc, use_cache

    def run(self):
        try:
            self.progress_update.emit("Loading packages…")
            pkgs = self.svc.get_all_packages_with_categories(self.use_cache)
            self.progress_update.emit("Counting…")
            counts = self.svc.cache_manager.get_category_counts()
            self.packages_loaded.emit(pkgs, counts)
        except Exception as e:
            self.error_occurred.emit(str(e))


class ActionThread(QThread):
    finished = pyqtSignal(bool, str)
    output_line = pyqtSignal(str)

    def __init__(self, svc, pkg, action):
        super().__init__()
        self.svc, self.pkg, self.action = svc, pkg, action

    def run(self):
        try:
            if self.action == "install":
                ok, msg = self.svc.install_package(
                    self.pkg, callback=lambda l: self.output_line.emit(l))
            else:
                ok, msg = self.svc.remove_package(self.pkg)
                self.output_line.emit(msg)
            self.finished.emit(ok, msg)
        except Exception as e:
            self.finished.emit(False, str(e))


class UpdatesCheckThread(QThread):
    updates_checked = pyqtSignal(dict)  # package_name -> has_update

    def __init__(self, svc):
        super().__init__()
        self.svc = svc

    def run(self):
        try:
            updates_dict = {}
            updates = self.svc.package_manager.check_updates()
            update_names = set(pkg.name for pkg in updates)
            updates_dict = {name: name in update_names for name in self.svc.package_manager.installed_packages}
            self.updates_checked.emit(updates_dict)
        except Exception as e:
            logger.error(f"Failed to check updates: {e}")
            self.updates_checked.emit({})


class BrokenCheckThread(QThread):
    """Background thread to detect packages with missing/broken files."""
    broken_checked = pyqtSignal(list)  # list of dicts

    def __init__(self, svc):
        super().__init__()
        self.svc = svc

    def run(self):
        try:
            broken = self.svc.package_manager.check_broken_packages()
            self.broken_checked.emit(broken)
        except Exception as e:
            logger.error(f"Failed to check broken packages: {e}")
            self.broken_checked.emit([])


class FixBrokenThread(QThread):
    """Thread that reinstalls a broken package to fix it."""
    finished = pyqtSignal(bool, str, str)  # ok, msg, pkg_name
    output_line = pyqtSignal(str)

    def __init__(self, svc, pkg_name):
        super().__init__()
        self.svc = svc
        self.pkg_name = pkg_name

    def run(self):
        try:
            ok, msg = self.svc.package_manager.fix_broken_package(self.pkg_name)
            self.finished.emit(ok, msg, self.pkg_name)
        except Exception as e:
            self.finished.emit(False, str(e), self.pkg_name)


# ── Helper: make a styled action button for a table cell ──────────

def _make_action_button(text: str, bg: str, fg: str, hover_bg: str, press_bg: str) -> QPushButton:
    """Create a properly sized, styled button."""
    btn = QPushButton(text)
    btn.setFixedHeight(28)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: {bg};
            color: {fg};
            border: none;
            border-radius: 5px;
            font-weight: 600;
            font-size: 12px;
            padding: 4px 18px;
        }}
        QPushButton:hover {{
            background: {hover_bg};
        }}
        QPushButton:pressed {{
            background: {press_bg};
        }}
    """)
    return btn


# ── Main Window ────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    PAGE = 150  # rows per batch

    def __init__(self):
        super().__init__()
        self.setWindowTitle("YayHub")
        self.setGeometry(100, 100, 1400, 800)
        self.setMinimumSize(1000, 550)

        # Try a nicer system font
        for fam in ("Inter", "Cantarell", "Noto Sans", "Segoe UI"):
            if fam in QFontDatabase.families():
                self.setFont(QFont(fam, 10))
                break

        self.svc = PackageService()
        self.all_pkgs: List[Package] = []
        self.view_pkgs: List[Package] = []
        self.updates_available = {}  # pkg_name -> True/False
        self.broken_packages = []     # list of dicts from check_broken_packages
        self._shown = 0
        self.cat = "All Packages"
        self._loader = None
        self._act_thread = None
        self._updates_thread = None  # Keep reference to updates thread
        self._batch_update_queue = []
        self._batch_update_index = 0
        self._batch_update_dlg = None
        self._broken_thread = None
        self._fix_thread = None
        self._batch_fix_queue = []
        self._batch_fix_index = 0
        self._batch_fix_dlg = None

        # Special views
        self._app_store = None
        self._services = None
        self._current_view = "packages"  # packages | apps | services

        self._build()
        self._load(True)

    # ───────────────────────── UI ──────────────────────────────────

    def _build(self):
        root = QWidget()
        self.setCentralWidget(root)
        outer = QHBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # sidebar
        self.sidebar = CategoriesSidebar()
        self.sidebar.setFixedWidth(240)
        self.sidebar.category_selected.connect(self._on_cat)
        outer.addWidget(self.sidebar)

        # right panel
        rp = QVBoxLayout()
        rp.setContentsMargins(20, 16, 20, 12)
        rp.setSpacing(14)

        # ── Search and Actions (no header) ──
        tb = QHBoxLayout()
        tb.setSpacing(10)
        self.search = SearchWidget()
        self.search.search_changed.connect(self._on_search)
        tb.addWidget(self.search, stretch=3)

        for label, slot in [("Refresh", self._refresh), ("🔄 Update All", self._update_all), ("🔧 Fix All", self._fix_all)]:
            b = QPushButton(label)
            b.setFixedHeight(36)
            b.setMinimumWidth(85)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet("""
                QPushButton {
                    background: #2a2a3e;
                    color: #ddd;
                    border: 1px solid #3a3a50;
                    border-radius: 8px;
                    font-weight: 500;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: #3a3a4e;
                    border-color: #6c71c4;
                }
                QPushButton:pressed {
                    background: #252535;
                }
            """)
            if label == "🔄 Update All":
                b.setStyleSheet("""
                    QPushButton {
                        background: #50fa7b;
                        color: #000;
                        border: 1px solid #40e06b;
                        border-radius: 8px;
                        font-weight: 600;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background: #60ff8b;
                        border-color: #50fa7b;
                    }
                    QPushButton:pressed {
                        background: #40e06b;
                    }
                """)
            elif label == "🔧 Fix All":
                b.setStyleSheet("""
                    QPushButton {
                        background: #ff5555;
                        color: #fff;
                        border: 1px solid #e04040;
                        border-radius: 8px;
                        font-weight: 600;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background: #ff6e6e;
                        border-color: #ff5555;
                    }
                    QPushButton:pressed {
                        background: #e04040;
                    }
                """)
                self._fix_all_btn = b
            b.clicked.connect(slot)
            tb.addWidget(b)
        rp.addLayout(tb)

        # ── Loading overlay ──
        self.load_box = QWidget()
        ll = QVBoxLayout(self.load_box)
        ll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._ltitle = QLabel("Loading packages…")
        self._ltitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lf = QFont(); lf.setPointSize(15); lf.setBold(True)
        self._ltitle.setFont(lf)
        self._ltitle.setStyleSheet("color:#ccc;")
        ll.addWidget(self._ltitle)
        self._lsub = QLabel("Please wait…")
        self._lsub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lsub.setStyleSheet("color:#888; font-size:13px;")
        ll.addWidget(self._lsub)
        self.load_box.hide()
        rp.addWidget(self.load_box, stretch=1)

        # ── Table ──
        self.tbl = QTableWidget()
        self.tbl.setColumnCount(4)
        self.tbl.setHorizontalHeaderLabels(["Package", "Version", "Description", ""])

        h = self.tbl.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.tbl.setColumnWidth(0, 280)
        self.tbl.setColumnWidth(1, 180)
        self.tbl.setColumnWidth(3, 120)
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.verticalHeader().setDefaultSectionSize(38)
        self.tbl.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tbl.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.setShowGrid(False)
        self.tbl.setSortingEnabled(True)
        self.tbl.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Direct inline style so text is ALWAYS visible
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
                padding: 10px 12px;
                border-bottom: 1px solid #28283e;
            }
            QTableWidget::item:selected {
                background: #6c71c4;
                color: #ffffff;
            }
            QTableWidget::item:hover:!selected {
                background-color: #2a2a42;
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
            QHeaderView::section:hover {
                background: #2e2e45;
            }
        """)
        self.tbl.hide()
        rp.addWidget(self.tbl, stretch=1)

        # load-more
        self.more_btn = QPushButton("Show more packages")
        self.more_btn.setFixedHeight(36)
        self.more_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.more_btn.setStyleSheet("""
            QPushButton {
                background: #2a2a3e;
                color: #aaa;
                border: 1px solid #3a3a50;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #3a3a4e;
                color: #ddd;
                border-color: #6c71c4;
            }
        """)
        self.more_btn.hide()
        self.more_btn.clicked.connect(self._more)
        rp.addWidget(self.more_btn)

        # info bar
        self.info = QLabel("")
        self.info.setStyleSheet("color:#888; font-size:12px; padding:2px 0;")
        rp.addWidget(self.info)

        # ── App Store View (hidden by default) ──
        self._app_store = AppStoreWidget()
        self._app_store.hide()
        rp.addWidget(self._app_store, stretch=1)

        # ── Services View (hidden by default) ──
        self._services = ServicesWidget()
        self._services.hide()
        rp.addWidget(self._services, stretch=1)

        outer.addLayout(rp, stretch=1)

        # status bar
        sb = QStatusBar()
        self.setStatusBar(sb)
        self.sb = sb
        self.prog = QProgressBar()
        self.prog.setMaximumWidth(200)
        self.prog.hide()
        sb.addPermanentWidget(self.prog)

    # ───────────────────── Loading ─────────────────────────────────

    def _load(self, cache=True):
        self.tbl.hide()
        self.more_btn.hide()
        self.load_box.show()
        self._ltitle.setText("Loading packages…")
        self._lsub.setText("Please wait…")
        self.prog.show()
        self.prog.setRange(0, 0)

        self._loader = PackageLoaderThread(self.svc, cache)
        self._loader.packages_loaded.connect(self._loaded)
        self._loader.progress_update.connect(lambda m: (self.sb.showMessage(m), self._lsub.setText(m)))
        self._loader.error_occurred.connect(self._err)
        self._loader.start()

    def _loaded(self, pkgs, counts):
        self.all_pkgs = pkgs
        self.prog.hide()
        self.load_box.hide()
        self.tbl.show()
        self.sidebar.update_counts(counts)
        self._filter()
        self.sb.showMessage(f"Loaded {len(pkgs)} packages")
        
        # Check for updates in background
        self._check_updates()
        # Check for broken packages
        self._check_broken()

    def _err(self, e):
        self.prog.hide()
        self._ltitle.setText("Error loading packages")
        self._lsub.setText(e)

    def _refresh(self):
        self._load(False)

    def _check_updates(self):
        """Start a background thread to check for available updates"""
        self._updates_thread = UpdatesCheckThread(self.svc)
        self._updates_thread.updates_checked.connect(self._on_updates_checked)
        self._updates_thread.start()

    def _on_updates_checked(self, updates_dict: dict):
        """Handle the updates check results — rebuild visible table"""
        self.updates_available = updates_dict
        n_updates = sum(1 for v in updates_dict.values() if v)
        n_broken = len(self.broken_packages)
        parts = [f"Loaded {len(self.all_pkgs)} packages", f"{n_updates} updates"]
        if n_broken:
            parts.append(f"{n_broken} broken")
        self.sb.showMessage("  •  ".join(parts))
        # Rebuild the table so buttons reflect the new state
        self._filter()

    def _check_broken(self):
        """Start background thread to detect broken packages."""
        self._broken_thread = BrokenCheckThread(self.svc)
        self._broken_thread.broken_checked.connect(self._on_broken_checked)
        self._broken_thread.start()

    def _on_broken_checked(self, broken_list: list):
        """Handle results from broken packages check."""
        self.broken_packages = broken_list
        n_broken = len(broken_list)
        n_updates = sum(1 for v in self.updates_available.values() if v)
        parts = [f"Loaded {len(self.all_pkgs)} packages", f"{n_updates} updates"]
        if n_broken:
            parts.append(f"⚠ {n_broken} broken")
        self.sb.showMessage("  •  ".join(parts))
        # Update sidebar count for Broken
        broken_counts = dict(self.sidebar.counts) if self.sidebar.counts else {}
        broken_counts["Broken"] = n_broken
        self.sidebar.update_counts(broken_counts)
        # If currently viewing broken tab, refresh
        if self.cat == "Broken":
            self._filter()

    # ───────────────────── Filter ──────────────────────────────────

    def _on_cat(self, c):
        self.cat = c
        if c == "Apps":
            self._show_view("apps")
        elif c == "Services":
            self._show_view("services")
        elif c == "NO INTERESING":
            self._show_view("apps_niche")
        else:
            self._show_view("packages")
            self._filter()

    def _show_view(self, view):
        """Switch between packages table, app store and services views."""
        self._current_view = view

        # Hide everything first
        self.tbl.hide()
        self.more_btn.hide()
        self.info.hide()
        self.load_box.hide()
        self._app_store.hide()
        self._services.hide()
        # Show/hide search bar and action buttons based on view
        search_parent = self.search.parent()

        if view == "apps":
            self._app_store.show()
            self._app_store.refresh_installed()
            self._app_store._filter_category = None  # Show all categories
        elif view == "apps_niche":
            self._app_store.show()
            self._app_store.refresh_installed()
            self._app_store._filter_category = "NO INTERESING"  # Show only NO INTERESING
        elif view == "services":
            self._services.show()
        else:
            # packages
            self.tbl.show()
            self.info.show()

    def _on_search(self, _q):
        self._filter()

    def _filter(self):
        c = self.cat
        q = self.search.get_search_text().lower()

        ps = self.all_pkgs
        if c == "Installed":
            ps = [p for p in ps if p.installed]
        elif c == "Updates":
            ps = [p for p in ps if p.installed and self.updates_available.get(p.name, False)]
        elif c == "Broken":
            broken_names = {b['name'] for b in self.broken_packages}
            ps = [p for p in ps if p.name in broken_names]
        elif c not in ("All Packages", ""):
            ps = [p for p in ps if getattr(p, 'category', '') == c]
        if q:
            ps = [p for p in ps if q in p.name.lower() or q in p.description.lower()]

        self.view_pkgs = ps
        self._shown = 0
        self.tbl.setSortingEnabled(False)
        self.tbl.setRowCount(0)
        self._more()
        self.tbl.setSortingEnabled(True)
        self.info.setText(f"{len(ps)} packages")

    # ───────────────────── Fill rows ───────────────────────────────

    def _more(self):
        end = min(self._shown + self.PAGE, len(self.view_pkgs))
        batch = self.view_pkgs[self._shown:end]
        if not batch:
            self.more_btn.hide()
            return

        self.tbl.setSortingEnabled(False)
        sr = self.tbl.rowCount()
        self.tbl.setRowCount(sr + len(batch))

        for i, pkg in enumerate(batch):
            row = sr + i
            gidx = self._shown + i   # global index in view_pkgs

            # ── col 0: name  (+ repo tag) ──
            repo_tag = pkg.repo.upper() if pkg.repo else ""
            status_dot = "●" if pkg.installed else "○"
            dot_color = "#50fa7b" if pkg.installed else "#555"
            # We'll use rich display via just text
            display_name = f"{pkg.name}"
            it = QTableWidgetItem(display_name)
            it.setData(Qt.ItemDataRole.UserRole, gidx)
            self.tbl.setItem(row, 0, it)

            # ── col 1: version ──
            vt = QTableWidgetItem(pkg.version)
            self.tbl.setItem(row, 1, vt)

            # ── col 2: description ──
            desc = pkg.description[:100] if pkg.description else ""
            dt = QTableWidgetItem(desc)
            self.tbl.setItem(row, 2, dt)

            # ── col 3: action button (one per row) ──
            broken_names = {b['name'] for b in self.broken_packages}
            is_broken = pkg.name in broken_names
            has_update = self.updates_available.get(pkg.name, False) if pkg.installed else False

            if is_broken:
                # Broken package → red Fix button
                btn = _make_action_button("Fix", "#ff5555", "#fff", "#ff6e6e", "#e04040")
                btn.clicked.connect(lambda _c=False, idx=gidx: self._act_fix(idx))
            elif not pkg.installed:
                btn = _make_action_button("Install", "#6c71c4", "#fff", "#7c81d4", "#5c61b4")
                btn.clicked.connect(lambda _c=False, idx=gidx: self._act_install(idx))
            elif has_update:
                btn = _make_action_button("Update", "#50fa7b", "#111", "#69ffab", "#40e06b")
                btn.clicked.connect(lambda _c=False, idx=gidx: self._act_update(idx))
            else:
                btn = _make_action_button("Remove", "#444", "#aaa", "#555", "#333")
                btn.clicked.connect(lambda _c=False, idx=gidx: self._act_remove(idx))
            self.tbl.setCellWidget(row, 3, btn)

        self.tbl.setSortingEnabled(True)
        self._shown = end
        rem = len(self.view_pkgs) - self._shown
        self.more_btn.setVisible(rem > 0)
        if rem > 0:
            self.more_btn.setText(f"Show more ({rem} remaining)")

    # ───────────────────── Actions ─────────────────────────────────

    def _pkg_at(self, idx) -> Optional[Package]:
        if 0 <= idx < len(self.view_pkgs):
            return self.view_pkgs[idx]
        return None

    def _act_install(self, idx):
        pkg = self._pkg_at(idx)
        if pkg:
            self._run(pkg, "install")

    def _act_update(self, idx):
        pkg = self._pkg_at(idx)
        if pkg:
            self._run(pkg, "install")  # update == reinstall latest

    def _act_remove(self, idx):
        pkg = self._pkg_at(idx)
        if pkg:
            self._run(pkg, "remove")

    def _act_fix(self, idx):
        pkg = self._pkg_at(idx)
        if pkg:
            self._run_fix(pkg.name)

    def _run_fix(self, pkg_name):
        """Reinstall a single broken package."""
        dlg = InstallProgressDialog(pkg_name, "Fixing (reinstalling)", self)
        self._fix_thread = FixBrokenThread(self.svc, pkg_name)
        self._fix_thread.output_line.connect(dlg.append_output)

        def done(ok, msg, name):
            dlg.set_completed(ok)
            if ok:
                # Remove from broken list
                self.broken_packages = [b for b in self.broken_packages if b['name'] != name]
                broken_counts = dict(self.sidebar.counts) if self.sidebar.counts else {}
                broken_counts["Broken"] = len(self.broken_packages)
                self.sidebar.update_counts(broken_counts)
                QTimer.singleShot(300, self._filter)

        self._fix_thread.finished.connect(done)
        self._fix_thread.start()
        dlg.exec()

    def _fix_all(self):
        """Fix all broken packages by reinstalling them."""
        if not self.broken_packages:
            self.sb.showMessage("No broken packages found")
            return

        from PyQt6.QtWidgets import QMessageBox
        names = [b['name'] for b in self.broken_packages]
        result = QMessageBox.question(
            self,
            "Fix All Broken Packages",
            f"Reinstall {len(names)} broken packages?\n\n" +
            ", ".join(names[:8]) + ("..." if len(names) > 8 else ""),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if result != QMessageBox.StandardButton.Yes:
            return

        self._batch_fix_queue = list(names)
        self._batch_fix_index = 0
        self._batch_fix_dlg = InstallProgressDialog("Fix All", "Fixing broken packages...", self)
        self._batch_fix_dlg.show()
        self._process_batch_fix()

    def _process_batch_fix(self):
        """Process the next package in the batch fix queue."""
        if self._batch_fix_index >= len(self._batch_fix_queue):
            self._batch_fix_dlg.set_completed(True)
            self.sb.showMessage("All broken packages fixed!")
            # Re-check broken to confirm
            QTimer.singleShot(500, self._check_broken)
            QTimer.singleShot(500, self._filter)
            return

        pkg_name = self._batch_fix_queue[self._batch_fix_index]
        self._batch_fix_dlg.append_output(
            f"\n{'='*50}\n"
            f"[{self._batch_fix_index + 1}/{len(self._batch_fix_queue)}] Fixing {pkg_name}...\n"
            f"{'='*50}\n"
        )

        self._fix_thread = FixBrokenThread(self.svc, pkg_name)
        self._fix_thread.output_line.connect(self._batch_fix_dlg.append_output)

        def done(ok, msg, name):
            if ok:
                self.broken_packages = [b for b in self.broken_packages if b['name'] != name]
            self._batch_fix_index += 1
            QTimer.singleShot(100, self._process_batch_fix)

        self._fix_thread.finished.connect(done)
        self._fix_thread.start()

    def _update_all(self):
        """Update all packages with available updates"""
        updates = [p for p in self.all_pkgs 
                   if p.installed and self.updates_available.get(p.name, False)]
        
        if not updates:
            self.sb.showMessage("No updates available")
            return
        
        # Show confirmation dialog
        from PyQt6.QtWidgets import QMessageBox
        result = QMessageBox.question(
            self,
            "Update All Packages",
            f"Update {len(updates)} packages?\n\n" + ", ".join(p.name for p in updates[:5]) + 
            ("..." if len(updates) > 5 else ""),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result != QMessageBox.StandardButton.Yes:
            return
        
        # Run batch update
        self._batch_update_queue = updates
        self._batch_update_index = 0
        self._batch_update_dlg = InstallProgressDialog("Batch Update", "Updating all packages...", self)
        self._batch_update_dlg.show()
        self._process_batch_update()

    def _process_batch_update(self):
        """Process the next package in batch update queue"""
        if self._batch_update_index >= len(self._batch_update_queue):
            self._batch_update_dlg.set_completed(True)
            self.sb.showMessage("All updates completed!")
            QTimer.singleShot(500, self._filter)
            return
        
        pkg = self._batch_update_queue[self._batch_update_index]
        self._batch_update_dlg.append_output(
            f"\n{'='*50}\n"
            f"[{self._batch_update_index + 1}/{len(self._batch_update_queue)}] Updating {pkg.name}...\n"
            f"{'='*50}\n"
        )
        
        self._act_thread = ActionThread(self.svc, pkg, "install")
        self._act_thread.output_line.connect(self._batch_update_dlg.append_output)
        
        def done(ok, msg):
            if ok:
                pkg.installed = True
                self.svc.refresh_installed_packages()
                self.updates_available[pkg.name] = False
            self._batch_update_index += 1
            QTimer.singleShot(100, self._process_batch_update)
        
        self._act_thread.finished.connect(done)
        self._act_thread.start()

    def _run(self, pkg, action):
        label = "Installing" if action == "install" else "Removing"
        dlg = InstallProgressDialog(pkg.name, label, self)
        self._act_thread = ActionThread(self.svc, pkg, action)
        self._act_thread.output_line.connect(dlg.append_output)

        def done(ok, _msg):
            dlg.set_completed(ok)
            if ok:
                pkg.installed = (action == "install")
                self.svc.refresh_installed_packages()
                # Mark package as updated (no longer needs update)
                if action == "install":
                    self.updates_available[pkg.name] = False
                elif action == "remove":
                    self.updates_available[pkg.name] = False
                QTimer.singleShot(300, self._filter)

        self._act_thread.finished.connect(done)
        self._act_thread.start()
        dlg.exec()

    # ───────────────────── Lifecycle ───────────────────────────────

    def closeEvent(self, ev):
        for t in (self._loader, self._act_thread, self._updates_thread, self._broken_thread, self._fix_thread):
            if t and t.isRunning():
                t.quit()
                t.wait(2000)
        ev.accept()
