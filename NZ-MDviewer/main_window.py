"""
Main window for NZ-MDviewer.
BalkanMDViewer class + main() entry point.
"""
import sys
import os
import json
import tempfile
import re
from pathlib import Path

import markdown
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTreeView, QToolBar, QStatusBar, QLineEdit,
    QFileDialog, QFileSystemModel, QMessageBox, QMenu, QDialog, QLabel,
    QGroupBox, QCheckBox, QComboBox, QDoubleSpinBox,
    QPushButton, QApplication, QSpinBox, QFrame,
    QPlainTextEdit, QInputDialog, QColorDialog,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtGui import (
    QAction, QKeySequence, QDesktopServices, QColor,
    QIcon, QPixmap, QCursor, QTextCursor, QShortcut,
)
from PySide6.QtCore import (
    Qt, QUrl, QTimer, QDir, QFileSystemWatcher,
)

import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("_pkg_init", os.path.join(os.path.dirname(os.path.abspath(__file__)), "__init__.py"))
_m = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_m)
VERSION = _m.VERSION; APP_NAME = _m.APP_NAME
del _ilu, _spec, _m

from translations import _t, set_lang
from editor import MarkdownEditor
from web import BalkanMDPage, ContentContainer
from styles import ucitaj_css
from settings_mgr import ucitaj_postavke, sacuvaj_postavke, SETTINGS_FILE


class BalkanMDViewer(QMainWindow):
    """
    Glavni prozor aplikacije.
    Lijevo fajlovi, desno fancy renderovan markdown.
    Jednostavno ko pasulj.
    """

    def __init__(self, pocetni_fajl=None):
        super().__init__()

        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        self.resize(1400, 800)

        # Trenutno otvoreni fajl
        self.trenutni_fajl = None

        # Navigaciona historija
        self.istorija = []
        self.istorija_index = -1

        # Edit mode state
        self.edit_mode = False
        self.edit_paused_watcher = False

        # Split mode state
        self.split_mode = False
        self.split_splitter = None
        self.split_timer = QTimer(self)
        self.split_timer.setSingleShot(True)
        self.split_timer.timeout.connect(self._split_preview_update)
        self._split_text_changed_conn = None

        # Omogući drag & drop
        self.setAcceptDrops(True)

        # File watcher za auto-reload
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.fileChanged.connect(self.on_file_changed)

        # Debounce timer za reload (da ne refresha 100 puta u sekundi)
        self.reload_timer = QTimer(self)
        self.reload_timer.setSingleShot(True)
        self.reload_timer.timeout.connect(self.reload_trenutni_fajl)

        # Glavni widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Meni bar
        self.kreiraj_meni()

        # Toolbar
        self.kreiraj_toolbar()

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(_t("status_ready"))

        # Word count label in status bar
        self.word_count_label = QLabel()
        self.word_count_label.hide()
        self.status_bar.addPermanentWidget(self.word_count_label)

        # --- GLAVNI SPLITTER ---
        self.glavni_splitter = QSplitter(Qt.Horizontal)
        self.glavni_splitter.setHandleWidth(6)
        self.glavni_splitter.setChildrenCollapsible(False)
        self.glavni_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #30363d;
                margin: 0px 2px;
            }
            QSplitter::handle:hover {
                background-color: #58a6ff;
            }
            QSplitter::handle:pressed {
                background-color: #1f6feb;
            }
        """)

        # === LIJEVA STRANA: LISTA FAJLOVA ===
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.homePath())
        self.file_model.setNameFilters(["*.md", "*.markdown", "*.mdown", "*.txt"])
        self.file_model.setNameFilterDisables(False)

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_model)
        self.tree_view.setRootIndex(self.file_model.index(QDir.homePath()))

        # Sakrij nepotrebne kolone
        for i in range(1, 4):
            self.tree_view.setColumnHidden(i, True)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setAnimated(True)
        self.tree_view.setIndentation(20)
        self.tree_view.setSortingEnabled(True)

        # Stil za drvo fajlova
        self.tree_view.setStyleSheet("""
            QTreeView {
                background-color: #0d1117;
                color: #c9d1d9;
                border: none;
                font-size: 13px;
            }
            QTreeView::item {
                padding: 4px;
            }
            QTreeView::item:hover {
                background: #161b22;
            }
            QTreeView::item:selected {
                background: #1f6feb;
                color: white;
            }
        """)

        # Klik i dvostruki klik na fajl
        self.tree_view.clicked.connect(self.klik_na_fajl)

        # === DESNA STRANA: CONTENT CONTAINER (Preview + Editor) ===
        self.pregledac = QWebEngineView()
        self.pregledac.setZoomFactor(1.0)

        # Custom page za interceptanje linkova
        self.custom_page = BalkanMDPage(self.pregledac)
        self.custom_page.md_link_clicked.connect(lambda path: self.ucitaj_fajl(path))
        self.pregledac.setPage(self.custom_page)

        # Context menu za zoom
        self.pregledac.setContextMenuPolicy(Qt.CustomContextMenu)
        self.pregledac.customContextMenuRequested.connect(self.show_context_menu)

        # Editor panel (toolbar + editor)
        self.editor_panel = QWidget()
        editor_panel_layout = QVBoxLayout(self.editor_panel)
        editor_panel_layout.setContentsMargins(0, 0, 0, 0)
        editor_panel_layout.setSpacing(0)
        self.editor_toolbar_widget = self.kreiraj_editor_toolbar()
        editor_panel_layout.addWidget(self.editor_toolbar_widget)
        self.editor = MarkdownEditor()
        editor_panel_layout.addWidget(self.editor)

        # Content container sa slide animacijom
        self.content_container = ContentContainer()
        self.content_container.setChildren(self.pregledac, self.editor_panel)

        # Dodaj widgete u splitter
        self.glavni_splitter.addWidget(self.tree_view)
        self.glavni_splitter.addWidget(self.content_container)
        self.glavni_splitter.setStretchFactor(0, 15)
        self.glavni_splitter.setStretchFactor(1, 85)

        layout.addWidget(self.glavni_splitter)

        # GitHub Dark CSS
        self.css_stil = ucitaj_css()

        # Trenutni sadržaj
        self.trenutni_sadrzaj = ""

        # Postavke
        self.settings = ucitaj_postavke()

        # Inicijalizuj vrijednosti iz postavki
        self.auto_refresh_val = self.settings.get("auto_refresh", True)
        self.auto_hide_sidebar_val = self.settings.get("auto_hide_sidebar", False)
        self.remember_sidebar_pos_val = self.settings.get("remember_sidebar_pos", True)
        self.default_zoom_val = self.settings.get("default_zoom", 1.0)
        self.default_editor = self.settings.get("default_editor", "xdg-open")
        self.recent_files = self.settings.get("recent_files", [])

        # Primijeni zoom iz postavki (override hardkodiranog 1.0)
        self.pregledac.setZoomFactor(self.default_zoom_val)

        # Rebuild recent menu after recent_files is loaded
        self._rebuild_recent_menu()

        # Primijeni sidebar postavke iz JSON-a
        sidebar_visible = self.settings.get("sidebar_visible", True)
        sidebar_width = self.settings.get("sidebar_width", 250)
        if sidebar_visible:
            self.tree_view.show()
        else:
            self.tree_view.hide()
        # Postavi širinu splitter-a tek kad je window prikazan
        QTimer.singleShot(0, lambda: self.glavni_splitter.setSizes([sidebar_width, self.width() - sidebar_width]))

        # Keyboard shortcuts
        self._setup_shortcuts()

        # Word count signal
        self.editor.textChanged.connect(self._update_word_count)

        # Početni ekran
        self.osvjezi_pregled(self._pocetni_ekran())

        # Ako je proslijeđen fajl kroz argument, otvori ga
        if pocetni_fajl and os.path.isfile(pocetni_fajl):
            # Malo zakasni da se prozor prvo renderuje
            QTimer.singleShot(100, lambda: self.ucitaj_fajl(pocetni_fajl))

    def _pocetni_ekran(self):
        """Returns markdown for the welcome screen."""
        return _t("welcome", version=VERSION)

    # ===== MENI =====

    def kreiraj_meni(self):
        """Kreira meni bar sa svim opcijama"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #161b22;
                color: #c9d1d9;
                border-bottom: 1px solid #30363d;
            }
            QMenuBar::item:selected {
                background-color: #30363d;
            }
            QMenu {
                background-color: #161b22;
                color: #c9d1d9;
                border: 1px solid #30363d;
            }
            QMenu::item:selected {
                background-color: #1f6feb;
            }
        """)

        # ===== FAJL MENI =====
        file_menu = menubar.addMenu(_t("menu_file"))

        open_action = QAction(_t("open_file"), self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.otvori_fajl)
        file_menu.addAction(open_action)

        reload_action = QAction(_t("reload"), self)
        reload_action.setShortcuts([QKeySequence.Refresh, QKeySequence("F5")])
        reload_action.triggered.connect(self.reload_trenutni_fajl)
        file_menu.addAction(reload_action)

        export_pdf_action = QAction(_t("export_pdf"), self)
        export_pdf_action.setShortcut("Ctrl+Shift+E")
        export_pdf_action.triggered.connect(self.export_pdf)
        file_menu.addAction(export_pdf_action)

        file_menu.addSeparator()

        folder_action = QAction(_t("change_folder"), self)
        folder_action.triggered.connect(self.promijeni_folder)
        file_menu.addAction(folder_action)

        file_menu.addSeparator()
        self.recent_menu = QMenu(_t("recent_files"), self)
        file_menu.addMenu(self.recent_menu)
        file_menu.addSeparator()

        exit_action = QAction(_t("exit"), self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # ===== PREGLED MENI =====
        view_menu = menubar.addMenu(_t("menu_view"))

        zoom_in = QAction(_t("zoom_in"), self)
        zoom_in.setShortcut(QKeySequence.ZoomIn)
        zoom_in.triggered.connect(
            lambda: self.pregledac.setZoomFactor(self.pregledac.zoomFactor() + 0.1)
        )
        view_menu.addAction(zoom_in)

        zoom_out = QAction(_t("zoom_out"), self)
        zoom_out.setShortcut(QKeySequence.ZoomOut)
        zoom_out.triggered.connect(
            lambda: self.pregledac.setZoomFactor(self.pregledac.zoomFactor() - 0.1)
        )
        view_menu.addAction(zoom_out)

        zoom_reset = QAction(_t("zoom_reset"), self)
        zoom_reset.setShortcut("Ctrl+0")
        zoom_reset.triggered.connect(lambda: self.pregledac.setZoomFactor(1.0))
        view_menu.addAction(zoom_reset)

        view_menu.addSeparator()

        self.toggle_sidebar_action = QAction(_t("toggle_sidebar"), self)
        self.toggle_sidebar_action.setShortcut("Ctrl+B")
        self.toggle_sidebar_action.triggered.connect(self.toggle_sidebar)
        view_menu.addAction(self.toggle_sidebar_action)

        # ===== POSTAVKE MENI =====
        settings_menu = menubar.addMenu(_t("menu_settings"))

        preferences_action = QAction("\u2699\ufe0f " + _t("preferences"), self)
        preferences_action.setStatusTip(_t("preferences"))
        preferences_action.triggered.connect(self.show_settings)
        settings_menu.addAction(preferences_action)

        # ===== POMOĆ MENI =====
        help_menu = menubar.addMenu(_t("menu_help"))

        about_action = QAction(_t("about"), self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    # ===== TOOLBAR =====

    def kreiraj_toolbar(self):
        """Kreira toolbar sa akcijama"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #161b22;
                border: none;
                border-bottom: 1px solid #30363d;
                spacing: 3px;
                padding: 4px;
            }
            QToolButton {
                background-color: #21262d;
                border: 1px solid #30363d;
                border-radius: 4px;
                padding: 6px 12px;
                color: #c9d1d9;
                font-weight: bold;
                min-width: 80px;
            }
            QToolButton:hover {
                background-color: #30363d;
                border-color: #58a6ff;
            }
            QToolButton:pressed {
                background-color: #1f6feb;
            }
            QToolButton:disabled {
                color: #484f58;
                background-color: #0d1117;
            }
            QLineEdit {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 4px;
                padding: 6px;
                color: #c9d1d9;
            }
            QLineEdit:focus {
                border-color: #58a6ff;
            }
        """)

        # Back dugme
        self.back_action = QAction(_t("btn_back"), self)
        self.back_action.setStatusTip(_t("tip_back"))
        self.back_action.setShortcut(QKeySequence("Alt+Left"))
        self.back_action.triggered.connect(self.idi_nazad)
        self.back_action.setEnabled(False)
        toolbar.addAction(self.back_action)

        # Forward dugme
        self.forward_action = QAction(_t("btn_fwd"), self)
        self.forward_action.setStatusTip(_t("tip_fwd"))
        self.forward_action.setShortcut(QKeySequence("Alt+Right"))
        self.forward_action.triggered.connect(self.idi_naprijed)
        self.forward_action.setEnabled(False)
        toolbar.addAction(self.forward_action)

        toolbar.addSeparator()

        # Open File dugme
        open_action = QAction(_t("btn_open"), self)
        open_action.setStatusTip(_t("tip_open"))
        open_action.triggered.connect(self.otvori_fajl)
        toolbar.addAction(open_action)

        # Edit/Preview toggle dugme
        self.edit_toggle_action = QAction(_t("btn_edit"), self)
        self.edit_toggle_action.setStatusTip(_t("tip_edit_toggle"))
        self.edit_toggle_action.triggered.connect(self.toggle_edit_mode)
        toolbar.addAction(self.edit_toggle_action)

        # Split view dugme
        self.split_action = QAction(_t("btn_split"), self)
        self.split_action.setStatusTip(_t("tip_split"))
        self.split_action.triggered.connect(self.toggle_split_mode)
        toolbar.addAction(self.split_action)

        # Delete dugme
        delete_action = QAction(_t("btn_delete"), self)
        delete_action.setStatusTip(_t("tip_delete"))
        delete_action.triggered.connect(self.delete_file)
        toolbar.addAction(delete_action)

        toolbar.addSeparator()

        # Search polje
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText(_t("search_placeholder"))
        self.search_field.setMaximumWidth(300)
        self.search_field.returnPressed.connect(self.search_in_file)
        toolbar.addWidget(self.search_field)

        toolbar.addSeparator()

        # Toggle Sidebar dugme
        self.sidebar_toolbar_action = QAction(_t("btn_sidebar"), self)
        self.sidebar_toolbar_action.setStatusTip(_t("tip_sidebar"))
        self.sidebar_toolbar_action.triggered.connect(self.toggle_sidebar)
        toolbar.addAction(self.sidebar_toolbar_action)

        # Dodaj toolbar u main window
        self.addToolBar(toolbar)

    def kreiraj_editor_toolbar(self):
        """Kreira toolbar za editor sa markdown formatting akcijama"""
        toolbar = QToolBar("Editor Toolbar")
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #161b22;
                border: none;
                border-bottom: 1px solid #30363d;
                spacing: 2px;
                padding: 3px;
            }
            QToolButton {
                background-color: #21262d;
                border: 1px solid #30363d;
                border-radius: 3px;
                padding: 4px 8px;
                color: #c9d1d9;
                font-weight: bold;
                min-width: 28px;
            }
            QToolButton:hover {
                background-color: #30363d;
                border-color: #58a6ff;
            }
            QToolButton:pressed {
                background-color: #1f6feb;
            }
            QSpinBox {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 3px;
                padding: 3px;
                color: #c9d1d9;
                min-width: 80px;
            }
        """)

        # Bold
        bold_action = QAction("B", self)
        bold_action.setToolTip(_t("tip_bold"))
        bold_action.triggered.connect(self.insert_bold)
        toolbar.addAction(bold_action)

        # Italic
        italic_action = QAction("I", self)
        italic_action.setToolTip(_t("tip_italic"))
        italic_action.triggered.connect(self.insert_italic)
        toolbar.addAction(italic_action)

        # Strikethrough
        strike_action = QAction("S\u0336", self)
        strike_action.setToolTip(_t("tip_strike"))
        strike_action.triggered.connect(self.insert_strikethrough)
        toolbar.addAction(strike_action)

        toolbar.addSeparator()

        # Headers H1-H3
        for level in range(1, 4):
            h_action = QAction(f"H{level}", self)
            h_action.setToolTip(f"Heading {level}")
            h_action.triggered.connect(lambda checked, l=level: self.insert_heading(l))
            toolbar.addAction(h_action)

        toolbar.addSeparator()

        # Link
        link_action = QAction("Link", self)
        link_action.setToolTip(_t("tip_link"))
        link_action.triggered.connect(self.insert_link)
        toolbar.addAction(link_action)

        # Image
        img_action = QAction("Img", self)
        img_action.setToolTip(_t("tip_img"))
        img_action.triggered.connect(self.insert_image)
        toolbar.addAction(img_action)

        # Code
        code_action = QAction("</>", self)
        code_action.setToolTip(_t("tip_code"))
        code_action.triggered.connect(self.insert_code)
        toolbar.addAction(code_action)

        toolbar.addSeparator()

        # Bullet list
        bullet_action = QAction("- List", self)
        bullet_action.setToolTip(_t("tip_bullet"))
        bullet_action.triggered.connect(self.insert_bullet_list)
        toolbar.addAction(bullet_action)

        # Numbered list
        num_action = QAction("1. List", self)
        num_action.setToolTip(_t("tip_num"))
        num_action.triggered.connect(self.insert_num_list)
        toolbar.addAction(num_action)

        toolbar.addSeparator()

        # Table
        table_action = QAction("Table", self)
        table_action.setToolTip(_t("tip_table"))
        table_action.triggered.connect(self.insert_table)
        toolbar.addAction(table_action)

        # HR
        hr_action = QAction("---", self)
        hr_action.setToolTip(_t("tip_hr"))
        hr_action.triggered.connect(self.insert_hr)
        toolbar.addAction(hr_action)

        # Blockquote
        quote_action = QAction("> Quote", self)
        quote_action.setToolTip(_t("tip_quote"))
        quote_action.triggered.connect(self.insert_blockquote)
        toolbar.addAction(quote_action)

        toolbar.addSeparator()

        # Font size
        self.editor_font_size = QSpinBox()
        self.editor_font_size.setRange(8, 32)
        self.editor_font_size.setValue(13)
        self.editor_font_size.setPrefix("Font: ")
        self.editor_font_size.setSuffix("px")
        self.editor_font_size.setToolTip(_t("tip_font"))
        self.editor_font_size.valueChanged.connect(self._change_editor_font_size)
        toolbar.addWidget(self.editor_font_size)

        # Color picker
        color_action = QAction("Color", self)
        color_action.setToolTip(_t("tip_color"))
        color_action.triggered.connect(self.insert_color_text)
        toolbar.addAction(color_action)

        # Special characters
        spec_action = QAction("\u03a9", self)
        spec_action.setToolTip(_t("tip_special"))
        spec_action.triggered.connect(self.insert_special_char)
        toolbar.addAction(spec_action)

        return toolbar

    def _setup_shortcuts(self):
        """Setup global keyboard shortcuts"""
        # Ctrl+E - toggle edit mode
        QShortcut(QKeySequence("Ctrl+E"), self, self.toggle_edit_mode)
        # Ctrl+S - save in edit mode
        QShortcut(QKeySequence.Save, self, self.sacuvaj_edit)
        # Ctrl+Shift+S - toggle split mode
        QShortcut(QKeySequence("Ctrl+Shift+S"), self, self.toggle_split_mode)
        # Editor-specific shortcuts (active when editor has focus)
        QShortcut(QKeySequence("Ctrl+B"), self.editor, self.insert_bold)
        QShortcut(QKeySequence("Ctrl+I"), self.editor, self.insert_italic)
        QShortcut(QKeySequence("Ctrl+K"), self.editor, self.insert_link)
        QShortcut(QKeySequence("Ctrl+`"), self.editor, self.insert_code)

    # ===== RECENT FILES =====

    def _rebuild_recent_menu(self):
        self.recent_menu.clear()
        if not self.recent_files:
            no_recent = QAction(_t("no_recent_files"), self)
            no_recent.setEnabled(False)
            self.recent_menu.addAction(no_recent)
        else:
            for path in self.recent_files[:10]:
                action = QAction(os.path.basename(path), self)
                action.setStatusTip(path)
                action.triggered.connect(lambda checked, p=path: self.ucitaj_fajl(p))
                self.recent_menu.addAction(action)
            self.recent_menu.addSeparator()
            clear_action = QAction(_t("clear_recent"), self)
            clear_action.triggered.connect(self._clear_recent_files)
            self.recent_menu.addAction(clear_action)

    def _clear_recent_files(self):
        self.recent_files = []
        self._rebuild_recent_menu()
        sacuvaj_postavke(self._collect_settings())

    def _update_recent_files(self, path: str):
        if path in self.recent_files:
            self.recent_files.remove(path)
        self.recent_files.insert(0, path)
        self.recent_files = self.recent_files[:10]
        self._rebuild_recent_menu()
        sacuvaj_postavke(self._collect_settings())

    # ===== WORD COUNT =====

    def _update_word_count(self):
        if self.edit_mode:
            tekst = self.editor.toPlainText()
        else:
            tekst = self.trenutni_sadrzaj
        if not tekst.strip():
            self.word_count_label.hide()
            return
        words = len(re.findall(r'\S+', tekst))
        minutes = max(1, round(words / 200))
        self.word_count_label.setText(_t("word_count", words=words, minutes=minutes))
        self.word_count_label.show()

    # ===== PDF EXPORT =====

    def export_pdf(self):
        if not self.trenutni_fajl:
            return
        default = str(Path(self.trenutni_fajl).with_suffix('.pdf'))
        path, _ = QFileDialog.getSaveFileName(self, _t("export_pdf"), default, "PDF (*.pdf)")
        if path:
            try:
                self.pregledac.page().pdfPrintingFinished.disconnect(self._on_pdf_done)
            except RuntimeError:
                pass
            self.pregledac.page().pdfPrintingFinished.connect(self._on_pdf_done)
            self.pregledac.page().printToPdf(path)

    def _on_pdf_done(self, path, ok):
        try:
            self.pregledac.page().pdfPrintingFinished.disconnect(self._on_pdf_done)
        except RuntimeError:
            pass
        if ok:
            self.status_bar.showMessage(_t("status_pdf_saved", path=path))

    # ===== SPLIT VIEW =====

    def toggle_split_mode(self):
        if self.split_mode:
            self._exit_split_mode()
        else:
            self._enter_split_mode()

    def _enter_split_mode(self):
        self.split_mode = True
        # Load file content into editor if needed
        if not self.edit_mode and self.trenutni_fajl:
            try:
                with open(self.trenutni_fajl, "r", encoding="utf-8") as f:
                    self.editor.setPlainText(f.read())
            except Exception:
                pass
        self.split_splitter = QSplitter(Qt.Horizontal)
        # Reparent editor_panel and pregledac
        self.editor_panel.setParent(self.split_splitter)
        self.pregledac.setParent(self.split_splitter)
        self.split_splitter.addWidget(self.editor_panel)
        self.split_splitter.addWidget(self.pregledac)
        self.editor_panel.show()
        self.pregledac.show()
        self.glavni_splitter.replaceWidget(1, self.split_splitter)
        # setSizes mora biti u singleShot jer geometrija nije postavljena odmah
        QTimer.singleShot(0, lambda: (
            self.split_splitter.setSizes([
                self.split_splitter.width() // 2,
                self.split_splitter.width() // 2,
            ]) if self.split_splitter else None
        ))
        # Ukloni Ctrl+B sa sidebar akcije da nema konflikta s bold prečicom u editoru
        self.toggle_sidebar_action.setShortcut("")
        self._split_text_changed_conn = self.editor.textChanged.connect(
            lambda: self.split_timer.start(400)
        )
        self.split_action.setText(_t("btn_single"))

    def _exit_split_mode(self):
        # Disconnect live-update
        try:
            self.editor.textChanged.disconnect(self._split_text_changed_conn)
        except Exception:
            pass
        # Save editor content
        if self.trenutni_fajl:
            try:
                with open(self.trenutni_fajl, "w", encoding="utf-8") as f:
                    f.write(self.editor.toPlainText())
            except Exception:
                pass
        # Re-attach widgets to content_container (setChildren resetuje na preview stanje)
        self.content_container.setChildren(self.pregledac, self.editor_panel)
        self.glavni_splitter.replaceWidget(1, self.content_container)
        if self.split_splitter:
            self.split_splitter.deleteLater()
            self.split_splitter = None
        self.split_mode = False
        self.split_action.setText(_t("btn_split"))
        # Vrati Ctrl+B na sidebar ako nismo u edit modu
        if not self.edit_mode:
            self.toggle_sidebar_action.setShortcut("Ctrl+B")
        # Resetuj edit_mode — izlaz iz split uvijek ide u preview
        if self.edit_mode:
            self.edit_mode = False
            self.edit_toggle_action.setText(_t("btn_edit"))
            self.toggle_sidebar_action.setShortcut("Ctrl+B")
        # Refresh preview
        if self.trenutni_fajl:
            self.reload_trenutni_fajl()

    def _split_preview_update(self):
        tekst = self.editor.toPlainText()
        self.osvjezi_pregled(tekst)

    # ===== SIDEBAR =====

    def toggle_sidebar(self):
        """Prikazuje/sakriva sidebar"""
        if self.tree_view.isVisible():
            self.tree_view.hide()
        else:
            self.tree_view.show()

    def edit_file(self):
        """Toggle edit mode umjesto otvaranja u eksternom editoru"""
        self.toggle_edit_mode()

    # ===== NAVIGACIJA (BACK/FORWARD) =====

    def idi_nazad(self):
        """Idi na prethodni fajl u historiji"""
        if self.istorija_index > 0:
            self.istorija_index -= 1
            self.ucitaj_fajl(self.istorija[self.istorija_index], iz_istorije=True)

    def idi_naprijed(self):
        """Idi na sljedeći fajl u historiji"""
        if self.istorija_index < len(self.istorija) - 1:
            self.istorija_index += 1
            self.ucitaj_fajl(self.istorija[self.istorija_index], iz_istorije=True)

    def azuriraj_navigaciju(self):
        """Ažuriraj enabled stanje Back/Forward dugmadi"""
        self.back_action.setEnabled(self.istorija_index > 0)
        self.forward_action.setEnabled(
            self.istorija_index < len(self.istorija) - 1
        )

    # ===== EDIT MODE =====

    def toggle_edit_mode(self):
        """Prebaci između Edit i Preview moda"""
        if self.edit_mode:
            self.prebaci_u_preview()
        else:
            self.prebaci_u_edit()

    def prebaci_u_edit(self):
        """Prebaci u edit mod sa slide animacijom"""
        if not self.trenutni_fajl:
            QMessageBox.warning(
                self, _t("dlg_warning"), _t("msg_no_file_edit")
            )
            return

        self.edit_mode = True

        # Učitaj sadržaj u editor
        self.editor.setPlainText(self.trenutni_sadrzaj)

        # Pauziraj file watcher
        if self.trenutni_fajl:
            try:
                self.file_watcher.removePath(self.trenutni_fajl)
                self.edit_paused_watcher = True
            except Exception:
                pass

        # Update toolbar
        self.edit_toggle_action.setText(_t("btn_preview"))
        self.toggle_sidebar_action.setShortcut("")

        # Animiraj prelaz (only if not split mode)
        if not self.split_mode:
            self.content_container.slideTo('editor')
        self.status_bar.showMessage(_t("status_edit", name=os.path.basename(self.trenutni_fajl)))

    def prebaci_u_preview(self):
        """Prebaci u preview mod, sačuvaj fajl"""
        self.edit_mode = False

        # Sačuvaj sadržaj
        content = self.editor.toPlainText()
        self.trenutni_sadrzaj = content

        # Sačuvaj na disk
        if self.trenutni_fajl:
            try:
                with open(self.trenutni_fajl, 'w', encoding='utf-8') as f:
                    f.write(content)
            except Exception as e:
                QMessageBox.critical(
                    self, _t("dlg_error"), _t("msg_save_err", err=str(e))
                )

        # Ponovo pokreni file watcher
        if self.edit_paused_watcher and self.trenutni_fajl:
            self.file_watcher.addPath(self.trenutni_fajl)
            self.edit_paused_watcher = False

        # Update preview
        self.osvjezi_pregled(content)

        # Update toolbar
        self.edit_toggle_action.setText(_t("btn_edit"))
        self.toggle_sidebar_action.setShortcut("Ctrl+B")

        # Animiraj prelaz (only if not split mode)
        if not self.split_mode:
            self.content_container.slideTo('preview')
        if self.trenutni_fajl:
            self.status_bar.showMessage(_t("status_preview", name=os.path.basename(self.trenutni_fajl)))
        self._update_word_count()

    def sacuvaj_edit(self):
        """Sačuvaj fajl iz editora (Ctrl+S)"""
        if not self.edit_mode or not self.trenutni_fajl:
            return
        try:
            content = self.editor.toPlainText()
            with open(self.trenutni_fajl, 'w', encoding='utf-8') as f:
                f.write(content)
            self.trenutni_sadrzaj = content
            self.status_bar.showMessage(_t("status_saved", name=os.path.basename(self.trenutni_fajl)))
            self._update_word_count()
        except Exception as e:
            QMessageBox.critical(
                self, _t("dlg_error"), _t("msg_save_err", err=str(e))
            )

    # ===== EDITOR FORMATTING AKCIJE =====

    def _wrap_selection(self, prefix, suffix=None):
        """Omotaj selektovani tekst sa prefix/suffix"""
        if suffix is None:
            suffix = prefix
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            selected = cursor.selectedText()
            cursor.insertText(f"{prefix}{selected}{suffix}")
        else:
            pos = cursor.position()
            cursor.insertText(f"{prefix}{suffix}")
            cursor.setPosition(pos + len(prefix))
            self.editor.setTextCursor(cursor)

    def insert_bold(self):
        self._wrap_selection("**")

    def insert_italic(self):
        self._wrap_selection("*")

    def insert_strikethrough(self):
        self._wrap_selection("~~")

    def insert_heading(self, level):
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.StartOfBlock)
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        line = cursor.selectedText()
        # Ukloni postojeće # prefixe
        stripped = re.sub(r'^#+\s*', '', line)
        cursor.insertText(f"{'#' * level} {stripped}")

    def insert_link(self):
        cursor = self.editor.textCursor()
        selected = cursor.selectedText() if cursor.hasSelection() else ""
        url, ok = QInputDialog.getText(self, _t("dlg_insert_link"), _t("insert_link_url"))
        if ok and url:
            text = selected if selected else "link text"
            cursor.insertText(f"[{text}]({url})")

    def insert_image(self):
        cursor = self.editor.textCursor()
        selected = cursor.selectedText() if cursor.hasSelection() else ""
        url, ok = QInputDialog.getText(self, _t("dlg_insert_img"), _t("insert_img_url"))
        if ok and url:
            alt = selected if selected else "image"
            cursor.insertText(f"![{alt}]({url})")

    def insert_code(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            selected = cursor.selectedText()
            # Ako ima više linija, koristi code block
            if '\u2029' in selected:
                lines = selected.split('\u2029')
                cursor.insertText("```\n" + "\n".join(lines) + "\n```")
            else:
                cursor.insertText(f"`{selected}`")
        else:
            pos = cursor.position()
            cursor.insertText("``")
            cursor.setPosition(pos + 1)
            self.editor.setTextCursor(cursor)

    def insert_bullet_list(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            selected = cursor.selectedText()
            lines = selected.split('\u2029')
            cursor.insertText("\n".join(f"- {line}" for line in lines))
        else:
            cursor.insertText("- ")

    def insert_num_list(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            selected = cursor.selectedText()
            lines = selected.split('\u2029')
            cursor.insertText(
                "\n".join(f"{i+1}. {line}" for i, line in enumerate(lines))
            )
        else:
            cursor.insertText("1. ")

    def insert_table(self):
        cursor = self.editor.textCursor()
        template = (
            "| Header 1 | Header 2 | Header 3 |\n"
            "|----------|----------|----------|\n"
            "| Cell 1   | Cell 2   | Cell 3   |\n"
            "| Cell 4   | Cell 5   | Cell 6   |\n"
        )
        cursor.insertText(template)

    def insert_hr(self):
        cursor = self.editor.textCursor()
        cursor.insertText("\n---\n")

    def insert_blockquote(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            selected = cursor.selectedText()
            lines = selected.split('\u2029')
            cursor.insertText("\n".join(f"> {line}" for line in lines))
        else:
            cursor.insertText("> ")

    def insert_color_text(self):
        color = QColorDialog.getColor(QColor("#c9d1d9"), self, "Izaberi boju teksta")
        if color.isValid():
            cursor = self.editor.textCursor()
            selected = cursor.selectedText() if cursor.hasSelection() else "text"
            cursor.insertText(
                f'<span style="color:{color.name()}">{selected}</span>'
            )

    def insert_special_char(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #161b22;
                color: #c9d1d9;
                border: 1px solid #30363d;
            }
            QMenu::item:selected {
                background-color: #1f6feb;
            }
        """)
        chars = {
            _t("spec_arrows"):  ["\u2192", "\u2190", "\u2191", "\u2193", "\u2194", "\u21d2", "\u21d0", "\u21d1", "\u21d3"],
            _t("spec_math"):    ["\u00b1", "\u00d7", "\u00f7", "\u2260", "\u2248", "\u2264", "\u2265", "\u221e", "\u221a", "\u2211", "\u220f", "\u222b"],
            _t("spec_symbols"): ["\u00a9", "\u00ae", "\u2122", "\u00b0", "\u2020", "\u2021", "\u00a7", "\u00b6", "\u2022", "\u2026"],
            _t("spec_greek"):   ["\u03b1", "\u03b2", "\u03b3", "\u03b4", "\u03b5", "\u03c0", "\u03c3", "\u03bc", "\u03bb", "\u03a9"],
            _t("spec_emoji"):   ["\U0001f600", "\U0001f60e", "\U0001f389", "\U0001f525", "\u2b50", "\U0001f4a1", "\u2705", "\u274c", "\u26a0\ufe0f", "\U0001f4dd"],
        }
        for category, symbols in chars.items():
            submenu = menu.addMenu(category)
            for s in symbols:
                action = submenu.addAction(s)
                action.triggered.connect(
                    lambda checked, c=s: self.editor.insertPlainText(c)
                )
        menu.exec(QCursor.pos())

    def _change_editor_font_size(self, size):
        font = self.editor.font()
        font.setPointSize(size)
        self.editor.setFont(font)

    # ===== BROWSER OPEN =====

    def otvori_u_browseru(self):
        """Otvori trenutni fajl renderovan u default web browseru"""
        if not self.trenutni_fajl:
            self.status_bar.showMessage(_t("msg_no_file_edit"))
            return
        try:
            html = self._renderuj_html(self.trenutni_sadrzaj, include_base=True)
            tmp = tempfile.NamedTemporaryFile(
                mode='w', suffix='.html', delete=False, encoding='utf-8'
            )
            tmp.write(html)
            tmp.close()
            QDesktopServices.openUrl(QUrl.fromLocalFile(tmp.name))
            self.status_bar.showMessage(_t("btn_open") + " OK")
        except Exception as e:
            QMessageBox.critical(
                self, _t("dlg_error"), _t("dlg_error") + f": {str(e)}"
            )

    # ===== COPY / SELECT =====

    def copy_selected_text(self):
        """Kopiraj selektovani tekst iz pregledača"""
        self.pregledac.page().triggerAction(QWebEnginePage.WebAction.Copy)

    def select_all_text(self):
        """Selektuj sav tekst u pregledaču"""
        self.pregledac.page().triggerAction(QWebEnginePage.WebAction.SelectAll)

    def delete_file(self):
        """Briše trenutni fajl sa potvrdom"""
        if not self.trenutni_fajl:
            QMessageBox.warning(
                self, _t("dlg_warning"), _t("msg_no_file_delete")
            )
            return

        # Potvrda
        reply = QMessageBox.question(
            self,
            _t("dlg_confirm_delete"),
            _t("msg_confirm_delete", name=os.path.basename(self.trenutni_fajl), path=self.trenutni_fajl),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                obrisan = self.trenutni_fajl

                # Pošalji u Trash umjesto permanentnog brisanja
                try:
                    from gi.repository import Gio
                    Gio.File.new_for_path(obrisan).trash(None)
                except Exception:
                    os.remove(obrisan)  # fallback ako Trash nije dostupan

                self.status_bar.showMessage(_t("status_trashed", name=os.path.basename(obrisan)))

                # Ukloni iz navigacione historije da Back ne bi pokazao grešku
                self.istorija = [p for p in self.istorija if p != obrisan]
                self.istorija_index = len(self.istorija) - 1
                self.azuriraj_navigaciju()

                # Resetuj prikaz
                self.trenutni_fajl = None
                self.osvjezi_pregled(self._pocetni_ekran())

                QMessageBox.information(self, _t("dlg_success"), _t("msg_delete_ok"))

            except Exception as e:
                QMessageBox.critical(self, _t("dlg_error"), _t("msg_delete_err", err=str(e)))

    def search_in_file(self):
        """Traži tekst u trenutnom markdown fajlu"""
        search_term = self.search_field.text().strip()

        if not search_term:
            return

        if not self.trenutni_fajl:
            QMessageBox.warning(
                self, _t("dlg_warning"), _t("msg_no_file_search")
            )
            return

        if search_term.lower() not in self.trenutni_sadrzaj.lower():
            QMessageBox.information(
                self, _t("dlg_search"), _t("msg_not_found", term=search_term)
            )
            return

        # Escape za JS regex (posebni znakovi) i za JS string (navodnici)
        js_term = re.escape(search_term).replace('\\', '\\\\').replace("'", "\\'")

        js_code = f"""
        (function() {{
            var term = '{js_term}';
            var regex = new RegExp(term, 'gi');
            var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null);
            var nodes = [];
            var node;
            while ((node = walker.nextNode())) {{
                var tag = node.parentNode.nodeName;
                if (tag === 'SCRIPT' || tag === 'STYLE') continue;
                if (regex.test(node.nodeValue)) {{
                    nodes.push(node);
                    regex.lastIndex = 0;
                }}
            }}
            nodes.forEach(function(n) {{
                var span = document.createElement('span');
                span.innerHTML = n.nodeValue.replace(regex, function(m) {{
                    return '<mark style="background:#ffff00;color:#000000">' + m + '</mark>';
                }});
                n.parentNode.replaceChild(span, n);
            }});
            var first = document.querySelector('mark');
            if (first) first.scrollIntoView({{behavior:'smooth', block:'center'}});
            return nodes.length;
        }})();
        """

        # Čekaj da se stranica renderuje, pa tek onda highlightuj via JS
        def run_highlight(ok):
            self.pregledac.loadFinished.disconnect(run_highlight)
            def show_result(count):
                if count:
                    self.status_bar.showMessage(
                        _t("status_found", term=search_term, count=int(count))
                    )
            self.pregledac.page().runJavaScript(js_code, show_result)

        self.pregledac.loadFinished.connect(run_highlight)
        # Renderuj čist markdown — bez injektiranja HTML-a u markdown source
        self.osvjezi_pregled(self.trenutni_sadrzaj)
        self.status_bar.showMessage(_t("status_searching", term=search_term))

    def show_context_menu(self, pos):
        """Context menu za web view sa link, copy, browser opcijama"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #161b22;
                color: #c9d1d9;
                border: 1px solid #30363d;
            }
            QMenu::item:selected {
                background-color: #1f6feb;
            }
            QMenu::separator {
                background-color: #30363d;
                height: 1px;
                margin: 4px 8px;
            }
        """)

        # Pronađi link ispod kursora i tekst
        js_code = """
            (function() {
                const selection = window.getSelection();
                const selectedText = selection.toString().trim();

                // Pronađi link ispod kursora
                const element = document.elementFromPoint(%d, %d);
                let linkUrl = null;

                if (element) {
                    const linkElement = element.closest('a');
                    if (linkElement) {
                        linkUrl = linkElement.href;
                    }
                }

                return {
                    selectedText: selectedText,
                    hasSelection: selectedText.length > 0,
                    linkUrl: linkUrl,
                    hasLink: linkUrl !== null
                };
            })();
        """ % (pos.x(), pos.y())

        def create_menu_with_data(context_data):
            """Kreiraj meni sa podacima iz JavaScript-a"""
            if not context_data:
                context_data = {}

            # Opcije za linkove
            open_link = None
            copy_link = None
            if context_data.get("hasLink"):
                open_link = menu.addAction(_t("ctx_open_link"))
                copy_link = menu.addAction(_t("ctx_copy_link"))
                menu.addSeparator()

            # Copy / Select opcije
            copy_text = None
            if context_data.get("hasSelection"):
                copy_text = menu.addAction(_t("ctx_copy_sel"))
            select_all = menu.addAction(_t("ctx_select_all"))
            menu.addSeparator()

            # Open in browser
            open_browser = None
            if self.trenutni_fajl:
                open_browser = menu.addAction(_t("ctx_open_browser"))
                menu.addSeparator()

            # Zoom opcije
            zoom_in = menu.addAction(_t("ctx_zoom_in"))
            zoom_out = menu.addAction(_t("ctx_zoom_out"))
            zoom_reset = menu.addAction(_t("ctx_zoom_reset"))
            menu.addSeparator()
            reload_action = menu.addAction(_t("ctx_reload"))

            # Prikaži meni i handle akcije
            action = menu.exec(self.pregledac.mapToGlobal(pos))
            if not action:
                return

            # Handle link akcije
            if action == open_link and context_data.get("hasLink"):
                QDesktopServices.openUrl(QUrl(context_data["linkUrl"]))
            elif action == copy_link and context_data.get("hasLink"):
                QApplication.clipboard().setText(context_data["linkUrl"])
            # Handle copy/select
            elif action == copy_text and context_data.get("hasSelection"):
                QApplication.clipboard().setText(context_data["selectedText"])
            elif action == select_all:
                self.select_all_text()
            # Open in browser
            elif action == open_browser:
                self.otvori_u_browseru()
            # Standardne akcije
            elif action == zoom_in:
                self.pregledac.setZoomFactor(self.pregledac.zoomFactor() + 0.1)
            elif action == zoom_out:
                self.pregledac.setZoomFactor(self.pregledac.zoomFactor() - 0.1)
            elif action == zoom_reset:
                self.pregledac.setZoomFactor(1.0)
            elif action == reload_action:
                self.reload_trenutni_fajl()

        # Izvrši JavaScript i prikaži meni
        self.pregledac.page().runJavaScript(js_code, create_menu_with_data)

    def promijeni_folder(self):
        """Mijenja root folder za file browser"""
        folder = QFileDialog.getExistingDirectory(
            self, _t("change_folder"), QDir.homePath()
        )
        if folder:
            self.file_model.setRootPath(folder)
            self.tree_view.setRootIndex(self.file_model.index(folder))
            self.status_bar.showMessage(_t("status_folder", path=folder))

    def otvori_fajl(self):
        """Otvara fajl kroz dijalog"""
        ime_fajla, _ = QFileDialog.getOpenFileName(
            self,
            _t("open_file"),
            QDir.homePath(),
            "Markdown (*.md *.markdown *.mdown);;Text (*.txt);;Svi fajlovi (*.*)",
        )
        if ime_fajla:
            self.ucitaj_fajl(ime_fajla)

    def ucitaj_fajl(self, putanja, iz_istorije=False):
        """Učitava i renderuje markdown fajl"""
        if not os.path.isfile(putanja):
            QMessageBox.warning(self, _t("dlg_error"), _t("msg_file_missing", path=putanja))
            return

        # Ako smo u edit modu, prebaci u preview
        if self.edit_mode:
            self.prebaci_u_preview()

        # Historija navigacije
        if not iz_istorije:
            self.istorija = self.istorija[:self.istorija_index + 1]
            self.istorija.append(putanja)
            self.istorija_index = len(self.istorija) - 1

        # Ukloni stari fajl iz watchera
        if self.trenutni_fajl:
            try:
                self.file_watcher.removePath(self.trenutni_fajl)
            except Exception:
                pass

        self.trenutni_fajl = putanja

        # Dodaj novi fajl u watcher
        self.file_watcher.addPath(putanja)

        try:
            try:
                with open(putanja, "r", encoding="utf-8") as f:
                    content = f.read()
                encoding_note = ""
            except UnicodeDecodeError:
                with open(putanja, "r", encoding="latin-1") as f:
                    content = f.read()
                encoding_note = " (latin-1)"
        except Exception as e:
            QMessageBox.warning(self, _t("dlg_error"), _t("msg_read_err", err=e))
            return

        self.trenutni_sadrzaj = content
        self.osvjezi_pregled(content)
        self.setWindowTitle(f"{APP_NAME} - {os.path.basename(putanja)}")
        self.status_bar.showMessage(_t("status_loaded", path=putanja + encoding_note))

        # Expand i selektuj fajl u tree view
        index = self.file_model.index(putanja)
        if index.isValid():
            self.tree_view.setCurrentIndex(index)
            self.tree_view.scrollTo(index)

        # Ažuriraj back/forward dugmad
        self.azuriraj_navigaciju()

        # Update recent files and word count on successful load
        self._update_recent_files(putanja)
        self._update_word_count()

    def klik_na_fajl(self, index):
        """Handler za klik na fajl u tree view"""
        putanja = self.file_model.filePath(index)
        if os.path.isfile(putanja):
            ext = os.path.splitext(putanja)[1].lower()
            if ext in [".md", ".markdown", ".mdown", ".txt"]:
                self.ucitaj_fajl(putanja)

    def on_file_changed(self, path):
        """Kad se fajl promijeni izvana, reload sa debounce"""
        if path == self.trenutni_fajl and self.auto_refresh_val:
            # Na Linux/inotify, atomično saveanje (temp→rename) automatski uklanja
            # path iz watchera — trebamo ga dodati nazad
            if path not in self.file_watcher.files():
                self.file_watcher.addPath(path)
            self.reload_timer.start(300)

    def reload_trenutni_fajl(self):
        """Ponovo učitava trenutni fajl"""
        if self.trenutni_fajl and os.path.isfile(self.trenutni_fajl):
            # Sačuvaj scroll poziciju
            self.pregledac.page().runJavaScript(
                "window.scrollY",
                lambda scroll_pos: self._reload_with_scroll(scroll_pos),
            )
        else:
            self.status_bar.showMessage(_t("reload"))

    def _reload_with_scroll(self, scroll_pos):
        """Reload sa očuvanjem scroll pozicije"""
        try:
            with open(self.trenutni_fajl, "r", encoding="utf-8") as f:
                content = f.read()

            self.trenutni_sadrzaj = content
            self.osvjezi_pregled(content)

            # Vrati scroll poziciju nakon renderovanja
            if scroll_pos:
                QTimer.singleShot(
                    100,
                    lambda: self.pregledac.page().runJavaScript(
                        f"window.scrollTo(0, {scroll_pos})"
                    ),
                )

            self.status_bar.showMessage(_t("status_reloaded", name=os.path.basename(self.trenutni_fajl)))
        except Exception as e:
            self.status_bar.showMessage(_t("dlg_error") + f": {e}")

    def _renderuj_html(self, tekst, include_base=False):
        """Generiše kompletni HTML iz markdown teksta"""
        try:
            extensions = [
                "fenced_code",
                "tables",
                "nl2br",
                "toc",
                "abbr",
                "attr_list",
                "def_list",
                "footnotes",
                "md_in_html",
                "sane_lists",
                "smarty",
                "admonition",
            ]

            extension_configs = {}

            try:
                import pymdownx

                extensions.extend(
                    [
                        "pymdownx.highlight",
                        "pymdownx.superfences",
                        "pymdownx.tasklist",
                        "pymdownx.magiclink",
                        "pymdownx.betterem",
                        "pymdownx.tilde",
                        "pymdownx.mark",
                        "pymdownx.caret",
                        "pymdownx.keys",
                    ]
                )
                extension_configs.update(
                    {
                        "pymdownx.highlight": {
                            "use_pygments": True,
                            "guess_lang": True,
                            "linenums": False,
                            "css_class": "highlight",
                        },
                        "pymdownx.tasklist": {
                            "custom_checkbox": True,
                            "clickable_checkbox": False,
                        },
                    }
                )
            except ImportError:
                pass

            html_content = markdown.markdown(
                tekst, extensions=extensions, extension_configs=extension_configs
            )

        except Exception as e:
            html_content = f"""
            <div style="color: #f85149; background: #21262d; padding: 16px; border-radius: 6px;">
                <h3>Greška pri renderovanju</h3>
                <pre>{str(e)}</pre>
            </div>
            <hr>
            <pre>{tekst[:1000]}...</pre>
            """

        base_url_tag = ""
        if include_base and self.trenutni_fajl:
            base_url_tag = f"<base href='file://{os.path.dirname(self.trenutni_fajl)}/'>"

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    {base_url_tag}
    {self.css_stil}
</head>
<body>
    {html_content}
</body>
</html>"""

    def osvjezi_pregled(self, tekst=None):
        """Renderuje markdown u HTML i prikazuje"""
        if tekst is None:
            tekst = self.trenutni_sadrzaj

        html = self._renderuj_html(tekst)

        # Koristi base URL za relativne linkove
        base_url = QUrl()
        if self.trenutni_fajl:
            base_url = QUrl.fromLocalFile(
                os.path.dirname(self.trenutni_fajl) + '/'
            )
        self.pregledac.setHtml(html, base_url)

    # ===== DRAG & DROP =====

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith((".md", ".markdown", ".mdown", ".txt")):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            putanja = url.toLocalFile()
            if putanja.lower().endswith((".md", ".markdown", ".mdown", ".txt")):
                self.ucitaj_fajl(putanja)
                event.acceptProposedAction()
                return

    # ===== ABOUT =====

    def show_about(self):
        """Shows the About dialog."""
        GITHUB_URL = "https://github.com/yourusername/NZ-MDviewer"

        dialog = QDialog(self)
        dialog.setWindowTitle(_t("about_title"))
        dialog.setModal(True)
        dialog.resize(420, 340)
        dialog.setStyleSheet("""
            QDialog { background-color: #161b22; color: #c9d1d9; }
            QLabel  { color: #c9d1d9; background: transparent; border: none; }
            QPushButton {
                background-color: #21262d;
                border: 1px solid #30363d;
                border-radius: 4px;
                padding: 6px 14px;
                color: #c9d1d9;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #30363d; border-color: #58a6ff; }
            QPushButton:pressed { background-color: #1f6feb; }
            QPushButton#github_btn { border-color: #58a6ff; color: #58a6ff; }
            QPushButton#github_btn:hover { background-color: #1f6feb; color: #ffffff; }
        """)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)
        layout.setContentsMargins(24, 20, 24, 16)

        # Header row: icon + title + version
        header = QHBoxLayout()
        header.setSpacing(14)

        icon_path = Path(__file__).parent / "icons" / "nzmdviewer_64.png"
        if icon_path.exists():
            icon_label = QLabel()
            icon_label.setPixmap(QPixmap(str(icon_path)).scaled(
                56, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
            icon_label.setFixedSize(56, 56)
            header.addWidget(icon_label)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        name_label = QLabel(f"<b style='font-size:17px;'>{APP_NAME}</b>")
        name_label.setTextFormat(Qt.RichText)
        ver_label = QLabel(f"<span style='color:#8b949e;'>v{VERSION} \u2014 MIT License</span>")
        ver_label.setTextFormat(Qt.RichText)
        title_col.addWidget(name_label)
        title_col.addWidget(ver_label)
        header.addLayout(title_col)
        header.addStretch()
        layout.addLayout(header)

        # Thin separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #30363d; background-color: #30363d; border: none; max-height: 1px;")
        layout.addWidget(sep)

        # Body text
        body = QLabel(_t("about_body"))
        body.setTextFormat(Qt.RichText)
        body.setWordWrap(True)
        body.setOpenExternalLinks(True)
        layout.addWidget(body)

        layout.addStretch()

        # Bottom buttons
        btn_layout = QHBoxLayout()
        github_btn = QPushButton("\u2b50 GitHub")
        github_btn.setObjectName("github_btn")
        github_btn.setToolTip(GITHUB_URL)
        github_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(GITHUB_URL))
        )
        license_btn = QPushButton("\U0001f4c4 MIT License")
        license_btn.clicked.connect(lambda: self._show_license())
        btn_layout.addWidget(github_btn)
        btn_layout.addWidget(license_btn)
        btn_layout.addStretch()
        ok_btn = QPushButton("\u2713 OK")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

        dialog.exec()

    def _show_license(self):
        """Shows the MIT License text in a simple dialog."""
        dialog = QDialog(self)
        dialog.setWindowTitle("MIT License")
        dialog.setModal(True)
        dialog.resize(480, 320)
        dialog.setStyleSheet("""
            QDialog { background-color: #161b22; color: #c9d1d9; }
            QPlainTextEdit {
                background-color: #0d1117;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 4px;
                font-family: monospace;
                font-size: 12px;
            }
            QPushButton {
                background-color: #21262d;
                border: 1px solid #30363d;
                border-radius: 4px;
                padding: 6px 20px;
                color: #c9d1d9;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #30363d; }
        """)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(16, 16, 16, 12)
        text = QPlainTextEdit()
        text.setReadOnly(True)
        text.setPlainText(
            "MIT License\n\n"
            "Copyright (c) 2025 NZ\n\n"
            "Permission is hereby granted, free of charge, to any person obtaining a copy "
            "of this software and associated documentation files (the \"Software\"), to deal "
            "in the Software without restriction, including without limitation the rights "
            "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell "
            "copies of the Software, and to permit persons to whom the Software is "
            "furnished to do so, subject to the following conditions:\n\n"
            "The above copyright notice and this permission notice shall be included in all "
            "copies or substantial portions of the Software.\n\n"
            "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR "
            "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, "
            "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE "
            "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER "
            "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, "
            "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE "
            "SOFTWARE."
        )
        layout.addWidget(text)
        ok_btn = QPushButton("\u2713 OK")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(dialog.accept)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)
        dialog.exec()

    # ===== SETTINGS =====

    def show_settings(self):
        """Shows the preferences dialog."""
        from translations import _LANG as current_lang

        dialog = QDialog(self)
        dialog.setWindowTitle(_t("settings_title"))
        dialog.setModal(True)
        dialog.resize(550, 500)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #161b22;
                color: #c9d1d9;
            }
            QLabel {
                color: #c9d1d9;
                font-weight: bold;
            }
            QGroupBox {
                border: 1px solid #30363d;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #21262d;
                border: 1px solid #30363d;
                border-radius: 4px;
                padding: 8px 16px;
                color: #c9d1d9;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #30363d;
                border-color: #58a6ff;
            }
            QPushButton:pressed {
                background-color: #1f6feb;
            }
            QComboBox {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 4px;
                padding: 6px;
                color: #c9d1d9;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #c9d1d9;
            }
        """)

        layout = QVBoxLayout(dialog)

        # Language settings
        lang_group = QGroupBox(_t("settings_lang_group"))
        lang_layout = QVBoxLayout()
        lang_hbox = QHBoxLayout()
        lang_hbox.addWidget(QLabel(_t("settings_lang_label")))
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("Bosanski / Hrvatski / Srpski", "bs")
        current_idx = self.lang_combo.findData(current_lang)
        if current_idx >= 0:
            self.lang_combo.setCurrentIndex(current_idx)
        lang_hbox.addWidget(self.lang_combo)
        lang_layout.addLayout(lang_hbox)
        lang_note = QLabel(_t("settings_lang_note"))
        lang_note.setStyleSheet("color: #8b949e; font-weight: normal; font-style: italic;")
        lang_layout.addWidget(lang_note)
        lang_group.setLayout(lang_layout)
        layout.addWidget(lang_group)

        # Sidebar settings
        sidebar_group = QGroupBox(_t("settings_sidebar_group"))
        sidebar_layout = QVBoxLayout()

        self.show_sidebar_check = QCheckBox(_t("settings_show_sidebar"))
        self.show_sidebar_check.setChecked(self.tree_view.isVisible())
        sidebar_layout.addWidget(self.show_sidebar_check)

        self.auto_hide_sidebar = QCheckBox(_t("settings_auto_hide"))
        self.auto_hide_sidebar.setChecked(getattr(self, "auto_hide_sidebar_val", False))
        sidebar_layout.addWidget(self.auto_hide_sidebar)

        self.remember_sidebar_pos = QCheckBox(_t("settings_remember_pos"))
        self.remember_sidebar_pos.setChecked(
            self.settings.get("remember_sidebar_pos", True)
        )
        sidebar_layout.addWidget(self.remember_sidebar_pos)

        sidebar_group.setLayout(sidebar_layout)
        layout.addWidget(sidebar_group)

        # Preview settings
        preview_group = QGroupBox(_t("settings_preview_group"))
        preview_layout = QVBoxLayout()

        self.auto_refresh = QCheckBox(_t("settings_auto_refresh"))
        self.auto_refresh.setChecked(self.auto_refresh_val)
        preview_layout.addWidget(self.auto_refresh)

        zoom_hbox = QHBoxLayout()
        zoom_hbox.addWidget(QLabel(_t("settings_default_zoom")))
        self.default_zoom = QDoubleSpinBox()
        self.default_zoom.setRange(0.5, 3.0)
        self.default_zoom.setSingleStep(0.1)
        self.default_zoom.setValue(self.settings.get("default_zoom", 1.0))
        self.default_zoom.setSuffix("x")
        zoom_hbox.addWidget(self.default_zoom)
        preview_layout.addLayout(zoom_hbox)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton(_t("settings_save"))
        cancel_button = QPushButton(_t("settings_cancel"))

        save_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        if dialog.exec() == QDialog.Accepted:
            self.apply_settings()

    def apply_settings(self):
        """Applies and persists settings."""
        # Language
        nova_lang = self.lang_combo.currentData()
        if nova_lang:
            set_lang(nova_lang)
            self.settings["language"] = nova_lang

        # Other settings
        self.auto_hide_sidebar_val = self.auto_hide_sidebar.isChecked()
        self.remember_sidebar_pos_val = self.remember_sidebar_pos.isChecked()
        self.auto_refresh_val = self.auto_refresh.isChecked()
        self.default_zoom_val = self.default_zoom.value()

        # Sidebar visibility (show_sidebar_check takes immediate effect)
        if self.show_sidebar_check.isChecked():
            self.tree_view.show()
        else:
            self.tree_view.hide()

        # Default zoom
        current_zoom = self.pregledac.zoomFactor()
        if current_zoom != self.default_zoom_val:
            self.pregledac.setZoomFactor(self.default_zoom_val)

        # Sačuvaj sve postavke
        sacuvaj_postavke(self._collect_settings())

        # Info poruka
        self.status_bar.showMessage(_t("status_settings"))

    # ===== SETTINGS COLLECT =====

    def _collect_settings(self) -> dict:
        sizes = self.glavni_splitter.sizes()
        sidebar_width = sizes[0] if sizes and sizes[0] > 0 else 250
        return {
            "language": self.settings.get("language", "en"),
            "auto_hide_sidebar": getattr(self, "auto_hide_sidebar_val", False),
            "sidebar_visible": self.tree_view.isVisible(),
            "sidebar_width": sidebar_width,
            "remember_sidebar_pos": getattr(self, "remember_sidebar_pos_val", True),
            "auto_refresh": getattr(self, "auto_refresh_val", True),
            "default_zoom": getattr(self, "default_zoom_val", 1.0),
            "default_editor": getattr(self, "default_editor", "xdg-open"),
            "recent_files": getattr(self, "recent_files", []),
        }

    # ===== CLOSE EVENT =====

    def closeEvent(self, event):
        """Čuva postavke (uključujući širinu sidebara) pri zatvaranju prozora"""
        sacuvaj_postavke(self._collect_settings())
        event.accept()


def main():
    """Entry point"""
    # Load language from settings before building UI
    if os.path.isfile(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            lang = saved.get("language", "en")
            set_lang(lang)
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("NZ")
    app.setApplicationVersion(VERSION)

    # Set application icon
    icon_path = Path(__file__).parent / "icons" / "nzmdviewer_256.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Provjeri da li je proslijeđen fajl kao argument
    pocetni_fajl = None
    if len(sys.argv) > 1:
        potencijalni_fajl = sys.argv[1]
        if os.path.isfile(potencijalni_fajl):
            pocetni_fajl = os.path.abspath(potencijalni_fajl)

    prozor = BalkanMDViewer(pocetni_fajl)
    prozor.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
