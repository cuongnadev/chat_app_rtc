# This file contains helper functions for the PySide6 GUI,
# specifically for creating rounded pixmaps from image files.

from PySide6.QtGui import QPixmap, QPainter, QPainterPath
from PySide6.QtCore import Qt, QRectF

def RoundedPixmap(path, size=40, roundness=1.0):
    pixmap = QPixmap(path).scaled(size, size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

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