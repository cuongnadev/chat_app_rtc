from PySide6.QtWidgets import (
    QWidget, QHBoxLayout
)
from PySide6.QtCore import Qt
from pathlib import Path
from gui.widgets import (
    Navigation, LeftSidebar
)
from gui.windows import ChatPanel

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
        self.chat_panel = ChatPanel()

        # ========== Main Layout ==========
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.navigation)
        main_layout.addWidget(self.chat_list)
        main_layout.addWidget(self.chat_panel)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(main_layout)

        # Khi chọn cuộc trò chuyện trong danh sách
        self.chat_list.currentItemChanged.connect(self.chat_panel.change_chat)