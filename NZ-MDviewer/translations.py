"""
Simple dict-based i18n. "en" is default. "bs" = Bosnian/Croatian/Serbian.
To add a language: copy the "en" block and translate the values.
"""

_LANG: str = "en"  # Set from settings before UI is built


TRANSLATIONS: dict = {
    "en": {
        # Menus
        "menu_file":         "&File",
        "menu_view":         "&View",
        "menu_settings":     "&Settings",
        "menu_help":         "&Help",
        # File menu
        "open_file":         "Open File",
        "reload":            "Reload",
        "change_folder":     "Change Folder",
        "recent_files":      "Recent Files",
        "clear_recent":      "Clear Recent",
        "no_recent_files":   "(No recent files)",
        "export_pdf":        "Export as PDF",
        "exit":              "Exit",
        # View menu
        "zoom_in":           "Zoom In",
        "zoom_out":          "Zoom Out",
        "zoom_reset":        "Reset Zoom",
        "toggle_sidebar":    "Toggle Sidebar",
        # Settings menu
        "sidebar_menu":      "Sidebar",
        "preferences":       "Preferences",
        # Help menu
        "about":             "About",
        # Toolbar buttons
        "btn_back":          "◀ Back",
        "btn_fwd":           "▶ Fwd",
        "btn_open":          "📂 Open",
        "btn_edit":          "✏️ Edit",
        "btn_preview":       "👁️ Preview",
        "btn_delete":        "🗑️ Delete",
        "btn_sidebar":       "📁 Sidebar",
        "btn_split":         "⊟ Split",
        "btn_single":        "⊞ Single",
        "search_placeholder":"🔍 Search in file...",
        # Toolbar tooltips
        "tip_back":          "Back (Alt+Left)",
        "tip_fwd":           "Forward (Alt+Right)",
        "tip_open":          "Open markdown file",
        "tip_edit_toggle":   "Edit/Preview toggle (Ctrl+E)",
        "tip_delete":        "Delete current file",
        "tip_sidebar":       "Show/hide sidebar",
        "tip_split":         "Toggle split editor/preview (Ctrl+Shift+S)",
        # Editor toolbar tooltips
        "tip_bold":          "Bold (Ctrl+B)",
        "tip_italic":        "Italic (Ctrl+I)",
        "tip_strike":        "Strikethrough",
        "tip_link":          "Insert Link (Ctrl+K)",
        "tip_img":           "Insert Image",
        "tip_code":          "Code (Ctrl+`)",
        "tip_bullet":        "Bullet List",
        "tip_num":           "Numbered List",
        "tip_table":         "Insert Table",
        "tip_hr":            "Horizontal Line",
        "tip_quote":         "Blockquote",
        "tip_font":          "Editor font size",
        "tip_color":         "Text Color",
        "tip_special":       "Special Characters",
        # Status bar
        "status_ready":      "Ready 🚀",
        "status_loaded":     "Loaded: {path}",
        "status_edit":       "Edit mode: {name}",
        "status_preview":    "Preview: {name}",
        "status_reloaded":   "Reloaded: {name}",
        "status_saved":      "Saved: {name}",
        "status_trashed":    "Sent to trash: {name}",
        "status_searching":  "Searching: '{term}'...",
        "status_found":      "Found: '{term}' ({count} places)",
        "status_folder":     "Folder: {path}",
        "status_settings":   "Settings saved! ⚙️",
        "status_pdf_saved":  "PDF saved: {path}",
        "word_count":        "Words: {words}  ·  ~{minutes} min read",
        # Dialog titles
        "dlg_confirm_delete":"Confirm Delete",
        "dlg_error":         "Error",
        "dlg_warning":       "Warning",
        "dlg_search":        "Search",
        "dlg_success":       "Success",
        "dlg_insert_link":   "Insert Link",
        "dlg_insert_img":    "Insert Image",
        # Dialog messages
        "msg_no_file_edit":  "No file is open for editing!",
        "msg_no_file_delete":"No file is open for deletion!",
        "msg_no_file_search":"No file is open for search!",
        "msg_confirm_delete":"Are you sure you want to delete:\n\n📄 {name}\n\n{path}\n\nFile will be sent to Trash.",
        "msg_delete_ok":     "File sent to trash!",
        "msg_delete_err":    "Cannot delete file: {err}",
        "msg_not_found":     "Text '{term}' not found in file.",
        "msg_save_err":      "Cannot save: {err}",
        "msg_read_err":      "Cannot read file:\n{err}",
        "msg_file_missing":  "File does not exist:\n{path}",
        # Insert dialogs
        "insert_link_url":   "URL:",
        "insert_img_url":    "Image URL or path:",
        # Settings dialog
        "settings_title":    "Settings - NZ-MDviewer",
        "settings_lang_group":   "🌐 Language",
        "settings_lang_label":   "Interface language:",
        "settings_lang_note":    "Language change requires restart",
        "settings_sidebar_group":"📁 Sidebar Settings",
        "settings_show_sidebar": "Show sidebar",
        "settings_auto_hide":    "Auto-hide sidebar on startup",
        "settings_remember_pos": "Remember sidebar position",
        "settings_preview_group":"👁️ Preview Settings",
        "settings_auto_refresh": "Auto-refresh on file change",
        "settings_default_zoom": "Default zoom:",
        "settings_save":         "💾 Save",
        "settings_cancel":       "❌ Cancel",
        # About dialog
        "about_title":       "About NZ-MDviewer",
        "about_body": (
            "<p>Markdown viewer with system theme support.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Automatic light/dark theme following system</li>"
            "<li>Syntax highlighting</li>"
            "<li>Built-in Edit mode with markdown toolbar</li>"
            "<li>Back/Forward file navigation</li>"
            "<li>Recent files list</li>"
            "<li>Word count &amp; reading time</li>"
            "<li>Export to PDF</li>"
            "<li>Split view (editor + preview)</li>"
            "<li>Auto-reload on file change</li>"
            "<li>Drag &amp; Drop support</li>"
            "<li>Task lists, tables, footnotes...</li>"
            "</ul>"
        ),
        # Context menu
        "ctx_open_link":     "Open link in browser",
        "ctx_copy_link":     "Copy link",
        "ctx_copy_sel":      "Copy selected  (Ctrl+C)",
        "ctx_select_all":    "Select all  (Ctrl+A)",
        "ctx_open_browser":  "Open in browser",
        "ctx_zoom_in":       "Zoom In",
        "ctx_zoom_out":      "Zoom Out",
        "ctx_zoom_reset":    "Reset Zoom",
        "ctx_reload":        "Reload",
        # Special chars categories
        "spec_arrows":  "Arrows",
        "spec_math":    "Math",
        "spec_symbols": "Symbols",
        "spec_greek":   "Greek",
        "spec_emoji":   "Emoji",
        # Welcome screen (Markdown text)
        "welcome": (
            "# 👋 Welcome to NZ-MDviewer!\n\n"
            "## How to use:\n\n"
            "1. **Select folder** on the left (or `File → Change Folder`)\n"
            "2. **Click a .md file** to preview it\n"
            "3. **Drag & Drop** — drag a file directly into the window\n\n"
            "## Shortcuts:\n\n"
            "| Action | Shortcut |\n"
            "|--------|----------|\n"
            "| Open file | `Ctrl+O` |\n"
            "| Edit/Preview | `Ctrl+E` |\n"
            "| Split View | `Ctrl+Shift+S` |\n"
            "| Save (edit) | `Ctrl+S` |\n"
            "| Export PDF | `Ctrl+Shift+E` |\n"
            "| Back | `Alt+Left` |\n"
            "| Forward | `Alt+Right` |\n"
            "| Reload | `F5` / `Ctrl+R` |\n"
            "| Zoom In | `Ctrl++` |\n"
            "| Zoom Out | `Ctrl+-` |\n"
            "| Reset Zoom | `Ctrl+0` |\n"
            "| Quit | `Ctrl+Q` |\n\n"
            "---\n\n"
            "*NZ-MDviewer v{version}*\n"
        ),
    },
    "bs": {
        # Menus
        "menu_file":         "&Fajl",
        "menu_view":         "&Pregled",
        "menu_settings":     "&Postavke",
        "menu_help":         "&Pomoć",
        # File menu
        "open_file":         "Otvori fajl",
        "reload":            "Reload",
        "change_folder":     "Promijeni folder",
        "recent_files":      "Nedavni fajlovi",
        "clear_recent":      "Očisti listu",
        "no_recent_files":   "(Nema nedavnih fajlova)",
        "export_pdf":        "Izvezi kao PDF",
        "exit":              "Izlaz",
        # View menu
        "zoom_in":           "Zoom In",
        "zoom_out":          "Zoom Out",
        "zoom_reset":        "Reset Zoom",
        "toggle_sidebar":    "Sakrij/Prikaži sidebar",
        # Settings menu
        "sidebar_menu":      "Sidebar",
        "preferences":       "Postavke",
        # Help menu
        "about":             "O programu",
        # Toolbar buttons
        "btn_back":          "◀ Nazad",
        "btn_fwd":           "▶ Naprijed",
        "btn_open":          "📂 Otvori",
        "btn_edit":          "✏️ Edit",
        "btn_preview":       "👁️ Preview",
        "btn_delete":        "🗑️ Obriši",
        "btn_sidebar":       "📁 Sidebar",
        "btn_split":         "⊟ Podijeli",
        "btn_single":        "⊞ Jedan",
        "search_placeholder":"🔍 Traži u fajlu...",
        # Toolbar tooltips
        "tip_back":          "Nazad (Alt+Left)",
        "tip_fwd":           "Naprijed (Alt+Right)",
        "tip_open":          "Otvori markdown fajl",
        "tip_edit_toggle":   "Edit/Preview toggle (Ctrl+E)",
        "tip_delete":        "Obriši trenutni fajl",
        "tip_sidebar":       "Prikaži/sakrij sidebar",
        "tip_split":         "Podijeljeni editor/preview (Ctrl+Shift+S)",
        # Editor toolbar tooltips
        "tip_bold":          "Podebljano (Ctrl+B)",
        "tip_italic":        "Ukošeno (Ctrl+I)",
        "tip_strike":        "Precrtan tekst",
        "tip_link":          "Ubaci link (Ctrl+K)",
        "tip_img":           "Ubaci sliku",
        "tip_code":          "Kod (Ctrl+`)",
        "tip_bullet":        "Tačkasta lista",
        "tip_num":           "Numerisana lista",
        "tip_table":         "Ubaci tabelu",
        "tip_hr":            "Horizontalna linija",
        "tip_quote":         "Citat",
        "tip_font":          "Veličina fonta editora",
        "tip_color":         "Boja teksta",
        "tip_special":       "Specijalni karakteri",
        # Status bar
        "status_ready":      "Spreman za rad 🚀",
        "status_loaded":     "Učitano: {path}",
        "status_edit":       "Edit mod: {name}",
        "status_preview":    "Preview: {name}",
        "status_reloaded":   "Reloaded: {name}",
        "status_saved":      "Sačuvano: {name}",
        "status_trashed":    "Poslan u smeće: {name}",
        "status_searching":  "Tražim: '{term}'...",
        "status_found":      "Pronađeno: '{term}' ({count} mjesta)",
        "status_folder":     "Folder: {path}",
        "status_settings":   "Postavke sačuvane! ⚙️",
        "status_pdf_saved":  "PDF sačuvan: {path}",
        "word_count":        "Riječi: {words}  ·  ~{minutes} min čitanja",
        # Dialog titles
        "dlg_confirm_delete":"Potvrdi brisanje",
        "dlg_error":         "Greška",
        "dlg_warning":       "Upozorenje",
        "dlg_search":        "Pretraga",
        "dlg_success":       "Uspjeh",
        "dlg_insert_link":   "Ubaci link",
        "dlg_insert_img":    "Ubaci sliku",
        # Dialog messages
        "msg_no_file_edit":  "Nema otvorenog fajla za editovanje!",
        "msg_no_file_delete":"Nema otvorenog fajla za brisanje!",
        "msg_no_file_search":"Nema otvorenog fajla za pretragu!",
        "msg_confirm_delete":"Jesi li siguran da želiš obrisati:\n\n📄 {name}\n\n{path}\n\nFajl će biti poslan u Smeće (Trash).",
        "msg_delete_ok":     "Fajl poslan u smeće!",
        "msg_delete_err":    "Ne mogu obrisati fajl: {err}",
        "msg_not_found":     "Tekst '{term}' nije pronađen u fajlu.",
        "msg_save_err":      "Ne mogu sačuvati: {err}",
        "msg_read_err":      "Ne mogu pročitati fajl:\n{err}",
        "msg_file_missing":  "Fajl ne postoji:\n{path}",
        # Insert dialogs
        "insert_link_url":   "URL:",
        "insert_img_url":    "Image URL ili putanja:",
        # Settings dialog
        "settings_title":    "Postavke - NZ-MDviewer",
        "settings_lang_group":   "🌐 Jezik / Language",
        "settings_lang_label":   "Interface jezik:",
        "settings_lang_note":    "Promjena jezika zahtijeva restart",
        "settings_sidebar_group":"📁 Sidebar Postavke",
        "settings_show_sidebar": "Prikaži sidebar",
        "settings_auto_hide":    "Automatski sakrij sidebar pri startu",
        "settings_remember_pos": "Zapamti poziciju sidebara",
        "settings_preview_group":"👁️ Preview Postavke",
        "settings_auto_refresh": "Auto-refresh pri promjeni fajla",
        "settings_default_zoom": "Default zoom:",
        "settings_save":         "💾 Sačuvaj",
        "settings_cancel":       "❌ Odustani",
        # About dialog
        "about_title":       "O programu NZ-MDviewer",
        "about_body": (
            "<p>Markdown viewer sa podrškom za sistemsku temu.</p>"
            "<p><b>Funkcije:</b></p>"
            "<ul>"
            "<li>Automatsko praćenje sistemske light/dark teme</li>"
            "<li>Syntax highlighting</li>"
            "<li>Ugrađeni Edit mod sa markdown toolbarom</li>"
            "<li>Back/Forward navigacija između fajlova</li>"
            "<li>Lista nedavnih fajlova</li>"
            "<li>Broj riječi i procjena vremena čitanja</li>"
            "<li>Izvoz u PDF</li>"
            "<li>Podijeljeni prikaz (editor + preview)</li>"
            "<li>Auto-reload kad se fajl promijeni</li>"
            "<li>Drag &amp; Drop podrška</li>"
            "<li>Task liste, tablice, fusnote...</li>"
            "</ul>"
        ),
        # Context menu
        "ctx_open_link":     "Otvori link u browseru",
        "ctx_copy_link":     "Kopiraj link",
        "ctx_copy_sel":      "Kopiraj označeno  (Ctrl+C)",
        "ctx_select_all":    "Označi sve  (Ctrl+A)",
        "ctx_open_browser":  "Otvori u browseru",
        "ctx_zoom_in":       "Zoom In",
        "ctx_zoom_out":      "Zoom Out",
        "ctx_zoom_reset":    "Reset Zoom",
        "ctx_reload":        "Reload",
        # Special chars categories
        "spec_arrows":  "Strelice",
        "spec_math":    "Matematika",
        "spec_symbols": "Simboli",
        "spec_greek":   "Grčki",
        "spec_emoji":   "Emoji",
        # Welcome screen
        "welcome": (
            "# 👋 Dobrodošao u NZ-MDviewer!\n\n"
            "## Kako koristiti:\n\n"
            "1. **Izaberi folder** sa lijeve strane (ili `Fajl → Promijeni Folder`)\n"
            "2. **Klikni na .md fajl** da ga pregledaš\n"
            "3. **Drag & Drop** — možeš i prevući fajl direktno u prozor\n\n"
            "## Prečice:\n\n"
            "| Akcija | Prečica |\n"
            "|--------|---------|\n"
            "| Otvori fajl | `Ctrl+O` |\n"
            "| Edit/Preview | `Ctrl+E` |\n"
            "| Podijeljeni prikaz | `Ctrl+Shift+S` |\n"
            "| Sačuvaj (edit) | `Ctrl+S` |\n"
            "| Izvezi PDF | `Ctrl+Shift+E` |\n"
            "| Nazad | `Alt+Left` |\n"
            "| Naprijed | `Alt+Right` |\n"
            "| Reload | `F5` / `Ctrl+R` |\n"
            "| Zoom In | `Ctrl++` |\n"
            "| Zoom Out | `Ctrl+-` |\n"
            "| Reset Zoom | `Ctrl+0` |\n"
            "| Izlaz | `Ctrl+Q` |\n\n"
            "---\n\n"
            "*NZ-MDviewer v{version}*\n"
        ),
    },
}


def _t(key: str, **kwargs) -> str:
    """Return translated string for the active language, fall back to English."""
    lang = TRANSLATIONS.get(_LANG, TRANSLATIONS["en"])
    text = lang.get(key) or TRANSLATIONS["en"].get(key, key)
    return text.format(**kwargs) if kwargs else text


def set_lang(lang: str) -> None:
    """Set the active language."""
    global _LANG
    if lang in TRANSLATIONS:
        _LANG = lang
