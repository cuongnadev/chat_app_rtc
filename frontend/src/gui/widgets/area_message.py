from PySide6.QtWidgets import QWidget, QTextEdit, QLineEdit, QHBoxLayout, QVBoxLayout, QWidgetAction
from PySide6.QtCore import Signal
from pathlib import Path

from gui.widgets.button import Button

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = BASE_DIR / "assets"

class AreaMessage(QWidget):
    messageSent = Signal(str) # phát ra nội dung tin nhắn khi gửi
    def __init__(self):
        super().__init__()

        # Khung hiển thị tin nhắn
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
            }
        """)

        # paperclip
        self.paperclip_button = Button("", str(ASSETS_DIR / "paperclip.svg"), True, "transparent")

        # Ô nhập tin nhắn
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type a message")
        self.message_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 20px;
                border: 2px solid #E2E8F0;
                border-radius: 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #615EF0;
            }
        """)

        # Nút gửi
        self.send_button = Button("", str(ASSETS_DIR / "send.svg"), True, "transparent")
        self.send_button.clicked.connect(self.send_message)

        # Layout nhập tin nhắn
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.paperclip_button)
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)

        # Layout chính
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.chat_display)
        main_layout.addLayout(input_layout)

        self.setLayout(main_layout)

    def send_message(self):
        message = self.message_input.text().strip()
        if message:
            self.chat_display.append(f"<b>Bạn:</b> {message}")
            self.messageSent.emit(message)  # gửi signal ra ngoài
            self.message_input.clear()

    def append_message(self, sender: str, message: str):
        self.chat_display.append(f"<b>{sender}:</b> {message}")

    def clear_message(self):
        self.chat_display.clear();