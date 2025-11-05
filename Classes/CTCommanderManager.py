import os
import re
from Classes.UI.MainWindow import MainWindow
from Classes.IO.JsonHandler import JsonHandler
from Classes.GObjectCreator import GObjectCreator
from Classes.GMaterialDB import GMaterialDB
from Classes.IO.project_io import ProjectSerializer, ProjectDeserializer

class CTCommanderManager:
    def __init__(self):
        self.node_tree = None
        self.material_db_list = []
        
        self.json_handler = JsonHandler()
        
        if self.node_tree is None:
            self.node_tree = GObjectCreator.create_gate_root()
        
        self.ct_commander_window = MainWindow(self, self.json_handler)
        self.ct_commander_window.show()

        self.gate_version: tuple[int, int, int] = self.detect_gate_version()

        geant4_version = self.get_geant4_version()
        self.ct_commander_window.write_to_console(f"Detected Geant4 version: {geant4_version}")
    
        
    def get_material_db(self):
        return self.material_db_list
        
    def get_geant4_version(self):
        """Detects the Geant4 version from the parent directory of CTCommander.py."""
        current_dir = os.path.dirname(os.path.abspath(__file__))  # Get current directory (where CTCommander.py is)
        parent_dir = os.path.dirname(current_dir)  # Move one level up to parent directory

        print(f"Searching for Geant4 in: {parent_dir}")  # Debugging: Show search location

        try:
            files = os.listdir(parent_dir)  # List all files in the parent directory
        except FileNotFoundError:
            return "Error: Parent directory not found"

        # Regex pattern to match Geant4 version (e.g., geant4-v11.3.0.tar.gz)
        pattern = re.compile(r"geant4-v(\d+\.\d+\.\d+)\.tar\.gz")

        for file in files:
            match = pattern.search(file)
            if match:
                return match.group(1)  # Extracts "11.3.0"

        return "Geant4 version not found"
    
    def detect_gate_version(self):
        # Cool method for when I know how without running through Docker
        return (9,2,0)

    def set_gate_version(self, version_tuple: tuple[int, int, int] | tuple[int, int]):
        """Set Gate version (major, minor[, patch])."""
        if len(version_tuple) == 2:
            self.gate_version = (version_tuple[0], version_tuple[1], 0)
        else:
            self.gate_version = tuple(version_tuple[:3])

    
    def is_above_9_2(self) ->bool:
        return self.gate_version >= (9,3,0)
    
    
    def import_json(self, file_path):
        """
        Import a value snapshot and apply it:
        - import material DB if present
        - ensure static nodes exist
        - create missing distribution children when needed
        - set parameter values and default units by label
        """
        if not file_path:
            return
        try:
            data = self.json_handler.load(file_path)
        except Exception as e:
            self.ct_commander_window.write_to_console(f"Import failed: {e}")
            return

        try:
            self.apply_project_snapshot(data)  # uses _apply_object_snapshot recursively
            self.ct_commander_window.populate_hierarchy_tree(self.node_tree)
            self.ct_commander_window.write_to_console(f"Imported project from: {file_path}")
        except Exception as e:
            self.ct_commander_window.write_to_console(f"Apply failed: {e}")

    def export_json(self, file_path):
        """
        Save a value snapshot of the current project:
        - material_db_path (if any)
        - root tree with values/units/children
        """
        if not file_path:
            return
        try:
            data = self.build_project_snapshot()  # uses _build_snapshot recursively
            self.json_handler.save(file_path, data)  # your JsonHandler.save
            self.ct_commander_window.write_to_console(f"Exported project to: {file_path}")
        except Exception as e:
            self.ct_commander_window.write_to_console(f"Export failed: {e}")
        
        

    def import_material_db(self, file_path):
        """Handles Material Database import and updates UI."""

        self.material_db = GMaterialDB(file_path)
        if not hasattr(self.material_db, "file_path"):
            self.material_db.file_path = file_path
        self.ct_commander_window.write_to_console(self.material_db.read_material_db())
        self.material_db_list = self.material_db.get_material_DB()
        
        self.ct_commander_window.set_material_db_available(True)

        self.material_db.print_materialDB()
        print(self.material_db_list)        
        

        if self.node_tree and self.node_tree.get_nb_daughters() > 0:
            self.ct_commander_window.write_to_console("Material database loaded. Existing node tree preserved.")
        else:
            self.node_tree = GObjectCreator.create_static_objects(self.node_tree, self.material_db_list, gate_version=self.gate_version, sd_names=[])
            self.ct_commander_window.populate_hierarchy_tree(self.node_tree)
            
            
    def _param_to_value_snapshot(self, p) -> dict:
        # Store just what's needed to recreate UI state
        snap = {
            "label": getattr(p, "displayed_name", None) or getattr(p, "name", None),
            "values": list(p.default_value_list or []),
        }
        du = getattr(p, "default_unit", None)
        if du is not None:
            snap["unit"] = du
        return snap

    def _object_meta(self, obj) -> dict:
        """Small hints that help re-create missing children (no paths)."""
        meta = {}
        # commonly used on your objects
        if getattr(obj, "role", None):
            meta["role"] = obj.role
        if getattr(obj, "system_type", None):
            meta["system_type"] = obj.system_type
        if getattr(obj, "system_level", None):
            meta["system_level"] = obj.system_level
        # sources / distributions
        if getattr(obj, "source_type", None):
            meta["source_type"] = obj.source_type
        if getattr(obj, "subtype", None):
            meta["distribution_type"] = obj.subtype  # you stored type in create_distribution_child
        # for world daughters you can add "shape" if you attach it on creation
        if getattr(obj, "parent", None) and obj.parent.get_name() == "world":
            if getattr(obj, "subtype", None):
                meta["shape"] = obj.subtype
        return meta

    def _build_snapshot(self, obj) -> dict:
        return {
            "name": obj.get_name(),
            "node_type": obj.get_type(),
            "meta": self._object_meta(obj),
            "parameters": [self._param_to_value_snapshot(p) for p in getattr(obj, "parameters", [])],
            "children": [self._build_snapshot(c) for c in getattr(obj, "daughters", [])]
        }

    def build_project_snapshot(self) -> dict:
        # include material DB path if present so we can auto-import on restore
        material_db_path = getattr(getattr(self, "material_db", None), "file_path", None)
        return {
            "schema": "2.0",
            "material_db_path": material_db_path,
            "root": self._build_snapshot(self.node_tree) if self.node_tree else None
        }
        
    
    def _find_child_by_name(self, parent_obj, name):
        for c in getattr(parent_obj, "daughters", []):
            if c.get_name() == name:
                return c
        return None

    def _apply_param_values(self, obj, param_snapshots: list):
        # Match by label (displayed_name). This avoids persisting path strings.
        label_to_param = {}
        for p in getattr(obj, "parameters", []):
            key = getattr(p, "displayed_name", None) or getattr(p, "name", None)
            if key:
                label_to_param.setdefault(key, []).append(p)  # allow duplicates if any

        for ps in (param_snapshots or []):
            label = ps.get("label")
            if not label:
                continue
            candidates = label_to_param.get(label, [])
            if not candidates:
                continue
            # apply to all candidates sharing the label
            for p in candidates:
                p.default_value_list = list(ps.get("values", []))
                if "unit" in ps:
                    p.default_unit = ps["unit"]

    def _maybe_create_child_from_meta(self, parent_obj, child_snap: dict):
        """
        Create dynamic children (e.g. /source/<name>, /distributions/<name>) if they don't exist yet.
        We use the parent's name + child meta to decide what factory to call.
        """
        name = child_snap.get("name")
        meta = child_snap.get("meta", {}) or {}

        parent_name = (getattr(parent_obj, "name", None) or parent_obj.get_name() or "").lower()

        # ---- Distributions ----
        dist_type = meta.get("distribution_type")
        if parent_name == "distributions" and dist_type:
            new_obj = GObjectCreator.create_distribution_child(name, dist_type)
            parent_obj.add_daughter(new_obj)
            return new_obj

        # ---- Source ----
        src_type = meta.get("source_type")
        if parent_name == "source" and src_type:
            new_obj = GObjectCreator.create_source_child(name, src_type)
            parent_obj.add_daughter(new_obj)
            return new_obj

        # ---- Geometry (anywhere under world): use 'shape' ----
        shape = meta.get("shape")
        if shape:
            # Check if parent is under world (at any depth)
            anc = parent_obj
            under_world = False
            while anc is not None:
                if getattr(anc, "name", "").lower() == "world":
                    under_world = True
                    break
                anc = anc.get_parent()

            if under_world:
                # If your factory can create a child under ANY parent, use it.
                # Most implementations of create_world_daughter are happy as long as you add_daughter(new_obj).
                new_obj = GObjectCreator.create_world_daughter(name, shape, self.get_material_db())
                parent_obj.add_daughter(new_obj)
                return new_obj

        # Nothing to create
        return None

    def _apply_object_snapshot(self, obj, snap: dict):
        # apply meta
        meta = snap.get("meta", {}) or {}
        if "role" in meta:
            obj.role = meta["role"]
        if "system_type" in meta:
            obj.system_type = meta["system_type"]
        if "system_level" in meta:
            obj.system_level = meta["system_level"]

        # apply parameter values by label
        self._apply_param_values(obj, snap.get("parameters", []))

        # recurse for children (create missing dynamic ones when we can)
        for child_snap in (snap.get("children") or []):
            name = child_snap.get("name")
            child_obj = self._find_child_by_name(obj, name)
            if child_obj is None:
                child_obj = self._maybe_create_child_from_meta(obj, child_snap)
            if child_obj is not None:
                self._apply_object_snapshot(child_obj, child_snap)

    def apply_project_snapshot(self, data: dict):
        # 0) material DB auto-import if present
        mdb = (data or {}).get("material_db_path")
        if mdb and os.path.exists(mdb):
            # this calls your existing loader + updates UI flags
            self.import_material_db(mdb)

        # 1) ensure we have the base tree (gate root + static nodes)
        if not self.node_tree or not getattr(self.node_tree, "daughters", None):
            from Classes.GObjectCreator import GObjectCreator
            self.node_tree = GObjectCreator.create_gate_root()
            # Add standard static nodes (physics, digitizer, distributions, source, output, acquisition, verbose, vis, world)
            self.node_tree = GObjectCreator.create_static_objects(
                self.node_tree, self.get_material_db(), gate_version=self.gate_version, sd_names=[]
            )

        # 2) apply snapshot from root downward
        root_snap = (data or {}).get("root") or {}
        if root_snap:
            self._apply_object_snapshot(self.node_tree, root_snap)

        # 3) refresh UI
        self.ct_commander_window.populate_hierarchy_tree(self.node_tree)
        self.ct_commander_window.write_to_console("Project imported and applied.")