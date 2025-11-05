import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QLabel,
    QMenuBar, QStatusBar, QSplitter, QFileDialog, QLabel, 
    QSlider, QToolButton
)
from PyQt6.QtGui import QAction, QFont, QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, QSize
from Classes.UI.popups.PhysicsProcessPopup import PhysicsProcessPopup
from Classes.UI.popups.WorldObjectPopup import WorldObjectPopup
import Classes.StyleSheets as Style


from Classes.UI.actions.toolbar import ToolbarBuilder
from Classes.UI.sections.consoleSection import ConsoleSection
from Classes.UI.sections.hierarchySection import HierarchySection
from Classes.UI.sections.inspectorSection import InspectorSection
from Classes.UI.popups.MaterialDBViewerDialog import MaterialDBViewerDialog
from Classes.IO.project_io import ProjectSerializer, ProjectDeserializer
from Classes.IO.JsonHandler import JsonHandler
from Classes.GateObject import GateObject


class MainWindow(QMainWindow):
    def __init__(self, commander, jsonHandler):
        super().__init__()
        self.cManager = commander
        self.json_handler = jsonHandler
        self.current_theme = "light"
        
        self.default_font_size = 16
        self.setupUi()  # Initialize the UI
    
        
    def write_to_console(self, message):
        """Writes a message to the console"""
        if hasattr(self, "consoleSection") and self.consoleSection:
            self.consoleSection.write(message)
        else:
            print("Error while printing to console")
        

    def setupUi(self):
        """Main UI setup, calls all sub-setup functions."""
        self.setObjectName("CTCommanderWindow")
        self.resize(1200, 1200)
        self.setMinimumSize(QSize(700, 700))

        # Central widget
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.main_layout = QVBoxLayout(self.centralwidget)
        
        #Sections
        self.consoleSection = ConsoleSection(self)
        self.inspectorSection = InspectorSection(self)
        self.hierarchySection = HierarchySection(self)
        
        # Splitters (Hierarchy and Inspector sections)
        top_splitter = QSplitter(Qt.Orientation.Horizontal, self.centralwidget)
        top_splitter.addWidget(self.hierarchySection.widget)
        top_splitter.addWidget(self.inspectorSection.widget)
        top_splitter.setSizes([300, 450])
        
        # Main Splitter (Top views + Console)
        main_splitter = QSplitter(Qt.Orientation.Vertical, self.centralwidget)
        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(self.consoleSection.widget)
        main_splitter.setSizes([500, 300])
        
        self.main_layout.addWidget(main_splitter)

        # Setup toolbar
        self.toolbar_builder = ToolbarBuilder(self)
        self.toolbar = self.addToolBar("CT Toolbar")
        self.toolbar_builder.build_toolbar(
            self.toolbar,
            on_import=lambda: self.browse_file("import_json"),
            on_export=lambda: self.browse_file("export_json"),
            on_apply=lambda: None,
            on_run=lambda: None,
            on_toggle_theme=self.toggle_theme,
            on_view_material_db=self.open_material_db_viewer,
            on_exit=self.close,
            on_add=self.open_create_object_popup,
        )

        self.action_view_mat = getattr(self.toolbar_builder, "action_view_mat", None)
        if self.action_view_mat:
            self.action_view_mat.setEnabled(False)  # disabled until DB is loaded
        
        # Setup menu bar and status bar
        self.menubar = QMenuBar(self)
        self.setMenuBar(self.menubar)

        self.statusbar = QStatusBar(self)
        self.statusbar.addPermanentWidget(QLabel("Font Size:"))
        
        self.font_size_slider = self.setup_font_slider()
        self.statusbar.addPermanentWidget(self.font_size_slider)
        self.setStatusBar(self.statusbar)

        # Set window title and populate the hierarchy tree
        self.setWindowTitle("MainWindow")
        
        # Connect hierarchy events
        self.hierarchySection.tree.itemClicked.connect(self.inspectorSection.populate_parameters)
        self.hierarchySection.tree.itemChanged.connect(self.on_tree_item_check_changed)
        
        # Populate
        if self.cManager.node_tree:
            self.populate_hierarchy_tree(self.cManager.node_tree)

        # Apply theme
        self.apply_theme(self.current_theme)
        self.update_font_size(self.default_font_size)
        
        
    # ======= font slider + updates =======
    def setup_font_slider(self):
        """Create the Font Slider"""
        font_size_slider = QSlider(Qt.Orientation.Horizontal)
        font_size_slider.setMinimum(12)
        font_size_slider.setMaximum(26)
        font_size_slider.setValue(self.default_font_size) #Default
        font_size_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        font_size_slider.setTickInterval(2)
        font_size_slider.setFixedWidth(150)
        font_size_slider.valueChanged.connect(self.update_font_size)
        
        return font_size_slider


    def update_font_size(self, size):
        """Update font in application"""
        new_font = QFont()
        new_font.setPointSize(size)
        
        self.setFont(new_font)
        self.menubar.setFont(new_font)
        self.toolbar.setFont(new_font)
        self.statusbar.setFont(new_font)
        
        # header/list widgets
        self.hierarchySection.label.setFont(new_font)
        self.hierarchySection.tree.setFont(new_font)
        self.inspectorSection.label.setFont(new_font)
        self.inspectorSection.listview.setFont(new_font)
        self.consoleSection.label.setFont(new_font)
        self.consoleSection.list.setFont(new_font)
        
        self.hierarchySection.apply_font(size)
        self.inspectorSection.apply_font(size)
        
        # self.inspectorSection.resize_parameters(size)
        
         # Resize toolbar buttons
        for action in self.toolbar.actions():
            action.setFont(new_font)
            if isinstance(action, QAction):
                tool_button = self.toolbar.widgetForAction(action)
                if isinstance(tool_button, QToolButton):
                    tool_button.setIconSize(QSize(size + 8, size + 8))
        
        current = self.hierarchySection.tree.currentItem()
        if current:
            self.inspectorSection.populate_parameters(current)        
        
    # ======= hierarchy + inspector =======
    def on_tree_item_check_changed(self, item, column: int):
        state = item.checkState(0) == Qt.CheckState.Checked
        self.hierarchySection.set_item_enabled_recursively(item, state)

    def populate_hierarchy_tree(self, node):
        # snapshot
        exp, sel, scroll = self.hierarchySection.snapshot_state()
        
        tree = self.hierarchySection.tree
        tree.setUpdatesEnabled(False)
        try:
            old_block = tree.blockSignals(True)
            self.hierarchySection.populate(node, self.consoleSection.write)
        finally:
            tree.blockSignals(old_block)
            tree.setUpdatesEnabled(True)
            
        #restore
        self.hierarchySection.restore_state(exp, sel, scroll)    
        self.node_tree = node
    

    # ======= theme =======
    def apply_theme(self, theme):
        """Applies light or dark mode styles."""
        self.setStyleSheet(Style.DARK_MODE_STYLESHEET if theme == "dark" else Style.LIGHT_MODE_STYLESHEET)
        self.current_theme = theme

    def toggle_theme(self):
        """Toggles between light and dark mode."""
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme(new_theme)
                
    def _find_project_root(self, start: Path) -> Path:
        """
        Walk up until we find a folder that has 'Classes' (and preferably 'MaterialDB').
        Falls back to the top-most parent if not found.
        """
        for p in [start] + list(start.parents):
            if (p / "Classes").is_dir():
                # if MaterialDB is also here, great; otherwise still treat as root
                return p
        return start.parents[-1]

    def browse_file(self, action):
        """Opens a file dialog and triggers the appropriate import/export method."""
        print("Browse File")
        dlg = QFileDialog(self)

        if action == "export_json":
            dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)   # <-- Save dialog
            dlg.setFileMode(QFileDialog.FileMode.AnyFile)          # allow new file
            dlg.setNameFilter("JSON files (*.json)")
            dlg.setDefaultSuffix("json")
            dlg.selectFile("project.json")
        elif action == "import_json":
            dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
            dlg.setFileMode(QFileDialog.FileMode.ExistingFile)
            dlg.setNameFilter("JSON files (*.json);;All files (*.*)")
        elif action == "import_material_db":
            dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
            dlg.setFileMode(QFileDialog.FileMode.ExistingFile)
            # ... your start dir / filter ...

        if not dlg.exec():
            return

        path = dlg.selectedFiles()[0]
        if action == "export_json" and not path.lower().endswith(".json"):
            path += ".json"

        if action == "export_json":
            self.cManager.export_json(path)
        elif action == "import_json":
            self.cManager.import_json(path)
        elif action == "import_material_db":
            self.cManager.import_material_db(path)


    def open_create_object_popup(self):
        tree = self.hierarchySection.tree
        selected_item = tree.currentItem()
        if not selected_item:
            self.consoleSection.write("Invalid parent item")
            print("Invalid parent item selected.")
            return
            
        parent_obj = selected_item.data(0, Qt.ItemDataRole.UserRole)
        if not parent_obj:
            return
        
        existing_names = [tree.topLevelItem(i).text(0) for i in range(tree.topLevelItemCount())]
        
        dialog = WorldObjectPopup(
            self, 
            self.cManager.get_material_db(), 
            on_create_callback=lambda new_obj: self.add_object_to_tree(new_obj, parent_obj),
            existing_names=existing_names)
        dialog.exec()
        
    
    def add_object_to_tree(self, new_obj, parent_obj):
        parent_obj.add_daughter(new_obj)
        self.consoleSection.write(f"Added object '{new_obj.get_name()}' to '{parent_obj.get_name()}'.")
        
        # Try direct insert. If not found, fall back to repopulate-with-restore.
        item = self.hierarchySection.add_child_item(parent_obj,new_obj)
        if item is not None:
            self.inspectorSection.populate_parameters(item)
            return
        
        if item is None:
            exp, sel, scroll = self.hierarchySection.snapshot_state()
            self.populate_hierarchy_tree(self.cManager.node_tree)
            self.hierarchySection.restore_state(exp, sel, scroll)
            # Select new node after fallback:
            tree = self.hierarchySection.tree
            def find_and_select_new(item):
                obj = item.data(0, Qt.ItemDataRole.UserRole)
                if obj is new_obj:
                    # expand its parent so you see it
                    parent = item.parent()
                    if parent:
                        parent.setExpanded(True)
                    tree.setCurrentItem(item)
                    return True
                for i in range(item.childCount()):
                    if find_and_select_new(item.child(i)):
                        return True
                return False

            root = tree.invisibleRootItem()
            for i in range(root.childCount()):
                if find_and_select_new(root.child(i)):
                    break
                
    def set_material_db_available(self, available: bool):
        """Enable/disable the 'View Material DB' action."""
        if self.action_view_mat:
            self.action_view_mat.setEnabled(bool(available))

    def open_material_db_viewer(self):
        # Ask manager for the loaded GMaterialDB
        gmat_db = getattr(self.cManager, "material_db", None)
        if not gmat_db:
            self.write_to_console("No material database loaded.")
            return
        dlg = MaterialDBViewerDialog(self, gmat_db)
        dlg.exec()
        
    
    def add_source_from_popup(self, name: str, src_type: str):
        """
        Create a new source under the 'source' node and update UI.
        """
        try:
            # find the 'source' GateObject in your model
            source_obj = None
            for child in self.cManager.node_tree.daughters:
                if child.get_name() == "source":
                    source_obj = child
                    break
            if source_obj is None:
                self.write_to_console("Error: could not find '/source' node.")
                return

            from Classes.GObjectCreator import GObjectCreator
            new_src = GObjectCreator.create_source_child(name, src_type)

            # add to data model
            source_obj.add_daughter(new_src)

            # add to tree (try incremental first)
            item = self.hierarchySection.add_child_item(source_obj, new_src)
            if item is None:
                # fallback full refresh with state restore
                exp, sel, scroll = self.hierarchySection.snapshot_state()
                self.populate_hierarchy_tree(self.cManager.node_tree)
                self.hierarchySection.restore_state(exp, sel, scroll)
                # try to select it
                tree = self.hierarchySection.tree
                def walk(it):
                    obj = it.data(0, Qt.ItemDataRole.UserRole)
                    if obj is new_src:
                        if it.parent(): it.parent().setExpanded(True)
                        tree.setCurrentItem(it)
                        return True
                    for i in range(it.childCount()):
                        if walk(it.child(i)): return True
                    return False
                root = tree.invisibleRootItem()
                for i in range(root.childCount()):
                    if walk(root.child(i)): break
            else:
                self.hierarchySection.tree.setCurrentItem(item)

            self.write_to_console(f"Created source '{name}' ({src_type}).")
        except Exception as e:
            self.write_to_console(f"Failed to create source: {e}")
            
    def add_distribution_from_popup(self, name: str, dtype: str):
        """
        Create a new distribution under the '/distributions' node and update UI.
        """
        try:
            # find the 'distributions' GateObject
            distributions_obj = None
            for child in self.cManager.node_tree.daughters:
                if child.get_name() == "distributions":
                    distributions_obj = child
                    break
            if distributions_obj is None:
                self.write_to_console("Error: could not find '/distributions' node.")
                return

            from Classes.GObjectCreator import GObjectCreator

            # Use helper that enforces unique name and builds type-locked params
            new_dist = GObjectCreator.add_distribution_under_root(
                distributions_obj, name, dtype
            )

            # add to tree (try incremental first)
            item = self.hierarchySection.add_child_item(distributions_obj, new_dist)
            if item is None:
                # fallback full refresh with state restore
                exp, sel, scroll = self.hierarchySection.snapshot_state()
                self.populate_hierarchy_tree(self.cManager.node_tree)
                self.hierarchySection.restore_state(exp, sel, scroll)

                # try selecting the new node
                tree = self.hierarchySection.tree
                def walk(it):
                    obj = it.data(0, Qt.ItemDataRole.UserRole)
                    if obj is new_dist:
                        if it.parent(): it.parent().setExpanded(True)
                        tree.setCurrentItem(it)
                        return True
                    for i in range(it.childCount()):
                        if walk(it.child(i)): return True
                    return False
                root = tree.invisibleRootItem()
                for i in range(root.childCount()):
                    if walk(root.child(i)): break
            else:
                self.hierarchySection.tree.setCurrentItem(item)

            self.write_to_console(f"Created distribution '{new_dist.get_name()}' ({dtype}).")

        except Exception as e:
            self.write_to_console(f"Failed to create distribution: {e}")
            
            
    def save_project_to_json(self, path: str, changed_only=False):
        root: GateObject = self.cManager.node_tree
        ser = ProjectSerializer(include_only_changed=changed_only)
        data = ser.object_to_dict(root)
        # ensure only the top carries the schema marker
        data["_schema"] = "1.0"
        JsonHandler().save(path, data)
        self.write_to_console(f"Saved project to {path}")

    def load_project_from_json(self, path: str):
        raw = JsonHandler().load(path)
        # You can validate schema here if you want
        deser = ProjectDeserializer(material_db=self.material_db, gate_version=(9,3,0))
        new_root = deser.dict_to_object(raw, parent=None)

        # swap into controller + refresh UI
        self.cManager.node_tree = new_root
        exp, sel, scroll = self.hierarchySection.snapshot_state() if hasattr(self.hierarchySection, "snapshot_state") else (None,None,None)
        self.populate_hierarchy_tree(new_root)
        if exp is not None: self.hierarchySection.restore_state(exp, sel, scroll)
        self.write_to_console(f"Loaded project from {path}")