"""
Markdown editor widget with line numbers and syntax highlighting.
"""
from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtGui import QFont, QPainter
from PySide6.QtCore import Qt, QRect, QSize

from syntax import MarkdownHighlighter, LineNumberArea


class MarkdownEditor(QPlainTextEdit):
    """Editor with line numbers and markdown syntax highlighting."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.updateLineNumberAreaWidth(0)

        font = QFont("Fira Code", 13)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)

        self.highlighter = MarkdownHighlighter(self.document())
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * 4)

    def lineNumberAreaWidth(self):
        digits = len(str(max(1, self.blockCount())))
        return 3 + self.fontMetrics().horizontalAdvance('9') * max(digits, 3) + 10

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(
                0, rect.y(), self.line_number_area.width(), rect.height()
            )
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height())
        )

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), self.palette().alternateBase().color())
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(
            self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        )
        bottom = top + round(self.blockBoundingRect(block).height())
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(self.palette().placeholderText().color())
                painter.drawText(
                    0, top, self.line_number_area.width() - 5,
                    self.fontMetrics().height(), Qt.AlignRight, number,
                )
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1
