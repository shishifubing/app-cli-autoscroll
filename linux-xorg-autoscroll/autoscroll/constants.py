from typing import Any, Dict, List, Tuple
from os import environ as os_environ
from .functions import construct_argument, get_resource_content, convert_bool
from .arguments import ArgparseFormatter

SCROLLING_SPEED: int = 300
SCROLLING_ACCELERATION_DISTANCE: int = 10
SCROLLING_SLEEP_INTERVAL_INITIAL: float = 0.1
SCROLLING_DEAD_AREA: int = 50

BUTTONS_START: int = 2
BUTTONS_HOLD: bool = False

ICON_ENABLE: bool = False
ICON_SIZE: int = 30
ICON_PATH: str = 'resources/img/icon.svg'
ICON_ERROR: str = 'you enabled the icon ("enable" is "True") but the qt5 package is not installed'

CONFIG_PATH: str = f'{os_environ.get("HOME")}/.config/autoscroll/config.txt'
CONFIG_ENABLE: bool = False
CONFIG_INTERVAL: int = 5
CONFIG_ERROR_ENABLE: str = 'you are trying to enable the config (\'enable\' is set to \'True\'), but the path is not valid'
CONFIG_ERROR_PARSE: str = 'you are trying to parse the config file, but \'enable\' is \'False\''

DEBUG_SCROLL: bool = False
DEBUG_CLICK: bool = False
DEBUG_ARGUMENTS: bool = False
DEBUG_PADDING: int = 16

COORDINATE_NAME: str = 'coordinates'


PARSER_INITIALIZER: Dict[str, Any] = {
    'prog': 'linux-xorg-autoscroll',
    'formatter_class': ArgparseFormatter,
    'description': get_resource_content('resources/txt/prolog.txt'),
    'fromfile_prefix_chars': '@'}

ARGUMENTS: Dict[str, Any] = {
    'scrolling': {
        'description': 'Scrolling options',
        'parameters': {
            'speed': {
                'default': SCROLLING_SPEED,
                'type': int,
                'help': 'R|constant part of the scrolling speed',
            },
            'dead-area': {
                'default': SCROLLING_DEAD_AREA,
                'type': int,
                'help': ('R|size of the square area aroung the starting '
                         'point where scrolling will stop, in pixels')
            },
            'acceleration': {
                'default': SCROLLING_ACCELERATION_DISTANCE,
                'type': int,
                'help': ('R|dynamic part of the  scrolling speed, depends on the '
                         'distance from the point where the scrolling started, '
                         'can be set to 0')
            },
        }
    },
    'buttons': {
        'description': ('Button options\nOnce --buttons-start is pressed, '
                        'the scrolling starts, when --buttons-end is '
                        'pressed, it ends'),
        'parameters': {
            'hold': {
                'default': BUTTONS_HOLD,
                'action': 'store_true',
                'help': ('R|if set, the scrolling will end once you release '
                         '--buttons-start')
            },
            'start': {
                'default': BUTTONS_START,
                'type': int,
                'help': 'R|button that starts the scrolling'
            },
            'end': {
                'type': int,
                'help': ('R|button that ends the scrolling\n'
                         '[default: --buttons-start]')
            }
        }
    },
    'config': {
        'description': ('Configuration file options\n'
                        'It allows to load arguments on runtime'),
        'parameters': {
            'enable': {
                'default': CONFIG_ENABLE,
                'action': 'store_true',
                'help': ('R|if set, arguments from the configuration file '
                         'on --config-path will be loaded every --config-interval')
            },
            'path': {
                'default': CONFIG_PATH,
                'type': str,
                'help': 'R|path to the configuration file',
            },
            'interval': {
                'default': CONFIG_INTERVAL,
                'type': int,
                'help': ('R|how often the config file should be checked for '
                         'changes, in seconds')
            }
        }
    },
    'icon': {
        'description': ('Scrolling icon options\n'
                        'By default, an icon is displayed when the scrolling is active'),
        'parameters': {
            'disable': {
                'default': ICON_ENABLE,
                'action': 'store_false',
                'dest': 'enable',
                'help': 'R|if set, the icon will be disabled'
            },
            'path': {
                'default': ICON_PATH,
                'type': str,
                'help': 'R|path to the icon'
            },
            'size': {
                'default': ICON_SIZE,
                'type': int,
                'help': 'R|size of the icon, in pixels'
            }
        }
    },
    'debug': {
        'description': 'Debug options',
        'parameters': {
            'click': {
                'default': DEBUG_CLICK,
                'action': 'store_true',
                'help': 'R|if set, click info will be printed to stdout'
            },
            'scroll': {
                'default': DEBUG_SCROLL,
                'action': 'store_true',
                'help': 'R|if set, scroll info will be printed to stdout'
            }
        }
    }
}
