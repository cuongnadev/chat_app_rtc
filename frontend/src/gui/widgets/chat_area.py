from PySide6.QtWidgets import QWidget, QScrollArea, QVBoxLayout
from gui.widgets.chat_bubble import ChatBubble

class ChatArea(QWidget):
    def __init__(self):
        super().__init__()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.v_layout = QVBoxLayout(self.scroll_content)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.addStretch()

        self.scroll_area.setWidget(self.scroll_content)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(self.scroll_area)

    def add_message(self, sender, message, is_sender=False, file_data=None, local_path=None):
        """Hỗ trợ cả text và file"""
        bubble = ChatBubble(sender, message, is_sender, file_data=file_data, local_path=local_path)
        self.v_layout.insertWidget(self.v_layout.count() - 1, bubble)
        # tự cuộn xuống cuối
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
