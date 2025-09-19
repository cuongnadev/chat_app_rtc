from PySide6.QtWidgets import (
    QApplication, QWidget
)

from gui.windows import MainWindow

class ChatAppRTC(QWidget):
    def __init__(self):
        super().__init__()


        # main window
        self.main_window = MainWindow()
        self.main_window.show()


if __name__ == "__main__":
    app = QApplication([])
    window = ChatAppRTC()
    app.exec()