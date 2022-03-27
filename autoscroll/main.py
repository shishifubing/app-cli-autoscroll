#!/usr/bin/env python3

from sys import exit as sys_exit, argv as sys_argv
from .autoscroll import Autoscroll, QApplication, Icon, get_path


def start() -> None:

    scroll = Autoscroll()
    scroll.start(parse_argv=True)
    # application.setActiveWindow(scroll.icon.icon)
    #icon = Icon('resources/img/white.svg', 100)
    # application.setActiveWindow(icon)
    #icon.show(400, 400)
    return


if __name__ == '__main__':
    sys_exit(start())
