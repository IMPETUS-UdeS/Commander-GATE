# Classes/IO/project_io.py
from __future__ import annotations
import json
from typing import Any, Callable, Dict, List, Optional

from Classes.GateObject import GateObject
from Classes.GateParameter import GateParameter
from Classes.GObjectCreator import GObjectCreator

SCHEMA_VERSION = "1.0"

# ---- helpers to avoid non-serializable surprises ----
def _as_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]

def _clean_list(lst):
    # Avoid JSON 'NaN' etc; keep it simple
    out = []
    for x in (lst or []):
        if x is None:
            out.append(None)
        else:
            out.append(x)
    return out

def _is_ui_only_param(p: GateParameter) -> bool:
    name = getattr(p, "displayed_name", "") or ""
    path = getattr(p, "path", "") or ""
    types = [t.lower() for t in (p.input_type_list or [])]
    if "__ui_" in path:
        return True
    if "label" in types:  # purely presentational
        return True
    return False


class ProjectSerializer:
    """
    Convert GateObject -> dict (-> JSON).
    """
    def __init__(self,
                 param_filter: Optional[Callable[[GateParameter], bool]] = None,
                 include_only_changed: bool = False):
        self.param_filter = param_filter
        self.include_only_changed = include_only_changed

    # You can later add "is_changed" logic if you track pristine values.
    def _should_keep_param(self, p: GateParameter) -> bool:
        if _is_ui_only_param(p):
            return False
        if self.param_filter and not self.param_filter(p):
            return False
        return True

    def parameter_to_dict(self, p: GateParameter) -> Dict[str, Any]:
        return {
            "path": getattr(p, "path", ""),
            "name": getattr(p, "displayed_name", ""),
            "input_types": list(p.input_type_list or []),
            "values": _clean_list(p.default_value_list or p.value_list or []),
            "unit_list": list(getattr(p, "unit_list", []) or []),
            "default_unit": getattr(p, "default_unit", None),
        }

    def object_to_dict(self, obj: GateObject) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "_schema": SCHEMA_VERSION if obj.get_name() == "gate" else None,  # only top gets marker
            "name": obj.get_name(),
            "path": getattr(obj, "path", ""),
            "node_type": getattr(obj, "node_type", ""),
            # optional meta you use in UI/logic
            "role": getattr(obj, "role", None),
            "system_type": getattr(obj, "system_type", None),
            "system_name": getattr(obj, "system_name", None),
            "system_level": getattr(obj, "system_level", None),
            # for sources/distributions/world daughters:
            "source_type": getattr(obj, "source_type", None),
            "distribution_type": getattr(obj, "distribution_type", None),
            "shape": getattr(obj, "shape", getattr(obj, "subtype", None)),  # if you stash it
            # parameters
            "parameters": [self.parameter_to_dict(p)
                           for p in (obj.parameters or [])
                           if self._should_keep_param(p)],
            "children": []
        }
        # Nulls are fine in JSON, but prune top-level None keys for neatness
        data = {k: v for k, v in data.items() if v not in (None, [], "") or k in ("parameters", "children")}
        # recurse
        for child in getattr(obj, "daughters", []) or []:
            data["children"].append(self.object_to_dict(child))
        return data


class ProjectDeserializer:
    """
    Convert dict (JSON) -> GateObject tree.
    Uses GObjectCreator where possible.
    """
    def __init__(self, material_db=None, gate_version=(9, 3, 0)):
        self.material_db = material_db
        self.gate_version = gate_version

    def _param_from_dict(self, d: Dict[str, Any]) -> GateParameter:
        p = GateParameter(
            d.get("path", ""),
            d.get("name", ""),
            d.get("input_types", []),
            d.get("values", []),
            d.get("values", []),  # populate both default and current with same
            d.get("unit_list", None),
            0  # precision is optional; your GateParameter supports extra args
        )
        if "default_unit" in d:
            p.default_unit = d.get("default_unit")
        return p

    def _apply_params(self, obj: GateObject, p_list: List[Dict[str, Any]]) -> None:
        if not p_list:
            return
        # We try to *merge* onto the existing parameter layout (created by factory),
        # else append params that didn't exist.
        existing_by_path = {p.path: p for p in (obj.parameters or [])}
        for pd in p_list:
            if pd.get("path") in existing_by_path:
                tgt = existing_by_path[pd["path"]]
                tgt.input_type_list = list(pd.get("input_types", []) or [])
                vals = pd.get("values", [])
                tgt.default_value_list = list(vals or [])
                tgt.value_list = list(vals or [])
                tgt.unit_list = list(pd.get("unit_list", []) or [])
                if "default_unit" in pd:
                    tgt.default_unit = pd.get("default_unit")
            else:
                obj.parameters.append(self._param_from_dict(pd))

    def _new_child(self, parent_name: str, data: Dict[str, Any]) -> GateObject:
        name = data.get("name", "noname")
        node_type = data.get("node_type", "")
        # World daughters with shape
        if parent_name == "world" and data.get("shape"):
            try:
                child = GObjectCreator.create_world_daughter(name, data["shape"], self.material_db)
                child.shape = data["shape"]
                return child
            except Exception:
                pass
        # Source children
        if parent_name == "source":
            st = data.get("source_type") or data.get("subtype") or "gps"
            child = GObjectCreator.create_source_child(name, st)
            child.source_type = st
            return child
        # Distribution children
        if parent_name == "distributions":
            dt = data.get("distribution_type") or "Flat"
            child = GObjectCreator.create_distribution_child(name, dt)
            child.distribution_type = dt
            return child
        # Fallback: generic object
        return GateObject(name, data.get("path", ""), node_type, [])

    def dict_to_object(self, data: Dict[str, Any], parent: GateObject | None = None) -> GateObject:
        name = data.get("name", "noname")
        # Root “gate” node? If you prefer to rebuild with your factory:
        if name == "gate" and not parent:
            # Rebuild the whole static skeleton if you want — or accept as-is
            root = GateObject("gate", "/gate", "root", [])
            obj = root
        else:
            parent_name = parent.get_name() if parent else ""
            obj = self._new_child(parent_name, data)

        # common metadata
        for k in ("role", "system_type", "system_name", "system_level", "shape", "source_type", "distribution_type"):
            if k in data:
                setattr(obj, k, data[k])

        # parameters
        self._apply_params(obj, data.get("parameters", []))

        # children
        for cd in data.get("children", []):
            child = self.dict_to_object(cd, parent=obj)
            obj.add_daughter(child)

        return obj