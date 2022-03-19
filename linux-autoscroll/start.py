#!/usr/bin/env python3

from sys import exit as sys_exit, argv as sys_argv
from pynput.mouse import Listener
from .autoscroll.autoscroll import Autoscroll
from PyQt5.QtWidgets import QApplication


def display_button_name_listener(start: bool = False) -> None:
    if not start:
        return
    click = lambda *args, button, **kwargs: print(button)
    with Listener(on_click=click) as listener:
        listener.join()


def main() -> int:
    display_button_name_listener('button' in sys_argv)

    app = QApplication(sys_argv)
    app.setQuitOnLastWindowClosed(False)
    Autoscroll().start()
    return app.exec()


if __name__ == '__main__':
    sys_exit(main())
