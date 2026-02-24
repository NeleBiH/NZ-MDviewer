# NZ-MDmaster

![Version](https://img.shields.io/badge/Version-0.3.0-blue?style=flat-square)
![Python](https://img.shields.io/badge/Python-3-3776AB?style=flat-square&logo=python&logoColor=white)
![GUI](https://img.shields.io/badge/GUI-PySide6%20%2F%20Qt6-41CD52?style=flat-square&logo=qt&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-brightgreen?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Linux-FCC624?style=flat-square&logo=linux&logoColor=black)

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

**Split View — dark theme**
![Split View dark](screenshots/split-view-dark.png)

**Preview — light theme**
![Preview light](screenshots/preview-light.png)

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
git clone https://github.com/NeleBiH/NZ-MDmaster.git
cd NZ-MDmaster
chmod +x install_uninstall.sh
./install_uninstall.sh --install
```

The installer:
- Creates a venv at `~/.local/share/nzmdmaster/venv/`
- Installs pip dependencies
- Creates `~/.local/bin/nzmdmaster` launcher
- Registers MIME types for `.md` files
- Adds a `.desktop` entry (shows in app menu and file manager "Open With")
- Installs icons to the hicolor theme

### Update

```bash
./install_uninstall.sh --update
```

Settings (`~/.local/share/nzmdmaster/settings.json`) are preserved across updates.

### Uninstall

```bash
./install_uninstall.sh --uninstall
```

---

## Usage

```bash
# Open file browser
nzmdmaster

# Open a specific file
nzmdmaster /path/to/file.md
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
NZ-MDmaster/
├── NZ-MDmaster.py     # Entry point
├── __init__.py         # VERSION, APP_NAME
├── deps.py             # Dependency check
├── translations.py     # i18n (en, bs)
├── syntax.py           # Markdown syntax highlighter
├── editor.py           # Editor widget with line numbers
├── web.py              # Custom WebEngine page + slide animation container
├── styles.py           # CSS (GitHub Light/Dark, @media prefers-color-scheme)
├── settings_mgr.py     # Settings load/save (~/.local/share/nzmdmaster/settings.json)
├── main_window.py      # Main window
└── icons/              # App icons (16–512px PNG + SVG)
```

---

## Development

Run directly without installing:

```bash
python3 NZ-MDmaster/NZ-MDmaster.py
```

See [dev_log.md](dev_log.md) for full changelog, architecture notes, and known issues.

---

## License

MIT
