from PySide6.QtWidgets import QWidget, QLineEdit, QHBoxLayout, QVBoxLayout, QFileDialog
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon, QCursor
from pathlib import Path

from gui.widgets.button import Button
from gui.widgets.chat_area import ChatArea

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = BASE_DIR / "assets"

class AreaMessage(QWidget):
    messageSent = Signal(str) # phát ra nội dung tin nhắn khi gửi
    file_selected = Signal(str) # phát tín hiệu ra khi người dùng chọn file

    def __init__(self):
        super().__init__()

        # Khung hiển thị tin nhắn
        self.chat_display = ChatArea()

        # paperclip
        self.paperclip_button = Button("", str(ASSETS_DIR / "paperclip.svg"), True, "transparent")
        self.paperclip_button.clicked.connect(self.open_file_dialog)
        self.paperclip_button.setCursor(QCursor(Qt.PointingHandCursor))

        # Ô nhập tin nhắn
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type a message")
        self.message_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #E2E8F0;
                border-radius: 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #615EF0;
            }
        """)

        # mic action
        icon_default = QIcon(str(ASSETS_DIR / "mic.svg"))
        # tạo pixmap 24x24
        pixmap = icon_default.pixmap(40, 40)
        big_icon = QIcon(pixmap)

        self.mic_action = self.message_input.addAction(
            big_icon, QLineEdit.TrailingPosition
        )
        self.mic_action.triggered.connect(self.start_recording)

        # Nút gửi
        self.send_button = Button("", str(ASSETS_DIR / "send.svg"), True, "transparent")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setCursor(QCursor(Qt.PointingHandCursor))

        # Layout nhập tin nhắn
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.paperclip_button)
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
            # hiển thị bubble của mình
            self.chat_display.add_message("Bạn", message, is_sender=True)
            self.messageSent.emit(message)  # gửi signal ra ngoài
            self.message_input.clear()

    def append_message(self, sender: str, message: str, is_sender=False, file_data=None, local_path=None):
        # hiển thị bubble người khác
        self.chat_display.add_message(sender, message, is_sender=is_sender, file_data=file_data, local_path=local_path)

    def clear_message(self):
        # xóa hết bubble (remove tất cả widgets)
        while self.chat_display.v_layout.count() > 1:  # chừa lại stretch
            item = self.chat_display.v_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn file để gửi", "", "Tất cả (*)")
        if file_path:
            # # hiển thị bubble sender với nút mở file
            # self.append_message("Bạn", Path(file_path).name, local_path=file_path, is_sender=True)
            self.file_selected.emit(file_path)

    def start_recording(self):
        print("Mic clicked - start recording")
