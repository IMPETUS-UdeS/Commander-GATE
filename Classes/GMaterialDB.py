import os

class GElement(object):
    def __init__(self, name, symbol, number, weight):
        self.name = name
        self.symbol = symbol
        self.atomic_number = number
        self.atomic_weight = weight #g/mole
        
    def __repr__(self):
        return f"GElement({self.name}, {self.symbol}, Z={self.atomic_number}, A={self.atomic_weight} g/mole)"
    
    def __str__(self):
        return f"{self.name}:   S= {self.symbol}    ;   Z=  {self.atomic_number}    ;   A=  {self.atomic_weight} g/mole"
     
     
#May need to expand material later   
class GMaterial(object):
    def __init__(self, name):
        self.name = name
        #self.density = density
        
        
    def __repr__(self):
        return f"GMaterial({self.name})"    
    
    def __str__(self):
        return f"{self.name}"


class GMaterialDB(object):
    def __init__(self, file_path):
        self.element_DB = {}
        self.material_DB = {}
        self.file_path = file_path
        
    def get_material_DB(self):
        return [material.name for material in self.material_DB.values()]
    
    def read_material_db(self):
        if not self.file_path:
            print("No materialDB path was provided.")
            return "No materialDB path was provided."
        
        if not os.path.exists(self.file_path):
            print(f"Error: File '{self.file_path}' not found.")
            return f"Error: File '{self.file_path}' not found."
        
        if not self.file_path.lower().endswith(".db"):
            print("Error: Selected file is not a Material Database file.")
            return("Error: Selected file is not a Material Database file.")
        
        with open(self.file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        section = None
        
        currentMaterialLines = []
        
        for line in lines:
            line = line.strip()
            
            if not line or line.startswith("#"): #Skip empty or comment line
                continue
            
            if line.startswith("[") and line.endswith("]"): #Section header
                section = line.strip("[]").lower()
                continue
            
            if section == "elements":
                self.parse_element(line)
            elif section == "materials":
                if not line.startswith("+") and len(currentMaterialLines) > 0:
                    self.parse_material(currentMaterialLines)
                    currentMaterialLines.clear()
                
                currentMaterialLines.append(line) 
                
        print("Successfully imported Material Database.")
        return "Successfully imported Material Database."       
                
                
    def parse_element(self, line):
        """Parse a line from the Elements section."""
        
        if line is None:
            print("No line was sent as a paramter to parse element.")
            return
        
        try:
            name_part, properties_part = line.split(":")
            name = name_part.strip()
            
            properties = {p.split("=")[0].strip(): p.split("=")[1].strip() for p in properties_part.split(";")}
            
            symbol = properties.get("S", "?")
            atomic_number = float(properties.get("Z", 0))
            atomic_weight, atomic_unit = properties.get("A", 0).split()
            atomic_weight = float(atomic_weight)
            
            self.element_DB[name] = GElement(name, symbol, atomic_number, atomic_weight)            
        except Exception as e:
            print(f"Error parsing element line: {line} - {e}")
            
    def parse_material(self, lines):
        """Parse a line from the Materials section."""
        
        if len(lines) < 1:
            print("No lines were sent as a paramter to parse material.")
            return
            
        name_part, properties_part = lines[0].split(":")
        name = name_part.strip()
        
        self.material_DB[name] = GMaterial(name)
        
    def print_materialDB(self):
        print(len(self.element_DB))
        print("\nELEMENTS\n")
        for element in self.element_DB.values():
            print(element.__str__())
        
        print(len(self.material_DB))
        print("\nMATERIALS\n")
        for material in self.material_DB.values():
            print(material.__str__())        