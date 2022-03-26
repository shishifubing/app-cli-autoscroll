from .support import Base, Config, Scrolling, Icon, Buttons, Debug
from typing import Any, Dict
from pynput.mouse import Button, Listener
from threading import Event, Thread
from time import sleep
from signal import SIGABRT, SIGHUP, SIGKILL, signal as signal_signal, SIGINT, SIGTERM


class Autoscroll(Base):

    def __init__(self, *args, **kwargs) -> None:
        self.scrolling: Scrolling = Scrolling()
        self.icon: Icon = Icon()
        self.config: Config = Config()
        self.buttons: Buttons = Buttons()
        self.debug: Debug = Debug()
        self.event_end: Event = Event()

        self.update(*args, **kwargs)
        self._print('initializer', self.debug.arguments)

        # all threads used
        self.thread_scroll_listener: Listener = Listener(
            on_move=self._on_move,
            on_click=self._on_click,
            daemon=True)
        self.thread_scrolling: Thread = Thread(
            target=self._loop,
            args=(self._is_not_end, self._scroll),
            daemon=True)
        self.thread_config: Thread = Thread(
            target=self._loop,
            args=(self._is_not_end, self._update_from_config_file),
            daemon=True)

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

    def start(self, parse_argv: bool = False) -> None:
        self.update(**self.config.parse_argv() if parse_argv else {})
        self.thread_scrolling.start()
        self.thread_scroll_listener.start()
        self.thread_config.start()

    def stop(self) -> None:
        self.thread_scroll_listener.stop()
        self.scrolling.event_end.set()
        self.event_end.set()

    def _update_from_config_file(self) -> None:
        self.config.event_enabled.wait()
        self.update(**self.config.parse_config_file())
        sleep(self.config.interval)

    def _scroll(self) -> None:
        # wait for the scrolling event to be set in _on_click
        self.scrolling.wait()
        # wait for a period of time, calculated in _on_move
        self.scrolling.sleep_for_interval()
        # scroll on x-axis and y-axis, each scroll is either 1px, 0px, or -1px
        self.scrolling.scroll_once()

    def _on_move(self, x: int, y: int) -> None:
        self.scrolling.set_direction_and_coordinates(x, y)
        self.scrolling.set_interval()

    def _on_click(self, x: int, y: int, button: Button, pressed: bool) -> None:
        # sends information about which button was pressed/released
        self.buttons.press(button, pressed)

        if not self.scrolling.is_scrolling() and self.buttons.was_start_pressed():
            self.scrolling.set_initial_coordinates(x, y)
            self.icon.show(x, y)
            self.scrolling.start()
        elif self.buttons.was_end_pressed() or self.buttons.was_start_released():
            self.scrolling.stop()
            self.icon.close()

        # should be placed at the end to avoid initial scroll jumps
        self.scrolling.set_direction_and_coordinates(x, y)
        # debug
        self._print('click', self.debug.click)
        self.scrolling.clear_started_and_ended()
        self.buttons.press_clear()

    def _is_not_end(self) -> bool: return not self.event_end.is_set()

    def json(self) -> Dict[str, Any]:
        return {'scrolling': self.scrolling, 'buttons': self.buttons,
                'icon': self.icon, 'debug': self.debug, 'config': self.config}
