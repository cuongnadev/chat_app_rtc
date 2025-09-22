import socket
import threading
import json
from PySide6.QtCore import QObject, Signal

decoder = json.JSONDecoder()

from utils import ParseStream


class ChatClient(QObject):
    messageReceived = Signal(str, str)      # from, message
    usersUpdated = Signal(list)             # danh sách user online
    loginSuccess = Signal()

    def __init__(self, username, display_name, host="127.0.0.1", port=4105):
        super().__init__()
        self.username = username
        self.display_name = display_name
        self._gui_ready = False          # GUI đã connect signals chưa
        self._cached_users = None       # lưu tạm danh sách users nếu emit trước
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))

        # gửi login info
        login_payload = json.dumps({
            "type": "LOGIN",
            "username": self.username,
            "display_name": self.display_name
        })
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

                buffer = new_buffer

            except Exception as e:
                print("Connection closed", e)
                break

    def request_users(self):
        get_users_payload = json.dumps({"type": "GET_USERS"})
        self.client.sendall(get_users_payload.encode())

    def send_message(self, to, msg):
        payload = json.dumps({
            "type": "MESSAGE",
            "to": to,
            "from": self.username,
            "message": msg
        })
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
