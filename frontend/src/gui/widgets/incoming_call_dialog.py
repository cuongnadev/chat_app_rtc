from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt


class IncomingCallDialog(QDialog):
    def __init__(self, caller_display: str):
        super().__init__()
        self.setWindowTitle("Incoming Call")
        self.resize(360, 160)
        layout = QVBoxLayout()

        label = QLabel(f"Incoming video call from {caller_display}")
        label.setAlignment(Qt.AlignCenter)

        buttons = QHBoxLayout()
        self.accept_btn = QPushButton("Accept")
        self.decline_btn = QPushButton("Decline")
        self.accept_btn.setDefault(True)
        buttons.addWidget(self.accept_btn)
        buttons.addWidget(self.decline_btn)

        layout.addWidget(label)
        layout.addLayout(buttons)
        self.setLayout(layout)

        self.accept_btn.clicked.connect(self.accept)
        self.decline_btn.clicked.connect(self.reject)
