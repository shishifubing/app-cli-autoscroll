from importlib.resources import path as importlib_path
from typing import Any, Union
from pynput.mouse import Button
from argparse import ArgumentParser, Namespace
from .constants import ARGUMENTS
from argparse import RawDescriptionHelpFormatter


def parse_arguments() -> Namespace:
    parser = ArgumentParser(
        prog='linux-xorg-autoscroll',
        formatter_class=RawDescriptionHelpFormatter,
        description=get_resource_content('resources/txt/description.txt'))
    for argument in ARGUMENTS:
        parser.add_argument(argument[0], **argument[1])
    return parser.parse_args()


def print_mouse_action(
        do_print: bool,
        x: int,
        y: int,
        button: Button = None,
        pressed: bool = None,
        button_hold: bool = None,
        scroll_mode: bool = None,
        button_start: bool = None,
        button_end: bool = None) -> None:
    if not do_print:
        return
    result = [f'[{x}, {y}]']
    if button is not None and pressed is not None:
        result.append(
            f'{button}({button.value}) was {"pressed" if pressed else "released"}')
    if button_hold is not None and scroll_mode is not None:
        result.append(
            f'button_hold is {button_hold}, scroll_mode is {scroll_mode}')
    if button_start is not None and button_end is not None:
        result.append(f'is_start is {button_start}, is_end is {button_end}')
    print(', '.join(result))


def get_resource_path(resource: str = None) -> str:
    if resource is None:
        file = ''
        addition = ''
    else:
        split = resource.split('/')
        addition = '.'.join(split[0:-1])
        addition = f'.{addition}' if addition else ''
        file = split[-1]
        file = file if file != addition else ''
    return str(importlib_path(f'linux-xorg-autoscroll{addition}', file))


def get_resource_content(resource: str) -> str:
    with open(get_resource_path(resource), 'r') as file:
        return file.read()


def convert_button(
        value: Union[None, int, str, Button], default: int) -> Button:
    if isinstance(value, Button):
        return value
    return Button(convert(value, int, default))


def convert(
        value: Union[None, str, Any], target_type: Any, default: Any) -> Any:
    if value is None:
        return default
    if isinstance(type(value), type(target_type)):
        return value
    if isinstance(value, str):
        return target_type(value)
    message = f'value "{str(value)}"({str(type(value))})'
    message = f'{message} is not {type(None)}, {str} or {str(target_type)}'
    raise TypeError(message)
