from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from gui.windows import MainWindow


class ChatAppRTC(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("Chat App RTC")
        self.resize(1100, 650)

        # Set background color for the main window
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #F7FAFC;
            }
        """
        )

        # Central widget
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #F7FAFC;")
        self.setCentralWidget(central_widget)

        # Main window content
        self.main_window = MainWindow()

        # Layout for central widget
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.main_window)

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
