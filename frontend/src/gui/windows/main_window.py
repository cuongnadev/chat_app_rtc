from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel
)
from PySide6.QtCore import Qt
from pathlib import Path
from gui.windows import ChatPanel
from gui.widgets import Navigation, ChatList, Header, AreaMessage

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
                background-color:  #F7FAFC;
                color: #1A202C;
                padding: 0px;
                margin: 0px;
            }
        """
        )

        # ========== Left Sidebar ==========
        self.chat_list = ChatList()
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

        # ========== Welcome Widget ==========
        self.welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(self.welcome_widget)
        self.welcome_label = QLabel("Welcome to Chat App RTC 🎉")
        self.welcome_label.setAlignment(Qt.AlignCenter)
        self.welcome_label.setStyleSheet("""
            background-color: #FFFFFF;
            font-size: 24px;
            font-weight: bold;
            color: #1A202C;
        """)
        welcome_layout.addWidget(self.welcome_label)
        welcome_layout.setContentsMargins(0, 0, 0, 0)
        self.welcome_widget.setStyleSheet("background-color: #F7FAFC;")

        # ========== Main Layout ==========
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.navigation)
        main_layout.addWidget(self.chat_list)
        main_layout.addWidget(self.chat_panel, stretch=1)
        main_layout.addWidget(self.welcome_widget, stretch=1)
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

        # Ẩn chat_list và chat_panel khi mở app
        self.chat_list.hide()
        self.chat_panel.hide()

        # Connect nút Home và Messages
        self.navigation.home.clicked.connect(self.show_home)
        self.navigation.messages.clicked.connect(self.show_messages)

    def show_home(self):
        self.chat_list.hide()
        self.chat_panel.hide()
        self.welcome_widget.show()

    def show_messages(self):
        count = self.chat_list.get_list_widget().count()

        if count == 0:
            self.chat_list.show()
            self.welcome_widget.show()
            self.chat_panel.hide()
        else:
            self.chat_list.show()
            self.welcome_widget.hide()
            self.chat_panel.show()

            self.chat_list.get_list_widget().setCurrentRow(0)