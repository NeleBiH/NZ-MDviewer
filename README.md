# NZ-MDviewer

A desktop Markdown editor and viewer for Linux, built with Python and PySide6.

Write, preview, and manage Markdown files with a GitHub-style theme that automatically follows your system's light/dark mode preference. Features a built-in syntax-highlighted editor with live preview, file browser, PDF export, and full desktop integration.

---

## Features

- **Markdown Preview** — renders with GitHub Light/Dark theme (follows system theme automatically)
- **File Browser** — left panel with tree view for `.md`, `.markdown`, `.mdown`, `.txt` files
- **Split View** — side-by-side editor and live preview (Ctrl+Shift+S)
- **Editor** — syntax-highlighted Markdown editor with line numbers (Fira Code font)
- **Auto-Reload** — watches files for changes and reloads automatically
- **Recent Files** — File → Recent Files, persists across sessions
- **PDF Export** — File → Export as PDF (Ctrl+Shift+E)
- **Word Count** — live word/char count + estimated reading time in status bar
- **Zoom** — Ctrl+/- or toolbar controls
- **Navigation** — Back/Forward between visited files (Alt+Left / Alt+Right)
- **Drag & Drop** — drag `.md` and `.txt` files onto the window to open them
- **Desktop Integration** — opens `.md` files from file manager, right-click "Open With", MIME association

## Screenshots

*TODO: add screenshots*

---

## Requirements

**System packages** (Arch/CachyOS/Manjaro):
```bash
sudo pacman -S pyside6 qt6-webengine python
```

**Debian/Ubuntu:**
```bash
sudo apt install python3-pyside6.qtwebenginewidgets python3-pyside6.qtwebengine
```

**Python packages** (installed automatically by the install script):
- `markdown`
- `pymdown-extensions`
- `pygments`

---

## Installation

```bash
git clone https://github.com/NeleBiH/NZ-MDviewer.git
cd NZ-MDviewer
chmod +x install_uninstall.sh
./install_uninstall.sh --install
```

The installer:
- Creates a venv at `~/.local/share/nzmdviewer/venv/`
- Installs pip dependencies
- Creates `~/.local/bin/nzmdviewer` launcher
- Registers MIME types for `.md` files
- Adds a `.desktop` entry (shows in app menu and file manager "Open With")
- Installs icons to the hicolor theme

### Update

```bash
./install_uninstall.sh --update
```

Settings (`~/.local/share/nzmdviewer/settings.json`) are preserved across updates.

### Uninstall

```bash
./install_uninstall.sh --uninstall
```

---

## Usage

```bash
# Open file browser
nzmdviewer

# Open a specific file
nzmdviewer /path/to/file.md
```

Or open `.md` files directly from your file manager (Dolphin, Nautilus, etc.).

---

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| Ctrl+O | Open file |
| Ctrl+S | Save (in editor) |
| Ctrl+Shift+S | Toggle Split View |
| Ctrl+Shift+E | Export as PDF |
| Ctrl+B | Toggle sidebar |
| Ctrl++ / Ctrl+- | Zoom in/out |
| Ctrl+0 | Reset zoom |
| Alt+Left | Back |
| Alt+Right | Forward |
| F5 | Reload current file |

---

## Project Structure

```
NZ-MDviewer/
├── NZ-MDviewer.py     # Entry point
├── __init__.py         # VERSION, APP_NAME
├── deps.py             # Dependency check
├── translations.py     # i18n (en, bs)
├── syntax.py           # Markdown syntax highlighter
├── editor.py           # Editor widget with line numbers
├── web.py              # Custom WebEngine page + slide animation container
├── styles.py           # CSS (GitHub Light/Dark, @media prefers-color-scheme)
├── settings_mgr.py     # Settings load/save (~/.local/share/nzmdviewer/settings.json)
├── main_window.py      # Main window
└── icons/              # App icons (16–512px PNG + SVG)
```

---

## Development

Run directly without installing:

```bash
python3 NZ-MDviewer/NZ-MDviewer.py
```

See [dev_log.md](dev_log.md) for full changelog, architecture notes, and known issues.

---

## License

MIT
