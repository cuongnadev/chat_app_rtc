from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog
from PySide6.QtCore import Qt
from pathlib import Path
import os
import subprocess  # để mở file trên máy

class ChatBubble(QWidget):
    def __init__(self, sender, message, is_sender=False, file_data: bytes = None, local_path: str = None):
        super().__init__()
        self.is_sender = is_sender
        self.file_data = file_data      # bytes nếu nhận từ server
        self.local_path = local_path    # đường dẫn file nếu là sender có trên máy

        self.name_label = QLabel(sender)
        self.name_label.setStyleSheet("font-size: 12px; color: gray;")

        v_layout = QVBoxLayout()
        if not self.is_sender:
            v_layout.addWidget(self.name_label)

        if file_data or local_path:
            # là file: tạo widget hiển thị file
            filename = message  # message là tên file
            file_layout = QHBoxLayout()
            
            # label tên file
            file_label = QLabel(filename)
            file_label.setStyleSheet("background-color: #F1F1F1; padding: 6px 12px; border-radius: 8px;")
            
            # nút hành động
            btn = QPushButton()
            btn.setFixedSize(24,24)
            btn.setStyleSheet("border:none;")
            
            if self.is_sender and local_path:
                # nút mở file sender
                btn.setText("📂")
                btn.clicked.connect(self.open_local_file)
            else:
                # nút tải file nhận
                btn.setText("⬇️")
                btn.clicked.connect(self.save_file)
            
            file_layout.addWidget(file_label)
            file_layout.addWidget(btn)
            v_layout.addLayout(file_layout)
        else:
            # text bình thường
            msg_label = QLabel(message)
            msg_label.setWordWrap(True)
            msg_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            if self.is_sender:
                msg_label.setStyleSheet("background-color:#615EF0;color:white;border-radius:12px;padding:8px 16px;")
            else:
                msg_label.setStyleSheet("background-color:#F1F1F1;color:black;border-radius:12px;padding:8px 16px;")
            v_layout.addWidget(msg_label)

        h_layout = QHBoxLayout(self)
        if self.is_sender:
            h_layout.addStretch()
            h_layout.addLayout(v_layout)
        else:
            h_layout.addLayout(v_layout)
            h_layout.addStretch()

    def open_local_file(self):
        """Mở file đã có trên máy sender"""
        if self.local_path and os.path.exists(self.local_path):
            if os.name == "nt":
                os.startfile(self.local_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", self.local_path])
            else:
                subprocess.run(["xdg-open", self.local_path])

    def save_file(self):
        """Lưu file nhận từ server"""
        if self.file_data:
            filename = "file_received"
            path, _ = QFileDialog.getSaveFileName(self, "Save File", filename)
            if path:
                with open(path, "wb") as f:
                    f.write(self.file_data)
