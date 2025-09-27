import os
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from gui.windows import MainWindow
from gui.widgets import LoginWindow
from services.chat_client import ChatClient

try:
    from services.webrtc_client import WebRTCClient
    from gui.widgets.video_call_window import VideoCallWindow
    from gui.widgets.incoming_call_dialog import IncomingCallDialog

    WEBRTC_AVAILABLE = True
except ImportError as e:
    WEBRTC_AVAILABLE = False
    WebRTCClient = None
    VideoCallWindow = None
    IncomingCallDialog = None


class ChatAppRTC(QWidget):
    def __init__(self, client: ChatClient):
        super().__init__()
        self.client = client

        # Initialize WebRTC if available
        if WEBRTC_AVAILABLE:
            self.webrtc = WebRTCClient(self.client)
            self._active_call_window = None
        else:
            self.webrtc = None
            self._active_call_window = None

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

        # WebRTC incoming offer (only if available)
        if WEBRTC_AVAILABLE:
            self.client.rtcOfferReceived.connect(self.on_incoming_offer)

        # thông báo ChatClient GUI đã sẵn sàng
        self.client.gui_ready()

        # Layout for central widget
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.main_window)
        self.setLayout(layout)

        # Show the window
        self.show()

        # connect call button (only if WebRTC available)
        if WEBRTC_AVAILABLE:
            self.main_window.chat_panel.chat_header.button.clicked.connect(
                self.start_call
            )
        else:
            self.main_window.chat_panel.chat_header.button.clicked.connect(
                self._show_webrtc_unavailable
            )

    def send_message(self, message: str):
        current_item = self.main_window.chat_list.get_list_widget().currentItem()
        if current_item:
            data = current_item.data(Qt.UserRole)  # giờ dict này có cả username
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
            self.main_window.chat_panel.area_message.append_message(
                "Bạn", os.path.basename(file_path), local_path=file_path, is_sender=True
            )

            # gửi file thực tế qua client
            self.client.send_file(target, file_path)

    def on_file_received(self, sender: str, filename: str, data: bytes):
        # Không hiển thị nếu sender là chính mình
        if sender == self.client.username:
            return
        # hiển thị file dưới dạng "[File]: filename"
        self.main_window.chat_panel.area_message.append_message(
            sender, filename, file_data=data, is_sender=False
        )

    # ========== WebRTC ==========
    def _show_webrtc_unavailable(self):
        """Show message when WebRTC is not available"""
        QMessageBox.warning(
            self,
            "WebRTC Not Available",
            "Video calling is not available.\n\n"
            "Please install dependencies:\n"
            "pip install -r requirements.txt\n\n"
            "Make sure you have:\n"
            "- aiortc\n"
            "- opencv-python\n"
            "- pyaudio",
        )

    def start_call(self):
        if not WEBRTC_AVAILABLE or not self.webrtc:
            self._show_webrtc_unavailable()
            return

        current_item = self.main_window.chat_list.get_list_widget().currentItem()
        if not current_item:
            return
        data = current_item.data(Qt.UserRole)
        partner_username = data["username"]
        partner_display = data["name"]
        # show window
        self._active_call_window = VideoCallWindow(self.webrtc, partner_display)
        self._active_call_window.show()
        # initiate call
        self.webrtc.start_call(partner_username)

    def on_incoming_offer(self, from_username: str, sdp: str):
        if not WEBRTC_AVAILABLE or not self.webrtc:
            # Decline the call since we can't handle it
            self.client.send_rtc_end(from_username)
            return

        # find display name from current user list
        partner_display = from_username
        # prompt
        dlg = IncomingCallDialog(partner_display)
        if dlg.exec() == IncomingCallDialog.Accepted:
            # show window and accept
            self._active_call_window = VideoCallWindow(self.webrtc, partner_display)
            self._active_call_window.show()
            self.webrtc.accept_offer(from_username, sdp)
        else:
            # decline by sending end
            self.client.send_rtc_end(from_username)


if __name__ == "__main__":
    print("🎥 Starting Chat App RTC Client...")
    print("Make sure the server is running first!")
    print("-" * 50)

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
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    login = LoginWindow()

    if login.exec() == LoginWindow.Accepted:
        client = login.client
        client.connectionFailed.connect(
            lambda msg: QMessageBox.critical(None, "Lỗi kết nối", f"{msg}")
        )
        main_window = ChatAppRTC(client)

    sys.exit(app.exec())
