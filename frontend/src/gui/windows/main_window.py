from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt
from gui.widgets import Navigation, ChatList, Header, AreaMessage
from pathlib import Path

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
        # Header chat
        self.chat_header = Header(
            "Chào mừng bạn đến với Chat App", str(ASSETS_DIR / "avatar.png")
        )
        self.chat_header.setStyleSheet(
            """
            QWidget {
                background-color: #F7FAFC;
                color: #1A202C;
                padding: 0px;
                margin: 0px;
            }
        """
        )

        # Content chat, Ô nhập tin nhắn + nút gửi
        self.area_message = AreaMessage()
        self.area_message.setStyleSheet(
            """
            QWidget {
                background-color: #F7FAFC;
                color: #1A202C;
                padding: 0px;
                margin: 0px;
            }
        """
        )

        # Layout bên phải
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.chat_header)
        right_layout.addWidget(self.area_message, stretch=1)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # ========== Main Layout ==========
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.navigation)
        main_layout.addWidget(self.chat_list)
        main_layout.addLayout(right_layout, stretch=1)
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
        self.chat_list.get_list_widget().currentItemChanged.connect(self.change_chat)

    def change_chat(self, current_item, previous_item):
        """Đổi tiêu đề chat khi click bên trái"""
        if current_item:
            data = current_item.data(Qt.UserRole)
            self.chat_header.setName(data["name"])
            self.chat_header.setAvatar(data["avatar_path"])
            self.area_message.clear_message()

    def send_message(self):
        """Xử lý khi gửi tin nhắn"""
        # print("Bạn vừa gửi:", message)
        # Ở đây có thể gọi API gửi tin nhắn, rồi append tin nhắn trả lời:
        # self.area_message.append_message("Bot", "Xin chào bạn!")
