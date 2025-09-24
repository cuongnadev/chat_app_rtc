from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - Chat App RTC")
        self.resize(300, 150)

        layout = QVBoxLayout(self)

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

        self.ok_btn.clicked.connect(self.accept)

    def get_data(self):
        return self.username_input.text().strip(), self.display_name_input.text().strip()
