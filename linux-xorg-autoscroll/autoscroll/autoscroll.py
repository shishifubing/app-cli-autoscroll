from typing import Iterable, List, Tuple, Union
from pynput.mouse import Button, Controller, Listener
from threading import Event, Thread
from time import sleep
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtGui import QPixmap
from .functions import (
    convert_button, get_resource_path, convert, print_mouse_action)


class Icon:
    """
    base icon class
    """
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
            image = QPixmap(path).scaled(size, size, Qt.KeepAspectRatio)
            self.setPixmap(image)

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
    enables autoscroll on linux using xorg-server

    autoscroll means that while you hold "button_start", you can scroll just by
    moving your mouse, the scrolling will end after you release the button,

    if "button_hold" is set to "False", the scrolling will end only after you
    press "button_end"

    to find the number of the button use "xinput test" (requires xinput package)
    or start with show_buttons as True

    Example:
        Autoscroll().start()
    """

    def __init__(
            self,
            delay: Union[str, int] = None,
            button_start: Union[str, int] = None,
            button_end: Union[str, int] = None,
            button_hold: Union[str, bool] = None,
            dead_area: Union[str, int] = None,
            icon_path: str = None,
            icon_size: Union[str, int] = None,
            show_buttons: bool = False,
            show_movement: bool = False,
            **kwargs) -> None:
        """
        initializer

        Parameters:
            delay (int):
                speed of scrolling, defaults to 5

            button_start (int):
                the button that will start the scrolling mode, defaults to 8

            button_end (int):
                the button that will end the scrolling mode, defaults to 8

            button_hold (bool):
                if True, button_end is ignored and the scrolling mode will be
                active only while button_start is pressed, defaults to True

            dead_area (int):
                changes the size (in px) of the area below and above
                the starting point where scrolling is paused, defaults to 20

            icon_path (str):
                if specified, then the icon on that path will be displayed
                while the scrolling mode is active,
                defaults to resources/img/icon.svg

                supported formats: svg, png, jpg, jpeg, gif, bmp, pbm, pgm, ppm, xbm, xpm

            icon_size (int):
                the size of the icon in px, defaults to 30

                only svg images can be resized without loss of quality

            show_buttons (bool):
                if True, button clicks will be printed to stdout, defaults to False

            show_movement (bool):
                if True, mouse movements will be printed to stdout, defaults to False

            **kwargs: kwargs are ignored
        """
        self.delay: int = convert(delay, int, 5)
        self.button_start: Button = convert_button(button_start, 8)
        self.button_hold: bool = convert(button_hold, bool, True)
        self.button_end: Button = convert_button(button_end, 8)
        self.dead_area: int = convert(dead_area, int, 20)
        self.icon: Icon = icon_path, icon_size
        self.show_buttons: bool = show_buttons
        self.show_movement: bool = show_movement

        self.mouse: Controller = Controller()
        self.scroll_mode: Event = Event()
        self.listener = Listener(on_move=self.on_move, on_click=self.on_click)

    @property
    def icon(self) -> Union[None, Icon]:
        return self._icon

    @icon.setter
    def icon(self, value: Union[Icon, Tuple[str, int]]) -> None:
        if isinstance(value, Icon):
            self._icon = value
            return
        if not isinstance(value, Iterable) or len(value) < 2:
            raise ValueError(f'value "{str(value)}" is not a valid Iterable')

        icon_path, icon_size = value
        if not icon_path:
            icon_path = get_resource_path('resources/img/icon.svg')
        is_svg = icon_path[-4:].lower() == '.svg'
        icon_class = IconSvg if is_svg else IconRaster
        self._icon = icon_class(icon_path, convert(icon_size, int, 30))

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
        print_mouse_action(self.show_movement, x, y, None, None,
                           self.button_hold, self.scroll_mode.is_set())
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

        if start_pressed and not is_scroll_mode:
            self.direction = 0
            self.interval = 0.5
            self.scroll_mode.set()
            self.icon.pos = (x, y)
            self.icon.scroll_mode_entered.emit()
        elif (end_pressed or start_released) and is_scroll_mode:
            self.scroll_mode.clear()
            self.icon.scroll_mode_exited.emit()
        print_mouse_action(self.show_buttons, x, y, button, pressed,
                           self.button_hold, is_scroll_mode, is_start, is_end)
