from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QListWidget, QListWidgetItem, QWidget
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from Classes.StaticData import PHYSICS_PROCESSES
from Classes.GateParameter import GateParameter
import Classes.StyleSheets as Style

class PhysicsProcessPopup(QDialog):
    def __init__(self, parent, physics_gate_object, on_change_callback):
        super().__init__(parent)
        self.setWindowTitle("Edit Physics Processes")
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setMinimumSize(600, 400)
        self.physics_obj = physics_gate_object
        self.on_change_callback = on_change_callback
        self.font_size = parent.font().pointSize()
        self.default_font = QFont("Arial", self.font_size)
        self.setStyleSheet(Style.LIGHT_MODE_STYLESHEET)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        label = QLabel("Add a physics process:")
        label.setFont(self.default_font)
        layout.addWidget(label)

        self.process_dropdown = QComboBox()
        self.process_dropdown.setFont(self.default_font)
        self.process_dropdown.setMinimumHeight(self.font_size * 2)
        self.process_dropdown.addItems([
            p for p in PHYSICS_PROCESSES.keys() if not self._already_added(p)
        ])
        layout.addWidget(self.process_dropdown)

        add_button = QPushButton("Add Process")
        add_button.setFont(self.default_font)
        add_button.setFixedHeight(self.font_size * 2)
        add_button.clicked.connect(self.add_process)
        layout.addWidget(add_button)

        layout.addWidget(self._styled_label("Existing Processes:"))

        self.process_list = QListWidget()
        self.process_list.setFont(self.default_font)

        for p in self._get_existing_processes():
            item = QListWidgetItem()
            widget = QWidget()
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(5, 2, 5, 2)
            row_layout.setSpacing(10)

            process_label = QLabel(p)
            process_label.setFont(self.default_font)

            remove_btn = QPushButton("❌")
            remove_btn.setFont(self.default_font)
            remove_btn.setFixedWidth(30)
            remove_btn.setStyleSheet("font-size: 14px; color: red; border: none; background: transparent;")
            remove_btn.clicked.connect(lambda _, proc=p: self.remove_process(proc))

            row_layout.addWidget(process_label)
            row_layout.addStretch()
            row_layout.addWidget(remove_btn)

            widget.setLayout(row_layout)
            self.process_list.addItem(item)
            self.process_list.setItemWidget(item, widget)

        layout.addWidget(self.process_list)
        self.setLayout(layout)

    def _styled_label(self, text):
        label = QLabel(text)
        label.setFont(self.default_font)
        return label

    def _already_added(self, process_name):
        return any(param.path.endswith(process_name)
                   for param in self.physics_obj.parameters if "Process" in param.displayed_name)

    def _get_existing_processes(self):
        return [p.displayed_name.split(" ")[0]
                for p in self.physics_obj.parameters if "Process" in p.displayed_name]

    def add_process(self):
        selected = self.process_dropdown.currentText()
        if selected:
            data = PHYSICS_PROCESSES[selected]
            new_param = GateParameter(
                f"/physics/{selected}", f"{selected} Process",
                ["DropDown", "DropDown"],
                [list(data["process"])[0], list(data["model"])[0]],
                [list(data["process"]), list(data["model"])]
            )
            self.physics_obj.parameters.append(new_param)
            self.on_change_callback()
            self.close()

    def remove_process(self, proc_name):
        self.physics_obj.parameters = [
            p for p in self.physics_obj.parameters
            if not p.displayed_name.startswith(proc_name)
        ]
        self.on_change_callback()
        self.close()