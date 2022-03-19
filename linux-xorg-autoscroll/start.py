#!/usr/bin/env python3

from .autoscroll.functions import parse_arguments
from .autoscroll.autoscroll import Autoscroll
from PyQt5.QtWidgets import QApplication
from sys import exit as sys_exit


def main() -> int:
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    Autoscroll(**vars(parse_arguments())).start()
    return app.exec()


if __name__ == '__main__':
    sys_exit(main())
