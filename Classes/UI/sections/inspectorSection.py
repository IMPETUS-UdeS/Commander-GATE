from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListView, QLabel, QHBoxLayout, QLineEdit,
    QPushButton, QCheckBox, QSizePolicy, QFileDialog, QAbstractItemView, QComboBox
)
from PyQt6.QtGui import QFont, QStandardItemModel, QStandardItem, QFontMetrics
from PyQt6.QtCore import Qt, QSize
from functools import partial

# Use your existing popups
from Classes.UI.popups.PhysicsProcessPopup import PhysicsProcessPopup
from Classes.UI.popups.SourcePopup import SourcePopup
from .header import create_header_section
from Classes.StaticData import SYSTEM_TYPES, SYSTEM_LEVELS_BY_TYPE, SYSTEM_LEVEL_SHAPES
from Classes.UI.parameters.BigPopupCombo import BigPopupCombo
from Classes.UI.parameters.ElidingLabel import ElidingLabel
from Classes.UI.popups.DistributionsPopup import DistributionPopup

class InspectorSection:
    """
    Encapsulates the Inspector UI and logic. Keeps your look & behavior.
    Public API:
      - widget: container to add in layout
      - listview: QListView (for font update)
      - populate_parameters(item)  # mirrors your old method name/signature
      - resize_parameters(font_size)
    """
    
    def __init__(self, parent):
        self.host = parent
        self.widget = QWidget(parent)
        self.layout = QVBoxLayout(self.widget)

        self._seed_mode_dd = None
        self._seed_manual_edit = None

        self.label = create_header_section(self.widget, "Inspector View")
        self.layout.addWidget(self.label)

        self.listview = QListView()
        self.listview.setSpacing(0)
        self.layout.addWidget(self.listview)

        # Cache of inspector widgets for resize
        # Each entryL {"label": QLabel|None, "inputs": [widgets], "unit": QComboBox|None}
        self.inspector_widgets = []


    # --------------------------
    # Small helpers
    # --------------------------
    
    def _font(self, fs: int, bold: bool = False) -> QFont:
        return QFont("Arial", fs, QFont.Weight.Bold if bold else QFont.Weight.Normal)
    
    def _label_min_px(self, fs: int, ch: int = 32) -> int:
        fm = QFontMetrics(self._font(fs))
        return int(ch * fm.horizontalAdvance("M"))
    
    def _std_label_width(self, fs: int) -> int:
        return 175 + fs * 6
    
    def _control_height(self, fs: int) -> int:
        """A control height based on font, with a floor"""
        fm = QFontMetrics(self._font(fs))
        return max(24, fm.height() + 4)
    
    def _prepare_combo(self, cb: BigPopupCombo):
        cb.setMaxVisibleItems(20)
        view = QListView(cb)
        view.setUniformItemSizes(True)
        view.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerItem)
        cb.setView(view)
        
    def _combo(self, fs: int, items=None, width: int | None = None) -> BigPopupCombo:
        dd = BigPopupCombo(popup_rows=14, min_chars=16)
        dd.setFont(self._font(fs))
        self._prepare_combo(dd)
        if items:
            dd.addItems(items)
        if width:
            dd.setFixedWidth(width)
        return dd
    
    def _button(self, text: str, fs: int, width: int | None, click):
        btn = QPushButton(text)
        btn.setFont(self._font(fs))
        if width:
            btn.setFixedWidth(width)
        btn.setStyleSheet("font-size: 18px; font-weight: bold; border: none; background: transparent;" if "➕" in text or text == "Add ➕" else "")
        btn.clicked.connect(click)
        return btn
    
    def _row_widget(self) -> tuple[QWidget, QHBoxLayout]:
        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(1, 2, 1, 2)
        h.setSpacing(4)
        h.setAlignment(Qt.AlignmentFlag.AlignLeft)
        return row, h
    
    def _append_widget_row(self, model: QStandardItemModel, widget: QWidget, fs: int, vpad: int = 6, spacer: int = 1):
        row_item = QStandardItem()
        model.appendRow(row_item)
        self.listview.setIndexWidget(row_item.index(), widget)
        self._apply_row_height(row_item, widget, fs, vpad=vpad)
        if spacer:
            self._add_spacer(model, spacer)
        
    def apply_font(self, fs: int):
        base = self._font(fs)
        self.widget.setFont(base)
        self.listview.setFont(base)
        self.label.setFont(self._font(fs, bold=True))

    
    # -----------------------------
    # Main population
    # -----------------------------
    def populate_parameters(self, item):
        if not item:
            return
        gate_object = item.data(0, Qt.ItemDataRole.UserRole)
        if gate_object is None:
            return

        # reset model + cache
        self.inspector_widgets = []
        model = QStandardItemModel()
        self.listview.setModel(model)
        font_size = self.host.font_size_slider.value()

        # header
        self._add_header(model, gate_object)
        

        # special rows
        self._maybe_add_physics_plus(model, item, gate_object, font_size)
        self._maybe_add_source_plus(model, item, gate_object, font_size)
        self._maybe_add_distributions_plus(model,item,gate_object,font_size)
        self._maybe_add_rename(model, gate_object, font_size)
        self._maybe_add_role(model, gate_object, font_size)
        self._maybe_add_system_root_row(model, gate_object, font_size)
        self._maybe_add_attach_row(model, gate_object, font_size)
        
        if getattr(gate_object, "node_type", "") == "source":
            self._maybe_add_source_controls(model, item, gate_object, font_size)

        # parameters
        self._add_parameters_block(model, gate_object, font_size)
        self._sync_seed_manual_state()

        # final pass for sizing
        self.resize_parameters(font_size)
    
    
    # -----------------------------
    # Header and section labels
    # -----------------------------
    def _add_header(self, model, gate_object):
        model.appendRow(QStandardItem(f"Object: {gate_object.get_name()}"))
        
    def _add_section_label(self, model, title, font_size):
        label_item = QStandardItem()
        label = ElidingLabel(title)
        label.setFont(self._font(font_size, bold=True))
        label.setStyleSheet("color: black; background-color: #e0e0e0; padding: 4px;")
        model.appendRow(label_item)
        self.listview.setIndexWidget(label_item.index(), label)
        self._apply_row_height(label_item, label, font_size, vpad=4)
    

    # -----------------------------
    # Special rows (physics/source/etc.)
    # -----------------------------

    def _maybe_add_physics_plus(self, model, item, gate_object, font_size):
        if gate_object.get_name() != "physics":
            return
        btn = self._button("➕", font_size, 40, click=lambda: PhysicsProcessPopup(
            self.host, gate_object, lambda: self.populate_parameters(item)
            ).exec())
        self._append_widget_row(model, btn, font_size)
        
    def _maybe_add_source_plus(self, model, item, gate_object, font_size):
        if gate_object.get_name() != "source":
            return
        btn = self._button( "Add ➕", font_size, 120, click=lambda: SourcePopup(
            self.host, lambda name, src_type: (
                hasattr(self.host, "add_source_from_popup") and self.host.add_source_from_popup(name, src_type),
                self.populate_parameters(item)
            )).exec()
        )
        
        self._append_widget_row(model, btn, font_size)
        
    def _maybe_add_distributions_plus(self, model, item, gate_object, font_size):
        if gate_object.get_name() != "distributions":
            return
        btn = self._button( "Add ➕", font_size, 120, click=lambda: DistributionPopup(
            self.host, on_create=lambda name, dtype: ( 
                hasattr(self.host, "add_distribution_from_popup") and self.host.add_distribution_from_popup(name, dtype),
                self.populate_parameters(item)
            )).exec()
        )
        self._append_widget_row(model, btn, font_size)

    def _maybe_add_rename(self, model, gate_object, font_size):
        if gate_object.get_type() == "root":
            return
        widget = self._build_rename_row(gate_object, font_size)
        self._append_widget_row(model, widget, font_size)


    def _maybe_add_role(self, model, gate_object, font_size):
        if not getattr(gate_object, "parent", None) or gate_object.parent.get_name() != "world":
            return
        widget = self._build_role_row(gate_object, font_size)
        self._append_widget_row(model, widget, font_size)
        

    def _maybe_add_system_root_row(self, model, gate_object, font_size):
        # Only direct daughters of world can become a "system root"
        if not getattr(gate_object, "parent", None) or gate_object.parent.get_name() != "world":
            return
        row, h = self._row_widget()

        lbl = ElidingLabel("System:")
        lbl.setFont(QFont("Arial", font_size))
        lbl.setMinimumWidth(self._label_min_px(font_size))
        
        cb = QCheckBox("Mark as system root")
        cb.setChecked(bool(getattr(gate_object, "system_type", None)))

        dd = self._combo(font_size)
        dd.addItems(SYSTEM_TYPES)
        #self._prepare_combo(dd)
        if getattr(gate_object, "system_type", None) in SYSTEM_TYPES:
            dd.setCurrentText(gate_object.system_type)

        def set_root_enabled(st):
            if st == Qt.CheckState.Checked.value:
                # ensure model has helpers on object
                if not hasattr(gate_object, "set_system_root"):
                    gate_object.set_system_root = lambda sys_type: setattr(gate_object, "system_type", sys_type)
                gate_object.set_system_root(dd.currentText())
            else:
                gate_object.system_type = None

        cb.stateChanged.connect(set_root_enabled)
        dd.currentTextChanged.connect(lambda v: gate_object.set_system_root(v) if cb.isChecked() else None)

        h.addWidget(lbl)
        h.addWidget(cb)
        h.addWidget(dd)
        self._append_widget_row(model, row, font_size)

    def _maybe_add_attach_row(self, model, gate_object, font_size):
        systems = self._all_system_roots()
        if not systems or gate_object.get_type() == "root" or not self._is_under_world(gate_object):
            return

        row, h = self._row_widget()
    
        lbl = ElidingLabel("Attach to system:");
        lbl.setFont(QFont("Arial", font_size));
        lbl.setMinimumWidth(self._label_min_px(font_size))

        sys_dd = self._combo(font_size, width=220 + font_size * 2)
        sys_dd.addItem(" - ")
        for s in systems:
            sys_dd.addItem(s.system_name if hasattr(s, "system_name") else s.get_name())
        if getattr(gate_object, "system_name", None):
            sys_dd.setCurrentText(gate_object.system_name)

        level_dd = self._combo(font_size)

        def refresh_levels():
            name = sys_dd.currentText()
            if name.strip() in {"-", " - "}:
                level_dd.clear(); return
            sys_obj = next((s for s in systems if (getattr(s, "system_name", s.get_name()) == name)), None)
            level_dd.clear()
            if sys_obj:
                for lvl in SYSTEM_LEVELS_BY_TYPE.get(getattr(sys_obj, "system_type", None), []):
                    level_dd.addItem(lvl)
                if getattr(gate_object, "system_level", None) in [level_dd.itemText(i) for i in range(level_dd.count())]:
                    level_dd.setCurrentText(gate_object.system_level)

        refresh_levels()
        sys_dd.currentTextChanged.connect(lambda _: refresh_levels())

        def apply_attach():
            name = sys_dd.currentText()
            if name.strip() in {"-", " - "}:
                gate_object.system_name = None; gate_object.system_level = None; return
            level = level_dd.currentText() or None
            if not hasattr(gate_object, "attach_to_system"):
                gate_object.attach_to_system = lambda nm, lv: (setattr(gate_object, "system_name", nm),
                                                            setattr(gate_object, "system_level", lv))
            gate_object.attach_to_system(name, level)
            # optional hint
            sys_type = None
            for s in systems:
                if getattr(s, "system_name", s.get_name()) == name:
                    sys_type = getattr(s, "system_type", None); break
            hint = self._shape_hint_text(gate_object, sys_type, level or "")
            if hint: self.host.write_to_console(f"Note: {hint}")

        sys_dd.currentTextChanged.connect(lambda _: apply_attach())
        level_dd.currentTextChanged.connect(lambda _: apply_attach())

        h.addWidget(lbl); h.addWidget(sys_dd); h.addWidget(level_dd)
        self._append_widget_row(model, row, font_size)
    
    
    # -----------------------------
    # Parameters block
    # -----------------------------    
    def _add_parameters_block(self, model, gate_object, font_size):
        # section gates
        sections_shown = {"placement": False, "moves": False, "vis": False, "random": False, "repeater": False}
        
        # Section tests collected here to avoid long if-chains; behavior identical.
        def _section_key_for(param_path: str) -> str | None:
            if "/placement/" in param_path:
                return "placement"
            if "/moves/" in param_path:
                return "moves"
            if "/vis/" in param_path:
                return "vis"
            if param_path.startswith("/random/"):
                return "random"
            if any(tag in param_path for tag in ("/repeaters/", "/ring/", "/linear/", "/cubicArray/", "/quadrant/", "/sphere/", "/genericRepeater/")):
                return "repeater"
            return None

        for param in gate_object.parameters:
            self._normalize_param_lists(param)

            key = _section_key_for(param.path)
            if key and not sections_shown[key]:
                title = {
                    "placement": "Placement Settings",
                    "moves": "Moving Settings",
                    "vis": "Visualization Settings",
                    "random": "Random Settings",
                    "repeater": "Repeater Settings",
                }[key]
                self._add_section_label(model, title, font_size)
                sections_shown[key] = True

            # one param row
            row_widget = self._build_param_row(param, font_size)
            self._append_widget_row(model, row_widget, font_size)

    def _normalize_param_lists(self, p):
        p.default_value_list = p.default_value_list or []
        p.value_list = p.value_list or []
        p.input_type_list = p.input_type_list or []

    def _build_param_row(self, param, font_size) -> QWidget:
        row, h = self._row_widget()

        label = ElidingLabel(param.displayed_name)
        label.setFont(self._font(font_size))
        label.setMinimumWidth(self._label_min_px(font_size))
        label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        h.addWidget(label)

        inputs = []
        for i, input_type in enumerate(param.input_type_list):
            w = self._build_input_widget(input_type, param, i, font_size)
            if w:
                w.setFont(QFont("Arial", font_size))
                h.addWidget(w, 0)
                inputs.append(w)

        # units
        unit_dd = None
        if getattr(param, "unit_list", None):
            unit_dd = self._combo(font_size, items=param.unit_list or [], width=100)
            default_index = (param.unit_list.index(param.default_unit)
                            if getattr(param, "default_unit", None) in (param.unit_list or []) else 0)
            unit_dd.setCurrentIndex(default_index)
            unit_dd.currentIndexChanged.connect(lambda idx, p=param: setattr(p, "default_unit", p.unit_list[idx]))
            h.addWidget(unit_dd)
        
        self.inspector_widgets.append({"label":label, "inputs":inputs, "unit":unit_dd})
        return row

    def _build_input_widget(self, input_type, param, i, font_size):
        default_value = param.default_value_list[i] if i < len(param.default_value_list) else ""
        current_value = param.value_list[i] if i < len(param.value_list) else ""

        if input_type == "TextArea":
            w = QLineEdit()
            w.setText(str(default_value))
            w.setFixedWidth(60 + font_size)
            w.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            w.textChanged.connect(lambda v, p=param, idx=i: self.update_parameter_value(p, idx, v))
            if getattr(param, "path", "").endswith("/random/setEngineSeedValue"):
                self._seed_manual_edit = w
                self._sync_seed_manual_state()
            return w

        if input_type == "DropDown":
            w = self._combo(font_size, width=120 + font_size * 2)
            items = current_value if isinstance(current_value, list) else [" - "]
            w.addItems(items)
            w.setCurrentText(str(default_value))
            w.setFixedWidth(120 + font_size * 2)
            #self._prepare_combo(w)
            w.currentTextChanged.connect(lambda v, p=param, idx=i: self.update_parameter_value(p, idx, v))
            if getattr(param, "path", "").endswith("/random/setEngineSeed"):
                self._seed_mode_dd = w
                # react to changes
                w.currentTextChanged.connect(lambda _=None: self._sync_seed_manual_state())
                w.currentIndexChanged.connect(lambda _=None: self._sync_seed_manual_state())
                self._sync_seed_manual_state()
            return w

        if input_type == "CheckBox":
            w = QCheckBox()
            w.setChecked(bool(default_value))
            w.stateChanged.connect(partial(self.update_checkbox_value, param, i))
            return w

        if input_type == "Select":
            w = self._button("Browse..." if not current_value else str(current_value), font_size, 200,
                                click=(lambda: self.host.browse_file("import_material_db")) if param.path == "/geometry/setMaterialDatabase"
                                else (lambda _, b=None, p=param, idx=i: self.browse_file_for_param(w, p, idx)))
            return w

        return None
    
    # -----------------------------
    # Utility actions
    # -----------------------------
    
    def update_parameter_value(self, param, index, value):
        while len(param.default_value_list) <= index:
            param.default_value_list.append(None)
        param.default_value_list[index] = value

    def update_checkbox_value(self, param, index, state):
        is_checked = (state == Qt.CheckState.Checked.value)
        while len(param.default_value_list) <= index:
            param.default_value_list.append(None)
        param.default_value_list[index] = is_checked

    def browse_file_for_param(self, button, param, index):
        dlg = QFileDialog()
        dlg.setWindowTitle("Select a File")
        dlg.setFileMode(QFileDialog.FileMode.ExistingFile)
        if dlg.exec():
            selected_file = dlg.selectedFiles()[0]
            while len(param.value_list) <= index:
                param.value_list.append("")
            param.value_list[index] = selected_file
            button.setText(selected_file)
            self.host.write_to_console(f"Selected file for {param.displayed_name}: {selected_file}")
    
    
    # -----------------------------
    # Rename / Role rows
    # -----------------------------
    def _build_rename_row(self, gate_object, font_size):
        row, h = self._row_widget()

        lbl = ElidingLabel("Object Name:")
        lbl.setFont(self._font(font_size))
        lbl.setMinimumWidth(self._label_min_px(font_size))
        lbl.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        name_input = QLineEdit()
        name_input.setFont(self._font(font_size))
        name_input.setText(gate_object.get_name())
        name_input.setFixedHeight(int(font_size * 1.8) - 4)
        name_input.setFixedWidth(170 + (font_size * 2))
        name_input.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        apply_btn = QPushButton("Apply")
        apply_btn.setFont(self._font(font_size))
        apply_btn.setFixedHeight(int(font_size * 1.8) - 4)
        apply_btn.setFixedWidth(70 + font_size)
        apply_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        apply_btn.clicked.connect(lambda: self.rename_gate_object(gate_object, name_input.text()))

        h.addWidget(lbl)
        h.addWidget(name_input)
        h.addWidget(apply_btn)
        h.addStretch(1)
        return row
    
    def _build_role_row(self, gate_object, font_size):
        row, h = self._row_widget()

        lbl = ElidingLabel("Object Role: ")
        lbl.setFont(self._font(font_size))
        lbl.setMinimumWidth(self._label_min_px(font_size))
        lbl.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        dd = self._combo(font_size, width=170 + font_size * 2)
        siblings = gate_object.parent.daughters if gate_object.parent else []
        existing_roles = [obj.role for obj in siblings if obj != gate_object]

        dd.addItem(" - ")
        if "Scanner" not in existing_roles:
            dd.addItem("Scanner")
        if "Phantom" not in existing_roles:
            dd.addItem("Phantom")

        dd.setCurrentText(gate_object.role or " - ")
        dd.currentTextChanged.connect(lambda v: setattr(gate_object, "role", v if v != " - " else None))

        h.addWidget(lbl); h.addWidget(dd)
        return row
    
    
    def rename_gate_object(self, gate_object, new_name):
        existing_names = set()
        root = self.host.hierarchySection.tree.invisibleRootItem()
        for i in range(root.childCount()):
            existing_names.add(root.child(i).text(0))

        unique_name = new_name
        if new_name in existing_names and gate_object.get_name() != new_name:
            i = 1
            while f"{new_name}{i}" in existing_names:
                i += 1
            unique_name = f"{new_name}{i}"

        gate_object.name = unique_name
        selected_item = self.host.hierarchySection.tree.currentItem()
        if selected_item:
            selected_item.setText(0, unique_name)
        self.host.write_to_console(f"Renamed object to: {unique_name}")
    
    # -----------------------------
    # Source helpers
    # -----------------------------
    def _maybe_add_source_controls(self, model, item, src_obj, font_size):    
        row, h = self._row_widget()

        lbl = ElidingLabel("Attach to volume:")
        lbl.setFont(self._font(font_size))
        lbl.setMinimumWidth(self._label_min_px(font_size))

        dd = self._combo(font_size, width=240 + font_size * 2)
        dd.addItem(" - ")
        for name in self._world_volume_names():
            dd.addItem(name)

        attach_param = next((p for p in src_obj.parameters if p.path.endswith("/attachTo")), None)
        current_attach = (attach_param.default_value_list[0] if (attach_param and attach_param.default_value_list) else "")
        if current_attach and dd.findText(current_attach) != -1:
            dd.setCurrentText(current_attach)

        def on_attach_changed(txt):
            if attach_param:
                attach_param.default_value_list = ["" if txt.strip() in ("", "-", " - ") else txt]

        dd.currentTextChanged.connect(on_attach_changed)

        # Delete button for this source
        del_btn = QPushButton("Delete Source")
        del_btn.setFont(self._font(font_size))
        del_btn.setFixedWidth(160)
        del_btn.clicked.connect(lambda: self._delete_source(item, src_obj))

        h.addWidget(lbl)
        h.addWidget(dd)
        h.addWidget(del_btn)
        self._append_widget_row(model, row, font_size)
        
    def _world_volume_names(self):
        """Return names of world and all its descendants as candidate attach targets."""
        names = []
        tree = self.host.hierarchySection.tree
        root = tree.invisibleRootItem()
        # find the 'world' item
        world_item = None
        for i in range(root.childCount()):
            it = root.child(i)
            obj = it.data(0, Qt.ItemDataRole.UserRole)
            if obj and obj.get_name() == "world":
                world_item = it
                break
        if not world_item:
            return names

        def walk(it):
            obj = it.data(0, Qt.ItemDataRole.UserRole)
            if obj:
                names.append(obj.get_name())  # use Gate name (matches Gate macro)
            for k in range(it.childCount()):
                walk(it.child(k))

        walk(world_item)
        return names
    
    
    def _delete_source(self, item, src_obj):
        # Remove from GateObject parent
        parent_obj = getattr(src_obj, "parent", None)
        if parent_obj and hasattr(parent_obj, "daughters"):
            try:
                parent_obj.daughters.remove(src_obj)
            except ValueError:
                pass

        # REmove from the QTreeWidget
        tree = self.host.hierarchySection.tree
        # 'item' here is the QTreeWidgetItem passed from populate_parameters; if not, find it:
        qt_item = item if hasattr(item, "data") else tree.currentItem()
        if qt_item and qt_item.parent():
            parent_qt = qt_item.parent()
            parent_qt.removeChild(qt_item)
        elif qt_item:
            # top-level under /source
            idx = tree.indexOfTopLevelItem(qt_item)
            if idx >= 0:
                tree.takeTopLevelItem(idx)

        # Clear inspector
        self.listview.setModel(QStandardItemModel())

        # Console note
        self.host.write_to_console(f"Deleted source '{src_obj.get_name()}'.")
    
    # -----------------------------
    # Misc utilities
    # -----------------------------
    def _add_spacer(self, model, height=1):
        s = QStandardItem(); 
        s.setSizeHint(QSize(10, height)); 
        model.appendRow(s)
        
    def _all_system_roots(self):
        # Scan the current tree for objects with system_type set
        systems = []
        tree = self.host.hierarchySection.tree
        root = tree.invisibleRootItem()
        def walk(item):
            obj = item.data(0, Qt.ItemDataRole.UserRole)
            if obj and getattr(obj, "system_type", None):
                systems.append(obj)
            for i in range(item.childCount()):
                walk(item.child(i))
        for i in range(root.childCount()):
            walk(root.child(i))
        return systems 
        
    def _shape_hint_text(self, gate_object, system_type, level):
        from Classes.StaticData import SYSTEM_LEVEL_SHAPES
        required = SYSTEM_LEVEL_SHAPES.get(system_type, {}).get(level, "any")
        if required == "any":
            return None
        
        if "cylinder" in gate_object.path:
            shape = "cylinder"
        elif "wedge" in gate_object.path:
            shape = "wedge"
        else:
            shape = "box"
        if shape != required:
            return f"Recommended shape for {system_type}:{level} is '{required}', current looks like '{shape}'."
        return None
    
    def _is_under_world(self, obj) -> bool:
        p = getattr(obj, "parent", None)
        while p:
            if p.get_name() == "world":
                return True
            p = getattr(p, "parent", None)
        return False
    
    
    def _sync_seed_manual_state(self):
        if not self._seed_manual_edit:
            return
        mode = (self._seed_mode_dd.currentText() if self._seed_mode_dd else "").strip().lower()
        is_manual = (mode == "manual")
        self._seed_manual_edit.setEnabled(is_manual)
        if is_manual:
            self._seed_manual_edit.setStyleSheet("")
            self._seed_manual_edit.setToolTip("Enter a seed (0 … 900000000)")
        else:
            self._seed_manual_edit.setStyleSheet("QLineEdit { color: palette(mid); }")
            self._seed_manual_edit.setToolTip("Switch Seed mode to 'manual' to edit")
            
    
    def _apply_row_height(self, std_item, row_widget, fs: int, vpad: int = 6):
        """Make the row and all its children tall enough so nothing clips."""
        h = self._control_height(fs)

        # controls
        for w in row_widget.findChildren(QWidget, options=Qt.FindChildOption.FindDirectChildrenOnly):
            if isinstance(w, QAbstractItemView):
                continue
            if hasattr(w, "setFixedHeight"):
                w.setFixedHeight(h)
                
        # row item height (this is what prevents clipping)
        std_item.setSizeHint(QSize(1, h + vpad))  # width is ignored by QListView
    
    
    # -----------------------------
    # Resizing (public API)
    # -----------------------------
    def resize_parameters(self, font_size: int):
        if not self.inspector_widgets:
            return
        
        def _text_width(fs: int) -> int: return 120 + (fs * 2)
        def _dd_width(fs: int)   -> int: return 220 + (fs * 2)

        for entry in self.inspector_widgets:
            # ---- normalize entry  ----
            if isinstance(entry, dict):
                label   = entry.get("label")
                inputs  = entry.get("inputs") or []
                unit_dd = entry.get("unit")
            else:
                label   = entry[0] if len(entry) > 0 else None
                second  = entry[1] if len(entry) > 1 else None
                unit_dd = entry[2] if len(entry) > 2 else None
                if isinstance(second, (list, tuple)):
                    inputs = list(second)
                elif second is None:
                    inputs = []
                else:
                    inputs = [second]

            # ---- label sizing ----
            if isinstance(label, QLabel):
                label.setFont(QFont(label.font().family(), font_size))
                if hasattr(self, "_label_min_px"):
                    label.setMinimumWidth(self._label_min_px(font_size))

            # ---- input widgets ----
            for w in inputs:
                if not w:
                    continue
                w.setFont(QFont(w.font().family(), font_size))

                # consistent widths per type
                if isinstance(w, QLineEdit):
                    w.setFixedWidth(_text_width(font_size))
                    w.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                elif isinstance(w, (QComboBox, BigPopupCombo)):
                    w.setFixedWidth(_dd_width(font_size))
                elif isinstance(w, QCheckBox):
                    w.setStyleSheet("")
                elif isinstance(w, QPushButton):
                    w.setFixedWidth(_dd_width(font_size))

            # ---- unit dropdown  ----
            if isinstance(unit_dd, BigPopupCombo):
                unit_dd.setFont(QFont("Arial", font_size))
                unit_dd.setFixedWidth(90 + (font_size // 2))
                self._prepare_combo(unit_dd)

        # ---- row heights ----
        row_h = self._control_height(font_size)
        for entry in self.inspector_widgets:
            # apply height to all widgets
            if isinstance(entry, dict):
                widgets = [entry.get("label")] + (entry.get("inputs") or []) + [entry.get("unit")]
            else:
                second = entry[1] if len(entry) > 1 else None
                if isinstance(second, (list, tuple)):
                    widgets = [entry[0]] + list(second) + ([entry[2]] if len(entry) > 2 else [])
                else:
                    widgets = [entry[0], second, entry[2] if len(entry) > 2 else None]

            for w in widgets:
                if w and hasattr(w, "setFixedHeight"):
                    w.setFixedHeight(row_h)

        # normalize QListView row heights to fix the clipping
        model = self.listview.model()
        if model:
            vpad = 4
            for r in range(model.rowCount()):
                it = model.item(r)
                if it is not None:
                    sh = it.sizeHint()
                    it.setSizeHint(QSize(sh.width(), row_h + vpad))
    
