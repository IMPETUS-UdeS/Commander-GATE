import sys
from PyQt6.QtWidgets import QApplication
from Classes.CTCommanderManager import CTCommanderManager

def main():
    app = QApplication(sys.argv)
    
    ct_commander_manager = CTCommanderManager()

    sys.exit(app.exec())
    



if __name__ == "__main__":
    main()
      