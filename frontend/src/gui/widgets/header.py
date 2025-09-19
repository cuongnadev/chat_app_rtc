from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PySide6.QtCore import Qt

from utils.happers import RoundedPixmap

class Header(QWidget):
    def __init__(self, name: str, avatar_path: str):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignLeft)

        # avatar
        self.avatar = QLabel()
        self.avatar.setPixmap(RoundedPixmap(avatar_path, 42))
        layout.addWidget(self.avatar)

        # title 
        self.title = QLabel(name)
        self.title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 8px;")
        layout.addWidget(self.title)

        self.setLayout(layout)

    def setName(self, name: str):
        self.title.setText(name)

    def setAvatar(self, avatar_path: str):
        self.avatar.setPixmap(RoundedPixmap(avatar_path, 42))
