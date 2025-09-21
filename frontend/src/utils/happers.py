from PySide6.QtGui import QPixmap, QPainter, QPainterPath
from PySide6.QtCore import Qt, QRectF

def RoundedPixmap(path, size=40, roundness=1.0):
    """
    Trả về QPixmap bo góc hoặc tròn từ file path
    :param path: đường dẫn ảnh
    :param size: kích thước final (ảnh vuông)
    :param roundness: 0.0 (vuông) → 1.0 (tròn)
    """
    # Scale ảnh thành hình vuông chính xác
    pixmap = QPixmap(path).scaled(size, size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

    # Pixmap rỗng có nền trong suốt
    rounded = QPixmap(size, size)
    rounded.fill(Qt.transparent)

    painter = QPainter(rounded)
    painter.setRenderHint(QPainter.Antialiasing)

    path_rect = QPainterPath()
    if roundness >= 1.0:
        path_rect.addEllipse(QRectF(0, 0, size, size))
    else:
        radius = size * roundness / 2
        path_rect.addRoundedRect(QRectF(0, 0, size, size), radius, radius)

    painter.setClipPath(path_rect)
    painter.drawPixmap(0, 0, pixmap)
    painter.end()

    return rounded
