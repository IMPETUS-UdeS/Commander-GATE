DARK_MODE_STYLESHEET = """
QWidget, QToolTip { background-color: #2E2E2E; color: white; }
QMenuBar, QToolBar, QStatusBar { background-color: #3E3E3E; }
QTreeWidget, QListWidget, QListView { background-color: #3E3E3E; color: white; }
QLabel, QLineEdit, QComboBox, QPushButton, QCheckBox { color: white; }
"""

LIGHT_MODE_STYLESHEET = """
QMainWindow { background-color: lightgray;}
QMenuBar, QToolBar, QStatusBar { background-color: black; color: white; }
QToolBar QToolButton { color: white; }
QTreeWidget, QListWidget, QListView, QLabel, QDialog { background-color: white; color: black; }
QTreeWidget::item:selected { background-color: lightblue; color: black; }
QLineEdit, QComboBox, QPushButton, QCheckBox { 
    color: black; background-color: lightgrey; border-style: outset; border-width: 1px; border-color: black; 
} 
"""

WORLD_OBJECT_WINDOW_STYLESHEET = """
QDialog { background-color: lightgray; }
QFrame#HeaderSection, QFrame#ParamContainer {
    background-color: white; border: 1px solid gray; border-radius: 4px;
}
QLabel { background-color: white; color: black; font-family: Arial; }
QLineEdit, QComboBox {
    background-color: lightgray; border: 1px solid gray; border-radius: 4px; padding: 2px;
}
QPushButton { background-color: white; color: black; border: 1px solid gray; border-radius: 4px; padding: 4px; }

"""