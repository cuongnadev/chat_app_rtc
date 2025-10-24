import socket
import threading
import json
import base64
from pathlib import Path
from PySide6.QtCore import QObject, Signal

decoder = json.JSONDecoder()

from utils.parse import ParseStream


class ChatClient(QObject):
    messageReceived = Signal(str, str, str)  # from, message
    groupMessageReceived = Signal(str, str, str)
    usersUpdated = Signal(list)  # list of online users
    loginSuccess = Signal()
    connectionFailed = Signal(str)
    fileReceived = Signal(str, str, bytes)
    # WebRTC signaling
    rtcOfferReceived = Signal(str, str)  # from_username, sdp
    rtcAnswerReceived = Signal(str, str)  # from_username, sdp
    rtcIceReceived = Signal(str, dict)  # from_username, candidate
    rtcEndReceived = Signal(str)  # from_username

    def __init__(self, username, display_name):
        super().__init__()
        self.username = username
        self.display_name = display_name
        self._gui_ready = False  # GUI has connected signals
        self._cached_users = None  # temporarily store user list if emitted before
        self.client = None  # not create socket yet
        self._listening_thread = None

    def connect_to_server(self, host: str, port: int = 4105, timeout: float = 3.0):
        """Connect socket with timeout"""
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # set short timeout
        self.client.settimeout(timeout)

        try:
            self.client.connect((host, port))
        except Exception as e:
            self.connectionFailed.emit(str(e))
            return False

        self.client.settimeout(None)  # transfer to blocking mode

        # send login
        login_payload = json.dumps({
            "type": "LOGIN",
            "username": self.username,
            "display_name": self.display_name,
        })
        try:
            self.client.sendall(login_payload.encode())
        except Exception as e:
            self.connectionFailed.emit(str(e))
            return False

        # start listening thread
        self._listening_thread = threading.Thread(target=self.listen_server, daemon=True)
        self._listening_thread.start()
        return True


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
                        from_username = payload.get("from_username", None)
                        self.messageReceived.emit(payload["from"], payload["message"], from_username)

                    elif payload["type"] == "FILE":
                        # nhận file
                        import base64

                        raw_bytes = base64.b64decode(payload["data"])
                        self.fileReceived.emit(
                            payload["from"], payload["filename"], raw_bytes
                        )

                    elif payload["type"] == "GROUP_MESSAGE":
                        from_user = payload["from"]
                        group_name = payload["group_name"]
                        message = payload["message"]
                        self.groupMessageReceived.emit(group_name, from_user, message)

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

    def create_group(self, group_name, members):
        payload = json.dumps({
            "type": "CREATE_GROUP",
            "group_name": group_name,
            "members": members
        })
        self.client.sendall(payload.encode())
        print("📤 Sending CREATE_GROUP:", payload)

    def send_group_message(self, group_name, msg):
        payload = json.dumps({
            "type": "GROUP_MESSAGE",
            "group_name": group_name,
            "from": self.username,
            "message": msg
        })
        self.client.sendall(payload.encode())

    def join_group(self, group_name):
        payload = json.dumps({
            "type": "JOIN_GROUP",
            "username": self.username,
            "group_name": group_name
        })
        self.client.sendall(payload.encode())
