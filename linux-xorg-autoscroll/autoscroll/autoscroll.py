from typing import Any, Dict, List, Tuple, Union
from pynput.mouse import Button, Controller, Listener
from threading import Event, Thread
from time import sleep
from .support import Base, Config, Scrolling, Coordinates, Icon, Buttons, Debug
from .functions import raise_type_error
from .constants import SCROLLING_SLEEP_INTERVAL_INITIAL


class Autoscroll(Base):

    def __init__(self, *args, parse_argv: bool = False, **kwargs) -> None:
        self.scrolling: Scrolling = Scrolling()
        self.icon: Icon = Icon()
        self.config: Config = Config()
        self.buttons: Buttons = Buttons()
        self.debug: Debug = Debug()

        self.event_end: Event = Event()

        self.thread_scroll_listener: Listener = Listener(
            on_move=self._on_move,
            on_click=self._on_click)
        self.thread_scroll: Thread = Thread(
            target=self._loop,
            args=(self._is_not_end, self.scrolling.scroll,
                  {}, {'print_debug': self.debug.scroll}))
        # self.thread_config: Thread = Thread(
        #    target=self._loop,
        #    args=(self.is_not_end_config, self._config))

        self.update(*args, **kwargs)
        if self.config.enable:
            self.update(**self.config.parse_config_file())
        self.update(**self.config.parse_argv() if parse_argv else {})
        self._print('initializer', self.debug.arguments)

    def update(self,
               scrolling: Dict[str, Any] = None,
               icon: Dict[str, Any] = None,
               buttons: Dict[str, Any] = None,
               debug: Dict[str, Any] = None,
               config: Dict[str, Any] = None) -> None:
        self.config.update(**self._convert(config, {}, dict))
        self.scrolling.update(**self._convert(scrolling, {}, dict))
        self.icon.update(**self._convert(icon, {}, dict))
        self.buttons.update(**self._convert(buttons, {}, dict))
        self.debug.update(**self._convert(debug, {}, dict))

    def start(self) -> None:
        self.event_end.clear()
        self.thread_scroll_listener.start()
        self.thread_scroll.start()

    def stop(self) -> None:
        self.event_end.set()
        self.thread_scroll_listener.stop()

    def _on_move(self, x: int, y: int) -> None:
        self.scrolling.set_direction_and_coordinates(x, y)

        distance = self.scrolling.coordinates.distance(absolute=True)
        interval = (self.scrolling.acceleration * max(distance)
                    + self.scrolling.speed)
        self.scrolling.sleep_interval = abs(100 / interval) \
            if interval else SCROLLING_SLEEP_INTERVAL_INITIAL

    def _on_click(self, x: int, y: int, button: Button, pressed: bool) -> None:
        self.buttons.press(button, pressed)
        if self._scroll_has_started(button, pressed):
            self.scrolling.coordinates.initial = x, y
            self.icon.show(x, y)
            self.scrolling.start()
        if self._scroll_has_ended(button, pressed):
            self.scrolling.stop()
            self.icon.close()

        # should be placed at the end to avoid initial scroll jumps
        self.scrolling.set_direction_and_coordinates(x, y)
        # debug
        self._print('click', self.debug.click)
        self.scrolling.stop_started_and_ended()
        self.buttons.press_clear()

    def _is_not_end(self) -> bool: return not self.event_end.is_set()

    def _scroll_has_started(self, button: Button, pressed: bool) -> bool:
        return (not self.scrolling.is_scrolling()
                and self.buttons.is_start(button) and pressed)

    def _scroll_has_ended(self, button: Button, pressed: bool) -> bool:
        return not self.scrolling.has_started() and (
            (self.buttons.is_end(button) and pressed)
            or (self.buttons.hold
                and (self.buttons.is_start(button) and not pressed)))

    def json(self) -> Dict[str, Any]:
        return {'scrolling': self.scrolling, 'buttons': self.buttons,
                'icon': self.icon, 'debug': self.debug, 'config': self.config}

    def __repr__(self) -> str:
        return '\n'.join([str(value) for value in self.json().values()])
