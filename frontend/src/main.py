import os
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from gui.windows import MainWindow
from gui.widgets import LoginWindow
from services.chat_client import ChatClient


class ChatAppRTC(QWidget):
    def __init__(self, client: ChatClient):
        super().__init__()
        self.client = client

        # Set window properties
        self.setWindowTitle("Chat App RTC")
        self.resize(1100, 650)

        # Main window content
        self.main_window = MainWindow()

        # kết nối signals
        self.client.usersUpdated.connect(self.main_window.chat_list.update_users)
        self.client.messageReceived.connect(self.main_window.chat_panel.area_message.append_message)

        # khi bấm gửi tin nhắn
        self.main_window.chat_panel.area_message.messageSent.connect(self.send_message)

        # thông báo ChatClient GUI đã sẵn sàng
        self.client.gui_ready()

        # Layout for central widget
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.main_window)
        self.setLayout(layout)

        # Show the window
        self.show()

    def send_message(self, message: str):
        current_item = self.main_window.chat_list.get_list_widget().currentItem()
        if current_item:
            data = current_item.data(Qt.UserRole)   # giờ dict này có cả username
            print(f"data: {data}")
            target = data["name"]  # lấy username
            self.client.send_message(target, message)


if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("Fusion")
    app.setStyleSheet(
        """
        QWidget {
            background-color: #F7FAFC;
            color: #1A202C;
            font-family: 'Segoe UI', Arial;
        }
    """
    )
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, "assets", "chat_logo.ico")
    app.setWindowIcon(QIcon(icon_path))

    login = LoginWindow()
    if login.exec() == LoginWindow.Accepted:
        username, display_name = login.get_data()
        if username:
            client = ChatClient(username, display_name)

            # giữ biến window ngoài scope để không bị GC
            window_holder = {}

            def open_main_window():
                window_holder["window"] = ChatAppRTC(client)

            client.loginSuccess.connect(open_main_window)

    app.exec()
