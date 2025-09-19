from PySide6.QtGui import QPixmap, QPainter, QPainterPath
from PySide6.QtCore import Qt, QRectF

def RoundedPixmap(path, size=40):
    """Trả về QPixmap hình tròn từ file path"""
    # Load ảnh
    pixmap = QPixmap(path).scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

    # Tạo QPixmap rỗng
    rounded = QPixmap(size, size)
    rounded.fill(Qt.transparent)

    # Vẽ mask tròn
    painter = QPainter(rounded)
    painter.setRenderHint(QPainter.Antialiasing)
    path_circle = QPainterPath()
    path_circle.addEllipse(QRectF(0, 0, size, size))
    painter.setClipPath(path_circle)
    painter.drawPixmap(0, 0, pixmap)
    painter.end()

    return rounded
