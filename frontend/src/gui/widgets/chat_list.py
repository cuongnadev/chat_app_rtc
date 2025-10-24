from PySide6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QVBoxLayout,
    QWidget,
    QLabel,
    QHBoxLayout,
)
from PySide6.QtCore import Qt
from pathlib import Path
from gui.widgets import ChatItemWidget

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = BASE_DIR / "assets"


class ChatList(QWidget):
    def __init__(self, chat_list_data=[]):
        super().__init__()
        self.chat_list_data = chat_list_data
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        self.setLayout(main_layout)

        # Title bar
        title_layout = QHBoxLayout()
        self.title_label = QLabel("Messages")
        self.title_label.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #1A202C;
                padding: 12px;
                background-color: transparent;
            }
        """
        )
        title_layout.addWidget(self.title_label)
        title_widget = QWidget()
        title_widget.setLayout(title_layout)
        title_widget.setStyleSheet(
            """
            QWidget {
                background-color: #FFFFFF;
                padding: 5px;
            }
        """
        )
        main_layout.addWidget(title_widget)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setFixedWidth(350)
        self.search_bar.setFixedHeight(40)
        self.search_bar.setPlaceholderText("Search chats...")
        self.search_bar.setStyleSheet(
            """
            QLineEdit {
                padding: 10px;
                border: 1px solid #CBD5E0;
                border-radius: 8px;
                background-color: #F3F3F3;
                color: #1A202C;
                font-size: 14px;
            }
            QLineEdit::placeholder {
                color: #A0AEC0;
            }
            QLineEdit:focus {
                border: 1px solid #F3F3F3;
                background-color: #FFFFFF;
            }
        """
        )
        self.search_bar.textChanged.connect(self.filter_chats)
        main_layout.addWidget(self.search_bar)

        # Chat list
        self.list_widget = QListWidget()
        self.list_widget.setFixedWidth(350)
        self.list_widget.setFocusPolicy(Qt.NoFocus)
        self.list_widget.setSpacing(2)
        self.list_widget.setStyleSheet(
            """
            QListWidget {
                background-color: #F7FAFC;
                border: none;
            }
            QListWidget::item {
                border-radius: 12px;
                background-color: #FFFFFF;
                color: #1A202C;
            }
            QListWidget::item:selected {
                background-color: #E2E8F0;
                color: #1A202C;
            }
            QListWidget::item:hover {
                color: #1A202C;
                background-color: #EDF2F7;
            }
            QListWidget::item:selected:hover {
                background-color: #E2E8F0;
                color: #1A202C;
            }
            QListWidget QScrollBar:vertical, QListWidget QScrollBar:horizontal {
                width: 0px;
                height: 0px;
            }
        """
        )
        main_layout.addWidget(self.list_widget)
        self.load_chats(self.chat_list_data)

    def update_users(self, users):
        self.chat_list_data = []
        for u in users:
            if u.get("type") == "group":
                avatar = str(ASSETS_DIR / "group_avatar.png")
            else:
                avatar = str(ASSETS_DIR / "avatar.png")

            self.chat_list_data.append({
                "avatar": avatar,
                "name": u["display_name"],
                "username": u["username"],
                "type": u.get("type", "user"),
                "last_message": "",
                "last_active_time": "",
            })

        self.load_chats(self.chat_list_data)


    def load_chats(self, chat_list_data):
        self.list_widget.clear()
        for item in chat_list_data:
            self.add_chat_item(
                item["avatar"],
                item["name"],
                item["username"],
                item.get("last_message", ""),
                item.get("last_active_time", ""),
                item_type=item.get("type", "user"),
            )

    def add_chat_item(
        self, avatar_path, name, username, last_message="", last_active_time="", item_type="user"
    ):
        widget = ChatItemWidget(avatar_path, name, last_message, last_active_time)
        item = QListWidgetItem()
        item.setSizeHint(widget.sizeHint())
        item.setData(
            Qt.UserRole,
            {
                "name": name,
                "username": username,
                "avatar_path": avatar_path,
                "last_message": last_message,
                "last_active_time": last_active_time,
                "type": item_type
            },
        )
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, widget)
        return item

    def filter_chats(self, search_text):
        self.list_widget.clear()
        search_text = search_text.lower()
        if not search_text:
            self.load_chats(self.chat_list_data)
        else:
            filtered_data = [
                item
                for item in self.chat_list_data
                if search_text in item["name"].lower()
                or search_text in item.get("last_message", "").lower()
                or search_text in item.get("last_active_time", "").lower()
            ]
            self.load_chats(filtered_data)

    def get_list_widget(self):
        return self.list_widget
