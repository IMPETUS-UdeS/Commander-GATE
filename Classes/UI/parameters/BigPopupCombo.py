from PyQt6.QtCore import Qt, QTimer, QSize, QObject, QEvent
from PyQt6.QtWidgets import QComboBox, QListView, QStyledItemDelegate

class _FixedRowDelegate(QStyledItemDelegate):
    def __init__(self, row_h: int, parent=None):
        super().__init__(parent)
        self._row_h = row_h

    def sizeHint(self, option, index):
        sz = super().sizeHint(option, index)
        # lock the row height; keep whatever width the style wants
        return QSize(sz.width(), self._row_h)
    

class BigPopupCombo(QComboBox):
    """My Janky solution to the ComboBoxes visual bug"""
    def __init__(self, *args, popup_rows: int = 12, min_chars: int = 14, **kwargs):
        super().__init__(*args, **kwargs)
        self._popup_rows = max(1, popup_rows)
        self._min_chars  = max(1, min_chars)

        # Use a clean QListView for the popup
        v = QListView(self)
        v.setVerticalScrollMode(QListView.ScrollMode.ScrollPerPixel)
        v.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        v.setSpacing(0)  # no extra gaps between items
        self.setView(v)

        self.setMaxVisibleItems(self._popup_rows)

        self.setWheelEnabled(False)


    def setWheelEnabled(self, enabled: bool):
        self._wheel_enabled = enabled

    def wheelEvent(self, e):
        if getattr(self, "_wheel_enabled", True) or (self.view() and self.view().isVisible()):
            return super().wheelEvent(e)
        e.ignore()

    def _desired_popup_size(self) -> QSize:
        v  = self.view()
        fm = v.fontMetrics()

        # Deterministic row height
        probe = v.sizeHintForRow(0)
        row_h = max(22, (probe if probe > 0 else fm.height() + 6))

        # rows to show (cap to item count)
        rows = min(self._popup_rows, max(1, self.count()))
        h = rows * row_h + 2 * v.frameWidth()

        # width: longest text or minimum chars
        longest = 0
        m = self.model()
        for r in range(self.count()):
            longest = max(longest, fm.horizontalAdvance(str(m.data(m.index(r, 0)))))
        min_w = fm.horizontalAdvance("M" * self._min_chars)
        w = max(longest + 28, min_w)

        # lock row height via delegate (prevents “giant rows”)
        v.setItemDelegate(_FixedRowDelegate(row_h, v))
        return QSize(w, h)

    def showPopup(self):
        super().showPopup()
        v = self.view()
        container = v.window()  # QFrame with WindowType.Popup
        size = self._desired_popup_size()

        # Apply after Qt lays out (and again if it resizes)
        def apply():
            v.setMinimumHeight(size.height())
            v.setMaximumHeight(size.height())
            v.setMinimumWidth(size.width())
            container.resize(size)

            # put current item at top (avoids blank band “centering”)
            if self.currentIndex() >= 0:
                v.scrollTo(self.model().index(self.currentIndex(), 0),
                           QListView.ScrollHint.PositionAtTop)

        QTimer.singleShot(0, apply)

        # Keep enforcing if the style re-lays out
        class _Filter(QObject):
            def __init__(self, applier): super().__init__(container); self.applier = applier
            def eventFilter(self, obj, ev):
                if ev.type() in (QEvent.Type.Show, QEvent.Type.Resize):
                    QTimer.singleShot(0, self.applier)
                return False
        # Install once per popup show (container is recreated each time)
        f = _Filter(apply)
        container.installEventFilter(f)
        # retain ref so it doesn’t get GC’d immediately
        self._popup_filter = f