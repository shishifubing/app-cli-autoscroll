from enum import Enum
from typing import Any, Dict, Tuple
from argparse import RawDescriptionHelpFormatter
from os import environ as os_environ
from .functions import get_resource_content

SCROLLING_SPEED: int = 300
SCROLLING_ACCELERATION_DISTANCE: int = 10
SCROLLING_SLEEP_INTERVAL_INITIAL: float = 0.1
SCROLLING_DEAD_AREA: int = 50
SCROLLING_AUTOSCROLL: bool = True

BUTTONS_START: int = 2
BUTTONS_HOLD: bool = False

ICON_ENABLE: bool = False
ICON_SIZE: int = 30
ICON_PATH: str = 'resources/img/icon.svg'
ICON_ERROR: str = 'you enabled the icon ("enable" is "True") but the qt5 package is not installed'

CONFIG_PATH: str = f'{os_environ.get("HOME")}/.config/autoscroll/config.txt'
CONFIG_ENABLE: bool = False
CONFIG_LISTEN: bool = False
CONFIG_SLEEP: int = 5
CONFIG_ERROR_ENABLE: str = 'you are trying to enable the config (\'enable\' is set to \'True\'), but the path is not valid'
CONFIG_ERROR_PARSE: str = 'you are trying to parse the config file, but \'enable\' is \'False\''

DEBUG_SCROLL: bool = False
DEBUG_CLICK: bool = False
DEBUG_ARGUMENTS: bool = False
DEBUG_PADDING: int = 16

COORDINATE_NAME: str = 'coordinates'

PARSER_INITIALIZER: Dict[str, Any] = {
    'prog': 'linux-xorg-autoscroll',
    'formatter_class': RawDescriptionHelpFormatter,
    'description': get_resource_content('resources/txt/prolog.txt')}


class Arguments(Enum):
    enable = 0
    scrolling = 1
    buttons = 2
    icon = 3
    debug = 4


def construct(argument): return f'-{argument.name[0]}', f'--{argument.name}'


meta = {'nargs': 2, 'action': 'append', 'metavar': ''}


ARGUMENTS: Tuple[Tuple[Tuple[str, str], Dict[str, Any]]] = (
    (construct(Arguments.scrolling),
     {'help': 'speed dead_area acceleration', **meta}),
    (construct(Arguments.buttons),
     {'help': f'hold start end', **meta}),
    (construct(Arguments.icon),
     {'help': f'enable path size', **meta}),
    (construct(Arguments.debug),
     {'help': 'Debug options. If "scroll" is passed, scroll information will be printed to stdout. If "click" is passed, click information will be printed to stdout.',
      'nargs': '*', 'metavar': ('scroll', 'click')}))
