import os
from PySide6.QtWidgets import (
    QVBoxLayout, QWidget, QLabel, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from pathlib import Path

from utils.happers import RoundedPixmap

class Navigation(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("Navigation")
        self.setFixedWidth(64)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        # allow stylesheet to paint the widget background
        self.setAttribute(Qt.WA_StyledBackground, True)

        # stylesheet chỉ áp dụng cho chính widget này
        self.setStyleSheet("""
            #Navigation {
                background-color: #3184fa;
            }
        """)


        main_layout = QVBoxLayout();
        main_layout.setContentsMargins(0, 10, 0, 10)
        main_layout.setAlignment(Qt.AlignTop)

        # avatar
        self.avatar = QLabel()
        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        ASSETS_DIR = BASE_DIR / "assets"
        avatar_path = str(ASSETS_DIR / "avatarC.png")
        self.avatar.setPixmap(RoundedPixmap(avatar_path, 42))
        self.avatar.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.avatar)

        main_layout.addStretch()

        # setting
        self.settings = QPushButton()
        self.settings.setFixedSize(48, 48)
        setting_path = str(ASSETS_DIR / "settings.svg")
        self.settings.setIcon(QIcon(setting_path))
        self.settings.setIconSize(QSize(32, 32))
        self.settings.setStyleSheet("""
            QPushButton {
                border-radius: 24px;
                border: none;
                color: white;
            }
            QPushButton:hover {
                background-color: #1b6ae0;
            }
        """)
        main_layout.addWidget(self.settings, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)
        



