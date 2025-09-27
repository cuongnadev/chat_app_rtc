import socket
from PySide6.QtCore import QThread, Signal
from services.chat_client import ChatClient

class ConnectThread(QThread):
    finished = Signal(object)  # emit client hoặc None nếu fail

    def __init__(self, username, display_name, server_ip, parent=None):
        super().__init__(parent)
        self.username = username
        self.display_name = display_name
        self.server_ip = server_ip

    def run(self):
        try:
            client = ChatClient(self.username, self.display_name)
            success = client.connect_to_server(host=self.server_ip, port=4105, timeout=3.0)
            self.finished.emit(client if success else None)
        except Exception as e:
            print("ConnectThread exception:", e)
            self.finished.emit(None)