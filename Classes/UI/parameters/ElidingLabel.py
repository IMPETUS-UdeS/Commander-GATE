from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QFontMetrics
from PyQt6.QtCore import Qt

class ElidingLabel(QLabel):
    def __init__(self, text="", parent=None, elide_mode=Qt.TextElideMode.ElideRight):
        super().__init__(text, parent)
        self._full_text = text
        self._elide_mode = elide_mode
        self.setWordWrap(False)  # single line
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.setToolTip(text)

    def setText(self, text: str) -> None:
        self._full_text = text or ""
        self.setToolTip(self._full_text)
        super().setText(self._full_text)  # temporary; will be elided on resize
        self._apply_elide()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._apply_elide()

    def _apply_elide(self):
        fm = QFontMetrics(self.font())
        elided = fm.elidedText(self._full_text, self._elide_mode, max(0, self.width()))
        super().setText(elided)