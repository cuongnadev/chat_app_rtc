from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PySide6.QtGui import QPixmap, QMouseEvent
from PySide6.QtCore import Qt, Signal

class Button(QWidget):
    clicked = Signal() 
    def __init__(
        self,
        text="",
        icon_path=None,
        icon_on_left=True,
        bg_color="rgba(97, 94, 240, 0.10)",
        hover_color="rgba(97, 94, 240, 0.15)",
        pressed_color="rgba(97, 94, 240, 0.25)",
        text_color="#615EF0",
        parent=None
    ):
        super().__init__(parent)
        self.setObjectName("Button")
        # allow stylesheet to paint the widget background
        self.setAttribute(Qt.WA_StyledBackground, True)

        # Cho QWidget tự vẽ nền
        self.setAutoFillBackground(True)

        # Style mặc định
        self.setStyleSheet(f"""
            #Button {{
                background-color: {bg_color};
                border-radius: 8px;
            }}
            #Button:hover {{
                background-color: {hover_color};
            }}
            #Button:pressed {{
                background-color: {pressed_color};
            }}
        """)

        # Layout
        button_layout = QHBoxLayout(self)
        button_layout.setContentsMargins(16, 10, 16, 10)
        button_layout.setSpacing(8)


        if icon_on_left:
            # Icon
            if icon_path:
                self.icon_label = QLabel()
                self.icon_label.setStyleSheet("background-color: transparent")
                pixmap = QPixmap(icon_path).scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.icon_label.setPixmap(pixmap)
                button_layout.addWidget(self.icon_label)


            # Text
            if text.strip():
                self.text_label = QLabel(text)
                self.text_label.setStyleSheet(f"color: {text_color}; font-size: 16px; font-weight: bold; background-color: transparent;")
                button_layout.addWidget(self.text_label)
        else:
            # Text
            if text.strip():
                self.text_label = QLabel(text)
                self.text_label.setStyleSheet(f"color: {text_color}; font-size: 16px; font-weight: bold; background-color: transparent;")
                button_layout.addWidget(self.text_label)

            # Icon
            if icon_path:
                self.icon_label = QLabel()
                self.icon_label.setStyleSheet("background-color: transparent")
                pixmap = QPixmap(icon_path).scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.icon_label.setPixmap(pixmap)
                button_layout.addWidget(self.icon_label)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()  # phát signal khi nhả chuột
        super().mousePressEvent(event)
