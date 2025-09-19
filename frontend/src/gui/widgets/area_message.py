from PySide6.QtWidgets import QWidget, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Signal


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

        # Ô nhập tin nhắn
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Nhập tin nhắn...")
        self.message_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 14px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3184fa;
            }
        """)

        # Nút gửi
        self.send_button = QPushButton("Gửi")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setStyleSheet("""
            QPushButton {
                padding: 12px 20px;
                background-color: #3184fa;
                color: white;
                border-radius: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1b6ae0;
            }
        """)

        # Layout nhập tin nhắn
        input_layout = QHBoxLayout()
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