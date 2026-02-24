"""
Markdown syntax highlighter and line number area widget.
Colors chosen to be readable on both light and dark backgrounds.
"""
import re

from PySide6.QtGui import (
    QSyntaxHighlighter,
    QTextCharFormat,
    QFont,
    QColor,
)
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QSize


class MarkdownHighlighter(QSyntaxHighlighter):
    """Syntax highlighting for markdown in the editor."""

    def __init__(self, document):
        super().__init__(document)
        self.rules = []

        # Headers (#, ##, ### etc.) — GitHub blue, visible on both themes
        for i in range(1, 7):
            fmt = QTextCharFormat()
            fmt.setForeground(QColor("#0969da"))
            fmt.setFontWeight(QFont.Bold)
            self.rules.append((re.compile(rf'^{"#" * i}\s.+'), fmt))

        # Bold **text** or __text__ — bold weight only, no color override
        bold_fmt = QTextCharFormat()
        bold_fmt.setFontWeight(QFont.Bold)
        self.rules.append((re.compile(r'\*\*.+?\*\*'), bold_fmt))
        self.rules.append((re.compile(r'__.+?__'), bold_fmt))

        # Italic *text* or _text_
        italic_fmt = QTextCharFormat()
        italic_fmt.setFontItalic(True)
        self.rules.append((re.compile(r'(?<!\*)\*([^\*]+)\*(?!\*)'), italic_fmt))
        self.rules.append((re.compile(r'(?<!_)_([^_]+)_(?!_)'), italic_fmt))

        # Strikethrough ~~text~~
        strike_fmt = QTextCharFormat()
        strike_fmt.setFontStrikeOut(True)
        strike_fmt.setForeground(QColor("#6e7781"))
        self.rules.append((re.compile(r'~~.+?~~'), strike_fmt))

        # Inline code `text` — red, visible on both themes
        code_fmt = QTextCharFormat()
        code_fmt.setForeground(QColor("#cf222e"))
        self.rules.append((re.compile(r'`[^`]+`'), code_fmt))

        # Links [text](url) — GitHub blue
        link_fmt = QTextCharFormat()
        link_fmt.setForeground(QColor("#0969da"))
        link_fmt.setFontUnderline(True)
        self.rules.append((re.compile(r'\[([^\]]+)\]\([^\)]+\)'), link_fmt))

        # Images ![alt](url)
        img_fmt = QTextCharFormat()
        img_fmt.setForeground(QColor("#6e7781"))
        self.rules.append((re.compile(r'!\[([^\]]*)\]\([^\)]+\)'), img_fmt))

        # Lists - * + and 1. — neutral gray
        list_fmt = QTextCharFormat()
        list_fmt.setForeground(QColor("#6e7781"))
        self.rules.append((re.compile(r'^\s*[-*+]\s'), list_fmt))
        self.rules.append((re.compile(r'^\s*\d+\.\s'), list_fmt))

        # Blockquote > text — neutral gray
        quote_fmt = QTextCharFormat()
        quote_fmt.setForeground(QColor("#6e7781"))
        self.rules.append((re.compile(r'^>\s.*'), quote_fmt))

        # HR ---, ***, ___
        hr_fmt = QTextCharFormat()
        hr_fmt.setForeground(QColor("#6e7781"))
        self.rules.append((re.compile(r'^(---|\*\*\*|___)$'), hr_fmt))

        # Code block delimiter ```
        codeblock_fmt = QTextCharFormat()
        codeblock_fmt.setForeground(QColor("#cf222e"))
        self.rules.append((re.compile(r'^```.*$'), codeblock_fmt))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)


class LineNumberArea(QWidget):
    """Line number gutter for the editor."""

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)
