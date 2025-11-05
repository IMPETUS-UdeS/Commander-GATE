from PyQt6.QtWidgets import QToolBar
from PyQt6.QtGui import QAction

class ToolbarBuilder:
    def __init__(self, parent):
        self.parent = parent
        
        
    def _add_action(self, toolbar: QToolBar, name: str, tooltip: str, cb):
        action = QAction(name, self.parent)
        action.setStatusTip(tooltip)
        action.triggered.connect(cb)
        toolbar.addAction(action)
        return action
    
    def build_toolbar(self, toolbar: QToolBar,*, on_import, on_export, on_apply, on_run, on_toggle_theme, on_exit, on_add, on_view_material_db=None):
        actions = {}
        actions["import"] = self._add_action(toolbar, "Import", "Import Json configuration file", on_import)
        actions["export"] = self._add_action(toolbar, "Export", "Export configurations as Json", on_export)
        actions["apply"] = self._add_action(toolbar, "Apply Configurations", "Apply Configurations as JSON file", on_apply)
        actions["run"] = self._add_action(toolbar, "Run Simulation", "Run the GATE simulation", on_run)
        actions["toggle"] = self._add_action(toolbar, "Toggle Theme", "Switch between light and dark mode", on_toggle_theme)
        if on_view_material_db:
            self.action_view_mat = toolbar.addAction("View Materials")
            self.action_view_mat.triggered.connect(on_view_material_db)
            # start disabled until a DB is loaded:
            self.action_view_mat.setEnabled(False)
        actions["exit"] = self._add_action(toolbar, "Exit", "Exit the application", on_exit)
        actions["add"] = self._add_action(toolbar, "Add Geometry", "Create World Object", on_add)
        return actions