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
        self.client.messageReceived.connect(self.on_message_received)

        # khi bấm gửi tin nhắn
        self.main_window.chat_panel.area_message.messageSent.connect(self.send_message)
        # khi chọn file
        self.main_window.chat_panel.area_message.file_selected.connect(self.send_file)
        # khi nhận file
        self.client.fileReceived.connect(self.on_file_received)


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
            target = data["username"]  # lấy username
            self.client.send_message(target, message)

    def on_message_received(self, sender, message):
        """Nhận tin nhắn từ server rồi append vào chat"""
        self.main_window.chat_panel.area_message.append_message(sender, message)

    def send_file(self, file_path: str):
        print("send_file called", file_path)
        """Gửi file"""
        current_item = self.main_window.chat_list.get_list_widget().currentItem()
        
        if current_item:
            data = current_item.data(Qt.UserRole)
            target = data["username"]

            # hiển thị bubble sender với nút mở file
            self.main_window.chat_panel.area_message.append_message("Bạn", 
                os.path.basename(file_path), local_path=file_path, is_sender=True)

            # gửi file thực tế qua client
            self.client.send_file(target, file_path)

    def on_file_received(self, sender: str, filename: str, data: bytes):
        # Không hiển thị nếu sender là chính mình
        if sender == self.client.username:
            return
        # hiển thị file dưới dạng "[File]: filename"
        self.main_window.chat_panel.area_message.append_message(
        sender, filename, file_data=data, is_sender=False)


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
