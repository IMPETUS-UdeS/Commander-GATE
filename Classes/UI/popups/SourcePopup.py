from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from Classes.StaticData import SOURCE_TYPES

class SourcePopup(QDialog):
    def __init__(self, parent, on_create):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Add Source")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.on_create = on_create
        fs = parent.font_size_slider.value() if hasattr(parent, "font_size_slider") else 14

        lay = QVBoxLayout(self)
        name_lbl = QLabel("Source name:"); name_lbl.setFont(QFont("Arial", fs))
        self.name_in = QLineEdit(); self.name_in.setFont(QFont("Arial", fs))
        type_lbl = QLabel("Source type:"); type_lbl.setFont(QFont("Arial", fs))
        self.type_dd = QComboBox(); self.type_dd.addItems(SOURCE_TYPES); self.type_dd.setFont(QFont("Arial", fs))
        btn = QPushButton("Create"); btn.setFont(QFont("Arial", fs)); btn.clicked.connect(self._ok)

        for w in (name_lbl, self.name_in, type_lbl, self.type_dd, btn):
            lay.addWidget(w)

    def _ok(self):
        name = self.name_in.text().strip() or "source1"
        src_type = self.type_dd.currentText()
        self.on_create(name, src_type)
        self.accept()