from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)

from services.chat_client import ChatClient
from utils import ConnectThread


class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - Chat App RTC")
        self.resize(300, 150)
        self.client = None

        layout = QVBoxLayout(self)

        self.server_ip_input = QLineEdit()
        self.server_ip_input.setPlaceholderText("Nhập IP server (ví dụ 192.168.1.100)")
        layout.addWidget(QLabel("Server IP:"))
        layout.addWidget(self.server_ip_input)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nhập username (định danh)")
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_input)

        self.display_name_input = QLineEdit()
        self.display_name_input.setPlaceholderText("Nhập tên hiển thị")
        layout.addWidget(QLabel("Tên hiển thị:"))
        layout.addWidget(self.display_name_input)

        self.ok_btn = QPushButton("Kết nối")
        layout.addWidget(self.ok_btn)

        self.ok_btn.clicked.connect(self.attempt_login)

    def get_data(self):
        return (
            self.server_ip_input.text().strip(),
            self.username_input.text().strip(),
            self.display_name_input.text().strip(),
        )

    def attempt_login(self):
        server_ip, username, display_name = self.get_data()
        if not server_ip or not username:
            QMessageBox.warning(
                self, "Lỗi nhập liệu", "Bạn phải nhập Server IP và Username!"
            )
            return

        self.ok_btn.setEnabled(False)
        self.thread = ConnectThread(username, display_name, server_ip)
        self.thread.finished.connect(self.on_connection_done)
        self.thread.start()

    def on_connection_done(self, client):
        self.ok_btn.setEnabled(True)
        if client:
            self.client = client
            self.accept()
        else:
            QMessageBox.critical(self, "Lỗi kết nối", "Không thể kết nối tới server!")
