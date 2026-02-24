"""
Custom WebEngine page and slide-animation content container.
"""
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import (
    Qt,
    QUrl,
    Signal,
    QPropertyAnimation,
    QEasingCurve,
    QParallelAnimationGroup,
    QRect,
)


class BalkanMDPage(QWebEnginePage):
    """Custom page for intercepting .md links."""

    md_link_clicked = Signal(str)

    def acceptNavigationRequest(self, url, type_, isMainFrame):
        if type_ != QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            return True

        # Anchor links within page
        if url.hasFragment():
            local_path = url.toLocalFile()
            if not local_path or local_path.endswith('/'):
                return True

        # Local .md file links
        if url.isLocalFile():
            path = url.toLocalFile()
            if path.lower().endswith(('.md', '.markdown', '.mdown')):
                self.md_link_clicked.emit(path)
                return False

        # External links — open in browser
        if url.scheme() in ('http', 'https', 'mailto'):
            QDesktopServices.openUrl(url)
            return False

        return True


class ContentContainer(QWidget):
    """Container with slide animation between preview and editor widgets."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.preview = None
        self.editor_panel = None
        self._current = 'preview'
        self._anim_group = None

    def setChildren(self, preview, editor_panel):
        self.preview = preview
        self.editor_panel = editor_panel
        preview.setParent(self)
        editor_panel.setParent(self)
        # Always reset to preview state so _layoutCurrent() shows the right widget
        self._current = 'preview'
        self.preview.show()
        self.editor_panel.hide()
        self._layoutCurrent()

    def _layoutCurrent(self):
        r = self.rect()
        if self._current == 'preview':
            self.preview.setGeometry(r)
        else:
            self.editor_panel.setGeometry(r)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._layoutCurrent()

    def slideTo(self, target, callback=None):
        if target == self._current:
            if callback:
                callback()
            return

        w = self.width()
        h = self.height()

        if target == 'editor':
            from_w = self.preview
            to_w = self.editor_panel
            from_end = QRect(w, 0, w, h)
            to_start = QRect(-w, 0, w, h)
        else:
            from_w = self.editor_panel
            to_w = self.preview
            from_end = QRect(-w, 0, w, h)
            to_start = QRect(w, 0, w, h)

        to_w.setGeometry(to_start)
        to_w.show()

        anim1 = QPropertyAnimation(from_w, b"geometry")
        anim1.setDuration(300)
        anim1.setStartValue(QRect(0, 0, w, h))
        anim1.setEndValue(from_end)
        anim1.setEasingCurve(QEasingCurve.OutCubic)

        anim2 = QPropertyAnimation(to_w, b"geometry")
        anim2.setDuration(300)
        anim2.setStartValue(to_start)
        anim2.setEndValue(QRect(0, 0, w, h))
        anim2.setEasingCurve(QEasingCurve.OutCubic)

        self._anim_group = QParallelAnimationGroup()
        self._anim_group.addAnimation(anim1)
        self._anim_group.addAnimation(anim2)

        def on_finished():
            from_w.hide()
            self._current = target
            self._layoutCurrent()
            if callback:
                callback()

        self._anim_group.finished.connect(on_finished)
        self._anim_group.start()
