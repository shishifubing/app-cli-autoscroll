from PyQt5.QtCore import Qt
from PyQt5.QtSvg import QSvgWidget

from .functions import get_path


class Icon(QSvgWidget):
    def __init__(self, path: str, size: int) -> None:
        super().__init__(get_path(path))
        self.size = size
        self.resize(self.size, self.size)
        self.renderer().setAspectRatioMode(Qt.KeepAspectRatio)
        self.setWindowFlags(Qt.WindowStaysOnTopHint |
                            Qt.FramelessWindowHint | Qt.X11BypassWindowManagerHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def show(self, x_current: int, y_current: int) -> None:
        half_size = self.size // 2
        self.move(x_current - half_size, y_current - half_size)
        super().show()
