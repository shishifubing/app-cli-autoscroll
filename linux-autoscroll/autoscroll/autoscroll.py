from typing import Iterable, Tuple, Union
from pynput.mouse import Button, Listener
from pynput.mouse import Button, Controller, Listener
from threading import Event, Thread
from time import sleep
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtGui import QPixmap
from .functions import get_resource_path


class Icon:
    scroll_mode_entered = pyqtSignal()
    scroll_mode_exited = pyqtSignal()

    def show(self):
        x = self.pos[0] - self.size // 2
        y = self.pos[1] - self.size // 2
        self.move(x, y)
        super().show()

    def __init__(self, path: str, size: int) -> None:
        if isinstance(self, QSvgWidget):
            super().__init__(path)
        elif isinstance(self, QLabel):
            super().__init__()
            self.img = QPixmap(path).scaled(size, size, Qt.KeepAspectRatio)
            self.setPixmap(self.img)

        self.size = size
        self.resize(self.size, self.size)
        self.renderer().setAspectRatioMode(Qt.KeepAspectRatio)
        self.setWindowFlags(Qt.WindowStaysOnTopHint |
                            Qt.FramelessWindowHint | Qt.X11BypassWindowManagerHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.scroll_mode_entered.connect(self.show)
        self.scroll_mode_exited.connect(self.close)


class IconSvg(Icon, QSvgWidget):
    """
    class for svg icons
    """


class IconRaster(Icon, QLabel):
    """
    class for non-svg icons
    """


class Autoscroll:
    """
    enables autoscroll on linux using x-server

    autoscroll means that after you press the button_start you can
    scroll just by moving your mouse, the scrolling will end after
    you press button_end

    Example:
        Autoscroll().start()
    """

    def __init__(
            self,
            delay: int = 5,
            button_start: int = 8,
            button_end: int = 8,
            button_hold: bool = True,
            dead_area: int = 30,
            icon_path: str = None,
            icon_size: int = 30) -> None:
        """
        initializer

        Parameters:
            delay (int):
                speed of scrolling

            button_start (int):
                the button that will start the scrolling mode

            button_end (int):
                the button that will end the scrolling mode

            button_hold (bool):
                if True, button_end is ignored and the scrolling mode will be
                active only while button_start is pressed

            dead_area (int):
                changes the size (in px) of the area below and above
                the starting point where scrolling is paused

            icon_path (str):
                if specified, then the icon on that path will be displayed
                while the scrolling mode is active

                supported formats: svg, png, jpg, jpeg, gif, bmp, pbm, pgm, ppm, xbm, xpm

                the path MUST be absolute

            icon_size (int):
                the size of the icon in px

                only svg images can be resized without loss of quality

        """
        self.delay: int = delay
        self.button_start: Button = Button(button_start)
        self.button_hold: bool = button_hold
        self.button_end: Button = Button(button_end)
        self.dead_area: int = dead_area
        self.icon = icon_path, icon_size
        self.mouse = Controller()
        self.scroll_mode = Event()
        self.listener = Listener(on_move=self.on_move, on_click=self.on_click)

    @property
    def icon(self) -> Union[None, Icon]:
        return self._icon

    @icon.setter
    def icon(self, value: Union[Icon, Tuple[str, int]]) -> None:
        if isinstance(value, (type(None), Icon)):
            self._icon = value
            return
        if not isinstance(value, Iterable) or len(value) < 2:
            raise ValueError(f'value "{str(value)}" is not a valid Iterable')

        icon_path, icon_size = value
        if not icon_path:
            icon_path = str(get_resource_path('resources/img/icon.svg'))
        is_svg = icon_path[-4:].lower() == '.svg'
        icon_class = IconSvg if is_svg else IconRaster
        self._icon = icon_class(icon_path, icon_size)

    def start(self) -> None:
        self.listener.start()
        self.looper = Thread(target=self.loop)
        self.looper.start()

    def loop(self) -> None:
        while True:
            self.scroll_mode.wait()
            sleep(self.interval)
            self.mouse.scroll(0, self.direction)

    def on_move(self, x: int, y: int) -> None:
        if not self.scroll_mode.is_set():
            return

        delta = self.icon.pos[1] - y
        delta_abs = abs(delta)
        if delta_abs <= self.dead_area or not delta:
            self.direction = 0
        else:
            self.direction = -1 if (delta > 0) - 1 else 1
        if delta_abs <= self.dead_area + self.delay * 2:
            self.interval = 0.5
            return
        self.interval = self.delay / (delta_abs - self.dead_area)

    def on_click(self, x: int, y: int, button: Button, pressed: bool) -> None:
        is_start = button == self.button_start
        is_end = button == self.button_end
        is_scroll_mode = self.scroll_mode.is_set()
        start_pressed = is_start and pressed
        start_released = is_start and not pressed and self.button_hold
        end_pressed = is_end and pressed
        if not is_start or not is_end:
            return

        if start_pressed and not is_scroll_mode:
            self.direction = 0
            self.interval = 0.5
            self.scroll_mode.set()
            self.icon.pos = (x, y)
            self.icon.scroll_mode_entered.emit()
        elif (end_pressed or start_released) and is_scroll_mode:
            self.scroll_mode.clear()
            self.icon.scroll_mode_exited.emit()
