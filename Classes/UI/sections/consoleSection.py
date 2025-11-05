from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget
from .header import create_header_section

class ConsoleSection:
    
    def __init__(self,parent):
        """Creates and configures the console section."""
        self.widget = QWidget(parent)
        self.layout = QVBoxLayout(self.widget)
        
        self.label = create_header_section(self.widget, "Console Log")
        self.layout.addWidget(self.label)
        
        self.list = QListWidget()
        self.layout.addWidget(self.list)
        
    def write(self, message: str):
        """Writes a message to the console"""
        if self.list is not None:
            self.list.addItem(message)
            self.list.scrollToBottom()            
        else:
            print("Error while printing to console")