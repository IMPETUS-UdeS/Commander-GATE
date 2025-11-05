import json
import os

class JsonHandler():
    
    def load(self, file_name: str):
        if not file_name or not os.path.exists(file_name):
            raise FileNotFoundError(file_name)
        with open(file_name, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, file_name: str, data):
        if not file_name:
            raise ValueError("file_name is required")
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        
        
    def importJson(self, file_name=None):
        return self.load(file_name)

    def exportJson(self, file_name, data):
        self.save(file_name, data)
        return "JSON exported successfully"