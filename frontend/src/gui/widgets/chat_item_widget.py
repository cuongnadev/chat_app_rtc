from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from utils.happers import RoundedPixmap


class ChatItemWidget(QWidget):
    def __init__(
        self,
        avatar_path: str,
        name_text: str,
        last_message: str = "",
        last_active_time: str = "",
        parent=None,
    ):
        super().__init__(parent)

        self.setStyleSheet(
            """
            QWidget {
                background-color: #FFFFFF;
                padding: 0px;
                margin: 0px;
            }
        """
        )
        self.setCursor(QCursor(Qt.PointingHandCursor))

        # main_layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(20)

        # avatar
        self.avatar = QLabel()
        self.avatar.setPixmap(RoundedPixmap(avatar_path, 50, 1.0))
        self.avatar.setStyleSheet("background: transparent;")
        main_layout.addWidget(self.avatar)

        # left_content
        left_content = QVBoxLayout()
        left_content.setContentsMargins(0, 0, 0, 0)
        left_content.setSpacing(10)
        left_content.setAlignment(Qt.AlignVCenter)
        main_layout.addLayout(left_content)

        # info_layout
        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)

        # name
        self.name = QLabel(name_text)
        self.name.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #1A202C;
                background-color: transparent;
            }
        """
        )
        self.name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        info_layout.addWidget(self.name)

        info_layout.addStretch()

        # last active time
        self.last_active = QLabel(last_active_time)
        self.last_active.setStyleSheet(
            """
            QLabel {
                font-size: 12px;
                color: #A0AEC0;
                background-color: transparent;
            }
        """
        )
        info_layout.addWidget(self.last_active)

        left_content.addLayout(info_layout)

        # last message
        self.message = QLabel(last_message)
        self.message.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                color: #A0AEC0;
                background-color: transparent;
            }
        """
        )
        left_content.addWidget(self.message)

        main_layout.setAlignment(Qt.AlignLeft)
        self.setLayout(main_layout)
