from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt
from pathlib import Path

from utils.happers import RoundedPixmap
from gui.widgets.button import Button

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = BASE_DIR / "assets"

class Header(QWidget):
    def __init__(self, name: str, avatar_path: str, status="Online", dot_color="#68D391"):
        super().__init__()
        # avatar
        self.avatar = QLabel()
        self.avatar.setPixmap(RoundedPixmap(avatar_path, 42, 0.2))

        # name 
        self.name = QLabel(name)
        self.name.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.name.setStyleSheet("margin: 0; font-size: 18px; font-weight: bold;")

        # dot + status
        self.dot = QLabel()
        self.dot.setFixedSize(10, 10)
        self.dot.setStyleSheet(f"""
            background-color: {dot_color};
            border-radius: 5px
        """)

        self.status = QLabel(status)
        self.status.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status.setStyleSheet("""
            margin: 0;
            color: #000;
            font-size: 12px;
            font-style: normal;
            font-weight: 600;
        """)

        # button call
        self.button = Button("Call", str(ASSETS_DIR / "phone.svg"))

        # status
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(6)
        status_layout.addWidget(self.dot)
        status_layout.addWidget(self.status)

        # content_layout
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(4)
        content_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        content_layout.addWidget(self.name)
        content_layout.addLayout(status_layout)

        # info_layout
        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(10)
        info_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        info_layout.addWidget(self.avatar)
        info_layout.addLayout(content_layout)

        # header_layout
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignLeft)
        header_layout.addLayout(info_layout)

        header_layout.addStretch()

        header_layout.addWidget(self.button)
        self.setLayout(header_layout)

    def setName(self, name: str):
        self.name.setText(name)

    def setAvatar(self, avatar_path: str):
        self.avatar.setPixmap(RoundedPixmap(avatar_path, 42))
