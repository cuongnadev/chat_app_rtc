from PySide6.QtWidgets import (
    QVBoxLayout, QWidget, QLabel, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QCursor
from pathlib import Path

from utils.happers import RoundedPixmap

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = BASE_DIR / "assets"
class Navigation(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("Navigation")
        self.setFixedWidth(64)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        # allow stylesheet to paint the widget background
        self.setAttribute(Qt.WA_StyledBackground, True)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 10, 0, 10)
        main_layout.setAlignment(Qt.AlignTop)

        # avatar
        self.avatar = QLabel()
        avatar_path = str(ASSETS_DIR / "chat_logo.ico")
        self.avatar.setPixmap(RoundedPixmap(avatar_path, 42, 0.2))
        self.avatar.setAlignment(Qt.AlignCenter)
        self.avatar.setCursor(QCursor(Qt.PointingHandCursor))
        main_layout.addWidget(self.avatar)

        # home
        self.home = QPushButton()
        self.home.setFixedSize(40, 40)
        home_path = str(ASSETS_DIR / "home.svg")
        self.home.setIcon(QIcon(home_path))
        self.home.setIconSize(QSize(24, 24))
        self.home.setStyleSheet("""
            QPushButton {
                border-radius: 20px;
                border: none;
            }
            QPushButton:hover, QPushButton:checked {
                background-color: rgba(97, 94, 240, 0.10);
            }
        """)
        self.home.setCursor(QCursor(Qt.PointingHandCursor))
        self.home.setCheckable(True)

        # messages
        self.messages = QPushButton()
        self.messages.setFixedSize(40, 40)
        messages_path = str(ASSETS_DIR / "messages.svg")
        self.messages.setIcon(QIcon(messages_path))
        self.messages.setIconSize(QSize(24, 24))
        self.messages.setStyleSheet("""
            QPushButton {
                border-radius: 20px;
                border: none;
            }
            QPushButton:hover, QPushButton:checked {
                background-color: rgba(97, 94, 240, 0.10);
            }
        """)
        self.messages.setCursor(QCursor(Qt.PointingHandCursor))
        self.messages.setCheckable(True)

        nav_layout = QVBoxLayout()
        nav_layout.setContentsMargins(0, 10, 0, 10)
        nav_layout.setSpacing(10)
        nav_layout.setAlignment(Qt.AlignCenter)
        nav_layout.addWidget(self.home)
        nav_layout.addWidget(self.messages)

        main_layout.addLayout(nav_layout)
        main_layout.addStretch()

        # group
        self.groups = QPushButton()
        self.groups.setFixedSize(40, 40)
        groups_path = str(ASSETS_DIR / "groups.svg")
        self.groups.setIcon(QIcon(groups_path))
        self.groups.setIconSize(QSize(24, 24))
        self.groups.setStyleSheet("""
            QPushButton {
                border-radius: 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(97, 94, 240, 0.10);
            }
        """)
        self.groups.setCursor(QCursor(Qt.PointingHandCursor))
        main_layout.addWidget(self.groups, alignment=Qt.AlignCenter)
        self.groups.setCheckable(True)

        # setting
        self.settings = QPushButton()
        self.settings.setFixedSize(40, 40)
        setting_path = str(ASSETS_DIR / "gear.svg")
        self.settings.setIcon(QIcon(setting_path))
        self.settings.setIconSize(QSize(24, 24))
        self.settings.setStyleSheet("""
            QPushButton {
                border-radius: 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(97, 94, 240, 0.10);
            }
        """)
        self.settings.setCursor(QCursor(Qt.PointingHandCursor))
        main_layout.addWidget(self.settings, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

        self.home.setChecked(True)

        # When pressing Home → hide chat_list + chat_panel
        self.home.clicked.connect(lambda: self.select_nav(self.home))

        # When pressing Messages → show chat_list + chat_panel
        self.messages.clicked.connect(lambda: self.select_nav(self.messages))

    def select_nav(self, btn):
        for b in [self.home, self.messages]:
            if b != btn:
                b.setChecked(False)
        btn.setChecked(True)

        



