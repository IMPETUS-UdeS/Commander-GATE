from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

def create_header_section(parent, text: str) -> QLabel:
    label = QLabel(parent)
    label.setText(text)

    font = QFont()
    font.setFamily("Arial")
    font.setBold(True)
    font.setWeight(75)
    font.setPointSize(9)

    label.setFont(font)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setStyleSheet("background-color: #444; color: white; padding: 5px")
    return label
