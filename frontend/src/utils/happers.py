from PySide6.QtGui import QPixmap, QPainter, QPainterPath
from PySide6.QtCore import Qt, QRectF

def RoundedPixmap(path, size=40, roundness=1.0):
    """
    Trả về QPixmap bo góc từ file path
    :param path: đường dẫn ảnh
    :param size: kích thước final
    :param roundness: độ bo, từ 0.0 (không bo) đến 1.0 (bo tròn hoàn toàn)
    """
    pixmap = QPixmap(path).scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

    rounded = QPixmap(size, size)
    rounded.fill(Qt.transparent)

    painter = QPainter(rounded)
    painter.setRenderHint(QPainter.Antialiasing)

    path_rect = QPainterPath()

    # Tính bán kính theo roundness
    radius = size * roundness / 2  # roundness=1 → full circle, roundness=0 → không bo
    path_rect.addRoundedRect(QRectF(0, 0, size, size), radius, radius)

    painter.setClipPath(path_rect)
    painter.drawPixmap(0, 0, pixmap)
    painter.end()

    return rounded