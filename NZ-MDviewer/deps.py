"""
Dependency checker — no Qt imports at module level.
Must be imported and called BEFORE any Qt import.
"""
import sys


def provjeri_dependencije():
    """Provjerava da li su sve potrebne biblioteke instalirane"""
    nedostaje = []

    try:
        import markdown
    except ImportError:
        nedostaje.append("markdown")

    try:
        import pymdownx
    except ImportError:
        nedostaje.append("pymdown-extensions")

    try:
        import pygments
    except ImportError:
        nedostaje.append("pygments")

    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        nedostaje.append("PySide6")

    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView
    except ImportError:
        nedostaje.append("PySide6-WebEngine")

    if nedostaje:
        print("=" * 50)
        print("FALE TI BIBLIOTEKE, BRATE!")
        print("=" * 50)
        print("\nPokreni ovo da instaliraš sve što treba:\n")
        print(f"  pip install {' '.join(nedostaje)}")
        print("\nIli ako koristiš system Python:")
        print(f"  pip install {' '.join(nedostaje)} --break-system-packages")
        print("=" * 50)
        sys.exit(1)
