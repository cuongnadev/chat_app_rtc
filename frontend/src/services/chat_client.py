import socket
import threading
import json
import base64
from pathlib import Path
from PySide6.QtCore import QObject, Signal

decoder = json.JSONDecoder()

from utils import ParseStream


class ChatClient(QObject):
    messageReceived = Signal(str, str)  # from, message
    usersUpdated = Signal(list)  # danh sách user online
    loginSuccess = Signal()
    fileReceived = Signal(str, str, bytes)
    # WebRTC signaling
    rtcOfferReceived = Signal(str, str)  # from_username, sdp
    rtcAnswerReceived = Signal(str, str)  # from_username, sdp
    rtcIceReceived = Signal(str, dict)  # from_username, candidate
    rtcEndReceived = Signal(str)  # from_username

    def __init__(self, username, display_name, host="127.0.0.1", port=4105):
        super().__init__()
        self.username = username
        self.display_name = display_name
        self._gui_ready = False  # GUI đã connect signals chưa
        self._cached_users = None  # lưu tạm danh sách users nếu emit trước
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))

        # gửi login info
        login_payload = json.dumps(
            {
                "type": "LOGIN",
                "username": self.username,
                "display_name": self.display_name,
            }
        )
        self.client.sendall(login_payload.encode())

        # start listening thread
        thread = threading.Thread(target=self.listen_server, daemon=True)
        thread.start()

    def listen_server(self):
        buffer = ""
        while True:
            try:
                data = self.client.recv(4096).decode()
                if not data:
                    break

                buffer += data
                new_buffer = ""
                for payload in ParseStream(buffer):
                    if payload["type"] == "LOGIN_OK":
                        # login thành công
                        if not self._gui_ready:
                            self.loginSuccess.emit()  # GUI connect signals
                        # gửi yêu cầu users sau GUI connect
                        self.request_users()
                    elif payload["type"] == "USERS":
                        users = payload.get("users", [])
                        if self._gui_ready:
                            self.usersUpdated.emit(users)
                        else:
                            # lưu tạm
                            self._cached_users = users
                    elif payload["type"] in ("MESSAGE", "BROADCAST"):
                        self.messageReceived.emit(payload["from"], payload["message"])
                    elif payload["type"] == "FILE":
                        # nhận file
                        import base64

                        raw_bytes = base64.b64decode(payload["data"])
                        self.fileReceived.emit(
                            payload["from"], payload["filename"], raw_bytes
                        )
                    # WebRTC signaling messages from server
                    elif payload["type"] == "RTC_OFFER":
                        self.rtcOfferReceived.emit(payload["from"], payload["sdp"])
                    elif payload["type"] == "RTC_ANSWER":
                        self.rtcAnswerReceived.emit(payload["from"], payload["sdp"])
                    elif payload["type"] == "RTC_ICE":
                        self.rtcIceReceived.emit(
                            payload["from"], payload.get("candidate")
                        )
                    elif payload["type"] == "RTC_END":
                        self.rtcEndReceived.emit(payload["from"])

                buffer = new_buffer

            except Exception as e:
                print("Connection closed", e)
                break

    def request_users(self):
        get_users_payload = json.dumps({"type": "GET_USERS"})
        self.client.sendall(get_users_payload.encode())

    def send_message(self, to, msg):
        payload = json.dumps(
            {"type": "MESSAGE", "to": to, "from": self.username, "message": msg}
        )
        self.client.sendall(payload.encode())

    def send_file(self, to: str, file_path: str):
        """Gửi file cho user"""
        path = Path(file_path)
        if not path.exists():
            return
        with open(path, "rb") as f:
            raw = f.read()
        b64 = base64.b64encode(raw).decode()
        payload = json.dumps(
            {
                "type": "FILE",
                "to": to,
                "from": self.username,
                "filename": path.name,
                "data": b64,
            }
        )
        self.client.sendall(payload.encode())

    def gui_ready(self):
        """
        Gọi khi GUI đã connect signals
        để phát dữ liệu cached nếu có
        """
        self._gui_ready = True
        if self._cached_users:
            self.usersUpdated.emit(self._cached_users)
            self._cached_users = None

    # ========== WebRTC signaling senders ==========
    def send_rtc_offer(self, to: str, sdp: str):
        payload = json.dumps(
            {
                "type": "RTC_OFFER",
                "to": to,
                "from": self.username,
                "sdp": sdp,
            }
        )
        self.client.sendall(payload.encode())

    def send_rtc_answer(self, to: str, sdp: str):
        payload = json.dumps(
            {
                "type": "RTC_ANSWER",
                "to": to,
                "from": self.username,
                "sdp": sdp,
            }
        )
        self.client.sendall(payload.encode())

    def send_rtc_ice(self, to: str, candidate: dict):
        payload = json.dumps(
            {
                "type": "RTC_ICE",
                "to": to,
                "from": self.username,
                "candidate": candidate,
            }
        )
        self.client.sendall(payload.encode())

    def send_rtc_end(self, to: str):
        payload = json.dumps(
            {
                "type": "RTC_END",
                "to": to,
                "from": self.username,
            }
        )
        self.client.sendall(payload.encode())
