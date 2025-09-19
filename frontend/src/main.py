from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from gui.windows import MainWindow


class ChatAppRTC(QWidget):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("Chat App RTC")
        self.resize(1100, 650)

        # Main window content
        self.main_window = MainWindow()

        # Layout for central widget
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.main_window)

        self.setLayout(layout)

        # Show the window
        self.show()


if __name__ == "__main__":
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
    window = ChatAppRTC()
    app.exec()
