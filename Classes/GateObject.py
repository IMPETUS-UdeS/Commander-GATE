from Classes.GateParameter import GateParameter

class GateObject(object):
    def __init__(self, name, path, node_type, parameters=None, parent=None, 
                 system_type: str | None = None, system_name: str | None = None,system_level: str | None = None):
        self.name = name
        self.path = path
        self.node_type = node_type
        self.parameters = list(parameters or [])
        self.daughters = []
        self.enabled = True
        self.role = None
        self.parent = parent
        
        # Systems
        self.system_type = system_type
        self.system_name = system_name or (name if system_type else None)
        self.system_level = system_level
        
        #Source
        self.subtype = None     # e.g. "gps", "PencilBeam", "TPSPencilBeam", etc.
    
    def get_daughters(self):
        return self.daughters
    
    def get_name(self):
        return self.name
    
    def get_type(self):
        return self.node_type
    
    def get_nb_daughters(self):
        return len(self.daughters)
    
    def get_parent(self):
        return self.parent
    
    def add_daughter(self, daughter_obj):
        daughter_obj.parent = self
        self.daughters.append(daughter_obj)
        
    def is_system_root(self) -> bool:
        return bool(self.system_type)

    def set_system_root(self, system_type: str):
        self.system_type = system_type
        self.system_name = self.name

    def attach_to_system(self, system_name: str, level: str):
        self.system_name = system_name
        self.system_level = level
    
        
    def to_dict(self):
        return {
        "name": self.name,
        "path": self.path,
        "node_type": self.node_type,
        "parameters": [parameter.to_dict() for parameter in self.parameters], 
        "daughters": [daughter.to_dict() for daughter in self.daughters],
        "system_type": self.system_type,
        "system_name": self.system_name,
        "system_level": self.system_level,
    }
    
        
    def __str__(self):
        return f"{self.name}"