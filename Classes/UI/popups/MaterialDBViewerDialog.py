from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QTableView, QPushButton, QHBoxLayout
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt

class MaterialDBViewerDialog(QDialog):
    def __init__(self, parent, gmat_db):
        super().__init__(parent)
        self.setWindowTitle("Material Database")
        self.setModal(True)
        self.resize(800, 600)

        self.gmat_db = gmat_db

        layout = QVBoxLayout(self)

        # Tabs: Elements | Materials
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Elements table
        self.elements_view = QTableView()
        self.elements_view.setModel(self._build_elements_model())
        self.elements_view.setSortingEnabled(True)
        tabs.addTab(self.elements_view, "Elements")

        # Materials table
        self.materials_view = QTableView()
        self.materials_view.setModel(self._build_materials_model())
        self.materials_view.setSortingEnabled(True)
        tabs.addTab(self.materials_view, "Materials")

        # Close
        btns = QHBoxLayout()
        btns.addStretch(1)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btns.addWidget(close_btn)
        layout.addLayout(btns)

    def _build_elements_model(self):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Name", "Symbol", "Z", "Molar Mass"])

        for elem in self.gmat_db.element_DB.values():
            row = [
                QStandardItem(str(elem.name)),
                QStandardItem(str(elem.symbol)),
                QStandardItem(str(elem.atomic_number)),
                QStandardItem(str(elem.atomic_weight)),
            ]
            for it in row:
                it.setEditable(False)
            model.appendRow(row)

        return model

    def _build_materials_model(self):
        # For now materials only have a name in your class.
        # Later you can extend with density, composition, etc.
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Name"])

        for mat in self.gmat_db.material_DB.values():
            it = QStandardItem(str(mat.name))
            it.setEditable(False)
            model.appendRow([it])

        return model