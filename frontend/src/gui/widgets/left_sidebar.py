from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtCore import Qt
from gui.widgets import ChatItemWidget

class LeftSidebar(QListWidget):
    def __init__(self, chat_list_data):
        super().__init__()
        self.setFixedWidth(250)
        self.setFocusPolicy(Qt.NoFocus)
        self.setSpacing(4)

        self.setStyleSheet("""
            QListWidget {
                background-color: #f5f5f5;
                border: none;
            }
            QListWidget::item {
                border-radius: 12px;
                color: #333333;
            }
            QListWidget::item:selected {
                background-color: #d9eaff;
                color: black;
            }
            QListWidget::item:hover {
                color: black;
                background-color: #e8e8e8;
            }
            QListWidget::item:selected:hover {
                background-color: #d9eaff;
                color: black;
            }
        """)

        self.load_chats(chat_list_data)

    def load_chats(self, chat_list_data):
        """Tạo các item chat bên trái"""
        for item in chat_list_data:
            self.add_chat_item(item["avatar"], item["name"], item.get("last_message", ""))

    def add_chat_item(self, avatar_path, name, last_message=""):
        """Tạo từng item chat"""
        widget = ChatItemWidget(avatar_path, name, last_message)
        item = QListWidgetItem()
        item.setSizeHint(widget.sizeHint())
        item.setData(Qt.UserRole, {
            "name": name,
            "avatar_path": avatar_path
        })

        self.addItem(item)
        self.setItemWidget(item, widget)
        return item
