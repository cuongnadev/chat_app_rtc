from PySide6.QtWidgets import (
    QWidget, QHBoxLayout
)
from PySide6.QtCore import Qt
from pathlib import Path
from gui.windows import ChatPanel
from gui.widgets import Navigation, ChatList, Header, AreaMessage


# [Fake data]: Chat list
from constants.chat_list import chat_list

# Lấy thư mục gốc project
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = BASE_DIR / "assets"


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat App RTC")
        self.resize(1100, 650)

        # ========== Navigation ==========
        self.navigation = Navigation()
        self.navigation.setStyleSheet(
            """
            QWidget {
                background-color: #F7FAFC;
                color: #1A202C;
                padding: 0px;
                margin: 0px;
            }
        """
        )

        # ========== Left Sidebar ==========
        self.chat_list = ChatList(chat_list)
        self.chat_list.setStyleSheet(
            """
            QWidget {
                background-color: #F7FAFC;
                color: #1A202C;
                padding: 0px;
                margin: 0px;
            }
        """
        )

        # ========== Right Panel ==========
        self.chat_panel = ChatPanel()

        # ========== Main Layout ==========
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.navigation)
        main_layout.addWidget(self.chat_list)
        main_layout.addWidget(self.chat_panel, stretch=1)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.setLayout(main_layout)

        self.setStyleSheet(
            """
            QWidget {
                background-color: #F7FAFC;
                color: #1A202C;
                padding: 0px;
                margin: 0px;
            }
        """
        )

        # Khi chọn cuộc trò chuyện trong danh sách
        self.chat_list.get_list_widget().currentItemChanged.connect(self.chat_panel.change_chat)
