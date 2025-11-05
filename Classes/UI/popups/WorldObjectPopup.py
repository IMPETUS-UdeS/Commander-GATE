from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QListWidget, QListWidgetItem, QWidget, QSizePolicy, QScrollArea, QFrame
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from Classes.GObjectCreator import GObjectCreator
from Classes.StyleSheets import WORLD_OBJECT_WINDOW_STYLESHEET
from Classes.RepeaterParameterBuilder import RepeaterParameterBuilder

class WorldObjectPopup(QDialog):
    def __init__(self, parent, material_db, on_create_callback=None, existing_names=None):
        super().__init__(parent)
        
        self.setModal(True)
        self.setWindowTitle("Create World Object")
        self.setMinimumSize(400, 200)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.font_size = parent.font_size_slider.value()
        self.material_db = material_db
        self.on_create_callback = on_create_callback
        self.existing_names = existing_names or []

        self.init_ui()
        self.create_button.clicked.connect(self.handle_create)

    def init_ui(self):
        self.setStyleSheet(WORLD_OBJECT_WINDOW_STYLESHEET)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        label_font = QFont("Arial", self.font_size)

        # Section: Name
        name_label = QLabel("Object Name:")
        name_label.setFont(label_font)
        self.name_input = QLineEdit()
        self.name_input.setFont(label_font)
        self.name_input.setPlaceholderText("Enter object name")
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)

        # Section: Shape
        shape_label = QLabel("Shape:")
        shape_label.setFont(label_font)
        self.shape_dropdown = QComboBox()
        self.shape_dropdown.setFont(label_font)
        self.shape_dropdown.addItems([
            "box", "sphere", "cylinder", "cone", "ellipsoid",
            "elliptical tube", "hexagon", "wedge", "tet-mesh-box"
        ])
        layout.addWidget(shape_label)
        layout.addWidget(self.shape_dropdown)

        # Section: Repeater
        repeater_label = QLabel("Repeater:")
        repeater_label.setFont(label_font)
        self.repeater_dropdown = QComboBox()
        self.repeater_dropdown.setFont(label_font)
        self.repeater_dropdown.addItems([" - ", "linear", "ring", "cubicArray", "quadrant", "sphere", "generic"])
        layout.addWidget(repeater_label)
        layout.addWidget(self.repeater_dropdown)

        # Button
        self.create_button = QPushButton("Create")
        self.create_button.setFont(label_font)
        layout.addWidget(self.create_button)

    def handle_create(self):
        name = self.name_input.text().strip()
        if not name:
            print("Please enter a name.")
            return

        if name in self.existing_names:
            i = 1
            new_name = f"{name}{i}"
            while new_name in self.existing_names:
                i += 1
                new_name = f"{name}{i}"
            name = new_name

        shape = self.shape_dropdown.currentText()
        repeater_type = self.repeater_dropdown.currentText()

        new_obj = GObjectCreator.create_world_daughter(name, shape, self.material_db)

        if repeater_type != " - ":
            repeater_params = RepeaterParameterBuilder.get_parameters(name, repeater_type)
            new_obj.parameters.extend(repeater_params)

        if self.on_create_callback:
            self.on_create_callback(new_obj)

        self.accept()