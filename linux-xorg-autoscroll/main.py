#!/usr/bin/env python3

from PyQt5.QtWidgets import QApplication
from sys import exit as sys_exit, argv as sys_argv
from .autoscroll import Autoscroll


def main() -> int:
    app = QApplication(sys_argv)
    app.setQuitOnLastWindowClosed(False)
    Autoscroll(parse_argv=True).start()
    return app.exec()


if __name__ == '__main__':
    sys_exit(main())
