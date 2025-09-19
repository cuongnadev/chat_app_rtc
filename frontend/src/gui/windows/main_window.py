from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout
)
from PySide6.QtCore import Qt
from gui.widgets import (
    Navigation, LeftSidebar, Header, AreaMessage
)

from pathlib import Path

# Lấy thư mục gốc project
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = BASE_DIR / "assets"

chat_list = [
    {
        "avatar": str(ASSETS_DIR / "avatarC.png"),
        "name": "Cường Dev",
        "last_message": "Tin nhắn mới nhất"
    },
    {
        "avatar": str(ASSETS_DIR / "avatarV.png"),
        "name": "Trần Vinh",
        "last_message": "Tin nhắn mới nhất"
    },
    {
        "avatar": str(ASSETS_DIR / "avatarB.png"),
        "name": "Ka Bun",
        "last_message": "Đang xem..."
    },
    {
        "avatar": str(ASSETS_DIR / "avatarT.png"),
        "name": "Đông Thi",
        "last_message": "Ai làm bài tập chưa?"
    },
    # Thêm bao nhiêu chat tùy ý
]

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat App RTC")
        self.resize(1100, 650)

                # ========== Navigation ==========
        self.navigation = Navigation()

        # ========== Left Sidebar ==========
        self.chat_list = LeftSidebar(chat_list)

        # ========== Right Panel ==========
        # Header chat
        self.chat_header = Header("Chào mừng bạn đến với Chat App", str(ASSETS_DIR / "avatar.png"))

        # Content chat, Ô nhập tin nhắn + nút gửi
        self.area_message = AreaMessage()

        # Layout bên phải
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.chat_header)
        right_layout.addWidget(self.area_message)

        # ========== Main Layout ==========
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.navigation)
        main_layout.addWidget(self.chat_list)
        main_layout.addLayout(right_layout)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(main_layout)

        # Khi chọn cuộc trò chuyện trong danh sách
        self.chat_list.currentItemChanged.connect(self.change_chat)

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