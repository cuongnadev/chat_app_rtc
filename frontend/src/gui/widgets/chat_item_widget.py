from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt

from utils.happers import RoundedPixmap

class ChatItemWidget(QWidget):
    def __init__(self, avatar_path: str, name_text: str, last_message: str = "", parent=None):
        super().__init__(parent)

        # main_layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(10)

        # avatar
        self.avatar = QLabel()
        self.avatar.setPixmap(RoundedPixmap(avatar_path, 42))
        main_layout.addWidget(self.avatar)


        # info_layout
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)

        # name
        self.name = QLabel(name_text)
        self.name.setStyleSheet("font-size: 16px; font-weight: bold; color: black;")
        info_layout.addWidget(self.name)

        self.message = QLabel(last_message)
        self.message.setStyleSheet("font-size: 14px; color: gray;")
        info_layout.addWidget(self.message)

        main_layout.addLayout(info_layout)
        main_layout.setAlignment(Qt.AlignLeft)
        self.setLayout(main_layout)

