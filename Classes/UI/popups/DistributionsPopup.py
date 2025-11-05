# DistributionPopup.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from Classes.StaticData import DISTRIBUTION_TYPES  # ["Flat","Gaussian","Exponential","Manual","File"]

class DistributionPopup(QDialog):
    def __init__(self, parent, on_create=None, existing_names=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Create Distribution")
        self.setMinimumSize(360, 180)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.on_create = on_create
        self.existing_names = set(existing_names or [])

        font_size = getattr(parent, "font_size_slider", None)
        self.font = QFont("Arial", font_size.value() if font_size else 12)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Name
        name_label = QLabel("Distribution Name:")
        name_label.setFont(self.font)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g. my_gauss")
        self.name_edit.setFont(self.font)
        layout.addWidget(name_label)
        layout.addWidget(self.name_edit)

        # Type (immutable after creation — we’ll store it as a Label param on the child)
        type_label = QLabel("Type:")
        type_label.setFont(self.font)
        self.type_combo = QComboBox()
        self.type_combo.setFont(self.font)
        self.type_combo.addItems(DISTRIBUTION_TYPES)
        layout.addWidget(type_label)
        layout.addWidget(self.type_combo)

        # Create
        create_btn = QPushButton("Create")
        create_btn.setFont(self.font)
        create_btn.clicked.connect(self._handle_create)
        layout.addWidget(create_btn)

    def _handle_create(self):
        name = (self.name_edit.text() or "").strip()
        if not name:
            # keep it simple; you already log in your console elsewhere if needed
            return

        # ensure unique name (foo, foo_2, foo_3, …)
        base = name
        i = 2
        while name in self.existing_names:
            name = f"{base}_{i}"
            i += 1

        dtype = self.type_combo.currentText()
        if self.on_create:
            self.on_create(name, dtype)
        self.accept()