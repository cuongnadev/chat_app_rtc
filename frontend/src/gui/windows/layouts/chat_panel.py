from PySide6.QtWidgets import (
    QVBoxLayout,  QWidget
)
from gui.widgets import (
    Header, AreaMessage
)
from PySide6.QtCore import Qt
from pathlib import Path

# Lấy thư mục gốc project
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ASSETS_DIR = BASE_DIR / "assets"

class ChatPanel(QWidget):
    def __init__(self):
        super().__init__()

        chat_panel_layout = QVBoxLayout()
        chat_panel_layout.setContentsMargins(0, 0, 0, 0)

        # ========== Right Panel ==========
        # Header chat
        self.chat_header = Header("Chào mừng bạn đến với Chat App", str(ASSETS_DIR / "avatar.png"))

        # Content chat, Ô nhập tin nhắn + nút gửi
        self.area_message = AreaMessage()

        chat_panel_layout.addWidget(self.chat_header)
        chat_panel_layout.addWidget(self.area_message)

        self.setLayout(chat_panel_layout)

    def change_chat(self, current_item, previous_item):
        """Đổi tiêu đề chat khi click bên trái"""
        if current_item:
            data = current_item.data(Qt.UserRole)
            self.chat_header.setName(data["name"])
            self.chat_header.setAvatar(data["avatar_path"])
            self.area_message.clear_message()