from argparse import ArgumentParser
from threading import Event
from time import sleep
from pynput.mouse import Button, Controller, Listener
from .constants import (
    ARGUMENTS,
    BUTTONS_HOLD,
    BUTTONS_START,
    CONFIG_ENABLE,
    CONFIG_ERROR_ENABLE,
    CONFIG_ERROR_PARSE,
    CONFIG_LISTEN,
    CONFIG_PATH,
    CONFIG_SLEEP,
    COORDINATE_NAME,
    DEBUG_ARGUMENTS,
    DEBUG_CLICK,
    DEBUG_PADDING,
    DEBUG_SCROLL,
    ICON_ENABLE,
    ICON_ERROR,
    ICON_PATH,
    ICON_SIZE,
    PARSER_INITIALIZER,
    SCROLLING_ACCELERATION_DISTANCE,
    SCROLLING_DEAD_AREA,
    SCROLLING_SLEEP_INTERVAL_INITIAL,
    SCROLLING_AUTOSCROLL,
    SCROLLING_SPEED)
from .functions import check_iterable, construct_coordinates, has_dict, parse_arguments, raise_type_error, return_none
from typing import Any, Callable, Dict, Iterable, List, Tuple, Type, Union
from threading import Event, Thread
from os import stat as os_stat


class Base:

    repr_keys_ignore = []
    repr_keys_only = []

    def update(self, *args, **kwargs) -> None: ...

    def json(self) -> Dict[str, Any]: ...

    def __init__(self, *args, **kwargs) -> None: self.update(*args, **kwargs)

    def _repr_key_is_valid(self, name: str) -> bool:
        if self.repr_keys_only:
            return name in self.repr_keys_only
        return name not in self.repr_keys_ignore

    def __repr__(self) -> str:
        name = self.name if hasattr(self, 'name') else type(self).__name__
        raise_type_error(name, str)
        debug = {key: str(value)
                 for key, value in self.json().items()
                 if self._repr_key_is_valid(key)}
        return self._construct_debug(name.capitalize(), **debug)

    def __str__(self) -> str: return self.__repr__()

    def _set_if_nonexistent(self, name: str, value: Any) -> None:
        return None if hasattr(self, name) else setattr(self, name, value)

    def _construct_debug(self, _header: str, *args, **kwargs) -> str:
        result = ', '.join([item for item in args] +
                           [f'{name} - {value}'
                           for name, value in kwargs.items()])
        return _header.ljust(DEBUG_PADDING, ' ') + result

    @staticmethod
    def _convert_callable(value: Any) -> Any: return value

    def _set(self, _name: str, _nonexistent_value: Any, _value: Any,
             _type: Any = type(None), _callable: Callable = _convert_callable,
             **kwargs) -> None:
        self._set_if_nonexistent(_name, _nonexistent_value)
        setattr(self, _name, self._convert(_value, getattr(self, _name), _type,
                                           _callable, **kwargs))

    def _convert(self, _value: Any, none_value: Any = None,
                 _type: Any = type(None),
                 _callable: Callable = _convert_callable, **kwargs) -> Any:
        """
        converts

        value is None: default

        target_type is None or value is target_type: value

        value is convert_type and convert function is callable:
            convert_function(value)

        raise_type_error
        """
        if isinstance(_value, _type) and callable(_callable):
            return _callable(_value, **kwargs)
        if _value is None:
            return none_value
        if isinstance(_value, _type):
            raise ValueError(f'value "{_value}" is "{_type}", but the '
                             'conversion function is not callable')
        return raise_type_error(_value, (type(None), _type))

    def _loop(self, condition: Callable = return_none,
              action: Callable = return_none,
              condition_parameters: Dict[str, Any] = {},
              action_parameters: Dict[str, Any] = {}) -> None:
        if not (callable(condition) and callable(action)):
            raise TypeError(f'either \'{str(condition)}\' or '
                            f'\'{str(action)}\' is not callable')
        if not has_dict(condition_parameters, action_parameters):
            raise TypeError('parameters should have \'__dict__\' attribute')
        while condition(**condition_parameters):
            action(**action_parameters)

    def _print(self, header: str, do_print: bool = True) -> str:
        result = f'\n[{header}]\n{self}'
        if do_print:
            print(result)
        return result


class Coordinate(Base):

    def update(self, current: Union[int, str] = None,
               previous: Union[int, str] = None,
               initial: Union[int, str] = None) -> None:
        self.initial: int = initial
        self.previous: int = previous
        self.current: int = current

    def distance(self, absolute: bool = False) -> int:
        distance = self.initial - self.current
        return abs(distance) if absolute else distance

    def direction(self) -> int:
        # direction > 0 -> 1, direction == 0 -> 0, direction < 0 -> -1
        return (self.distance() == 0) + (1 if self.distance() > 0 else -1)

    @property
    def current(self) -> int: return self._current

    @property
    def previous(self) -> int: return self._previous

    @property
    def initial(self) -> int: return self._initial

    @current.setter
    def current(self, value: int) -> None:
        _current = getattr(self, '_current', None)
        self._set('_current', 0, value, (str, int), int)
        self._set('_previous', 0, _current, (str, int), int)

    @previous.setter
    def previous(self, value: int) -> None:
        self._set('_previous', 0, value, (str, int), int)

    @initial.setter
    def initial(self, value: int) -> None:
        self._set('_initial', 0, value, (str, int), int)

    def json(self) -> Dict[str, Any]:
        return {'current': self.current, 'previous': self.previous,
                'initial': self.initial}


class Coordinates(Base):

    def update(self, x: Union[Coordinate, str, int] = None,
               y: Union[Coordinate, str, int] = None,
               name: str = None) -> None:
        self.x: Coordinate = x
        self.y: Coordinate = y
        self.name: str = self._convert(name, COORDINATE_NAME, str)

    def direction(self) -> Tuple[int, int]:
        return (self.x.direction(), self.y.direction())

    def distance(self, absolute: bool = False) -> Tuple[int, int]:
        return (self.x.distance(absolute), self.y.distance(absolute))

    @property
    def x(self) -> Coordinate: return self._x

    @property
    def y(self) -> Coordinate: return self._y

    @property
    def current(self) -> Tuple[int, int]:
        return (self.x.current, self.y.current)

    @property
    def initial(self) -> Tuple[int, int]:
        return (self.x.initial, self.y.initial)

    @property
    def previous(self) -> Tuple[int, int]:
        return (self.x.previous, self.y.previous)

    @y.setter
    def y(self, value: Union[str, int, Coordinate]) -> None:
        self._set('_y', Coordinate(), value, (Coordinate, str, int),
                  self._convert_coordinate, name='_y')

    @x.setter
    def x(self, value: Union[str, int, Coordinate]) -> None:
        self._set('_x', Coordinate(), value, (Coordinate, str, int),
                  self._convert_coordinate, name='_x')

    @current.setter
    def current(self, value: Tuple[Union[str, int], Union[str, int]]) -> None:
        self.x.current, self.y.current = self._convert(
            value, (None, None), Iterable, self._convert_iterable)

    @initial.setter
    def initial(self, value: Tuple[Union[str, int], Union[str, int]]) -> None:
        self.x.initial, self.y.initial = self._convert(
            value, (None, None), Iterable, self._convert_iterable)

    @previous.setter
    def previous(self, value: Tuple[Union[str, int], Union[str, int]]) -> None:
        self.x.previous, self.y.previous = self._convert(
            value, (None, None), Iterable, self._convert_iterable)

    def _convert_coordinate(self, value: Union[Coordinate, int],
                            name: str) -> Coordinate:
        if isinstance(value, (int, str)):
            coordinate = getattr(self, name)
            setattr(coordinate, 'current', int(value))
            return coordinate
        return raise_type_error(value, Coordinate)

    def _convert_iterable(self, value: Any) -> Tuple[int, int]:
        raise_type_error(value, Iterable)
        x, y = None, None
        if len(value) >= 1:
            x = self._convert(value[0], None, (str, int), int)
        if len(value) >= 2:
            y = self._convert(value[1], None, (str, int), int)
        return x, y

    def json(self) -> Dict[str, Any]:
        coordinates = {'direction': str(self.direction()),
                       'distance': str(self.distance())}
        coordinates.update({item: construct_coordinates(getattr(self.x, item),
                                                        getattr(self.y, item))
                            for item in ('current', 'previous', 'initial')})
        return coordinates


class Buttons(Base):

    def __init__(self, *args, **kwargs) -> None:
        self.update(*args, **kwargs)

        self.button: Button = None
        self.is_pressed: bool = None

    def update(self, start: Union[Button, int, str] = None,
               end: Union[Button, int, str] = None,
               hold: Union[bool, str] = None) -> None:
        self.start: Button = start
        self.end: Button = end
        self.hold: bool = hold

    def press(self, button: Button, pressed: bool) -> None:
        self.button, self.is_pressed = button, pressed

    def press_clear(self) -> None: self.button, self.is_pressed = None, None

    def is_start(self, button: Button = None) -> bool:
        return self.start == button

    def is_end(self, button: Button = None) -> bool: return self.end == button

    @property
    def start(self) -> Button: return self._start

    @property
    def hold(self) -> bool: return self._hold

    @property
    def end(self) -> Button: return self._end

    @start.setter
    def start(self, value: Union[int, str, Button] = None) -> None:
        self._set('_start', Button(BUTTONS_START), value, (int, Button, str),
                  self._convert_button)

    @end.setter
    def end(self, value: Union[int, str, Button] = None) -> None:
        self._set('_end', self.start, value, (int, Button, str),
                  self._convert_button)

    @hold.setter
    def hold(self, value: Union[str, bool] = None) -> None:
        self._set('_hold', BUTTONS_HOLD, value, (str, bool), bool)

    @staticmethod
    def _convert_button(value: Union[Button, int, str]) -> Button:
        return value if isinstance(value, Button) else Button(int(value))

    def json(self) -> Dict[str, Any]:
        return {'start': self.start.name, 'end': self.end.name,
                'hold': self.hold, 'pressed button': self.button,
                'pressed': self.is_pressed}


class Scrolling(Base):

    def __init__(self, *args, **kwargs) -> None:
        self.sleep_interval: int = SCROLLING_SLEEP_INTERVAL_INITIAL
        self.controller: Controller = Controller()
        self.event_scrolling: Event = Event()
        self.event_scrolling_started: Event = Event()
        self.event_scrolling_ended: Event = Event()

        self.coordinates: Coordinates = Coordinates()
        self.coordinates.repr_keys_ignore = ['direction']
        self.direction: Coordinates = Coordinates(name='direction')
        self.direction.repr_keys_only = ['direction']

        self.update(*args, **kwargs)

    def update(self, dead_area: Union[str, int] = None,
               speed: Union[str, int] = None,
               acceleration: Union[str, int] = None,
               autoscroll: Union[bool, str] = None) -> None:
        self.speed: int = speed
        self.dead_area: int = dead_area
        self.acceleration: int = acceleration
        self.autoscroll: bool = autoscroll

    def start(self) -> None:
        self.event_scrolling.set()
        self.event_scrolling_started.set()

    def stop(self) -> None:
        self.event_scrolling.clear()
        self.event_scrolling_ended.set()

    def stop_started_and_ended(self) -> None:
        self.event_scrolling_ended.clear()
        self.event_scrolling_started.clear()

    def is_scrolling(self) -> bool: return self.event_scrolling.is_set()

    def has_started(self) -> bool: return self.event_scrolling_started.is_set()

    def has_ended(self) -> bool: return self.event_scrolling_ended.is_set()

    def scroll(self, print_debug: bool = False) -> None:
        # wait for the scrolling event to be set in self._on_click
        self.event_scrolling.wait()
        # wait for a period of time, calculated in self._on_move
        sleep(self.sleep_interval)
        # scroll on x-axis and y-axis, each scroll is either 1px, 0px, or -1px
        self.controller.scroll(*self.direction.current)
        if self.autoscroll:
            self.controller.move(*self.coordinates.initial)
        # debug
        self._print('scroll', print_debug)

    def is_dead_area(self) -> bool:
        if not self.autoscroll:
            return False
        distance = self.coordinates.distance(absolute=True)
        return distance[0] <= self.dead_area and distance[1] <= self.dead_area

    def set_direction_and_coordinates(self, x: int, y: int) -> None:
        self.coordinates.update(x, y)
        self.direction.current = ((0, 0) if self.is_dead_area()
                                  else self.coordinates.direction())

    def json(self) -> str:
        return {'is_scrolling': self.is_scrolling(),
                'interval': self.sleep_interval,
                'acceleration': self.acceleration,
                'dead_area': self.dead_area,
                'scrolling started': self.event_scrolling_started.is_set(),
                'scrolling ended': self.event_scrolling_ended.is_set(),
                'autoscroll': self.autoscroll}

    @property
    def speed(self) -> int: return self._speed

    @property
    def dead_area(self) -> int: return self._dead_area

    @property
    def acceleration(self) -> int: return self._acceleration

    @property
    def autoscroll(self) -> bool: return self._autoscroll

    @autoscroll.setter
    def autoscroll(self, value: Union[str, bool]) -> None:
        self._set('_autoscroll', SCROLLING_AUTOSCROLL,
                  value, (str, bool), bool)

    @speed.setter
    def speed(self, value: Union[str, int] = None) -> None:
        self._set('_speed', SCROLLING_SPEED, value, (str, int), int)

    @dead_area.setter
    def dead_area(self, value: Union[str, int]) -> None:
        self._set('_dead_area', SCROLLING_DEAD_AREA, value, (str, int), int)

    @acceleration.setter
    def acceleration(self, value: Union[str, int]) -> None:
        self._set('_acceleration', SCROLLING_ACCELERATION_DISTANCE, value,
                  (str, int), int)


class Icon(Base):

    def update(self, enable: Union[str, bool] = None,
               path: str = None, size: Union[str, int] = None) -> None:
        self.path: str = path
        self.size: int = size
        self.enable: bool = True if self.path or self.size else enable
        self.icon: Union[None, object] = self.path, self.size

    def show(self, x: int, y: int) -> None:
        return self.icon.show(x, y) if self.enable else None

    def close(self) -> None: return self.icon.close() if self.enable else None

    def json(self) -> Dict[str, Any]:
        return {'enable': self.enable, 'path': self.path, 'size': self.size}

    @property
    def path(self) -> str: return self._path

    @property
    def size(self) -> int: return self._size

    @property
    def enable(self) -> bool: return self._enable

    @property
    def icon(self) -> Union[None, Any]: return self._icon

    @path.setter
    def path(self, value: str) -> None:
        self._set('_path', ICON_PATH, value, str)

    @size.setter
    def size(self, value: Union[str, int]) -> None:
        self._set('_size', ICON_SIZE, value, (str, int), int)

    @enable.setter
    def enable(self, value: Union[str, bool]) -> None:
        self._set('_enable', ICON_ENABLE, value, (str, bool), bool)

    @icon.setter
    def icon(self, value: Tuple[str, int]) -> None:
        if not self.enable:
            self._icon = None
            return
        try:
            from .qt5_stuff import Icon as qt_icon
        except ImportError as exception:
            raise ValueError(ICON_ERROR) from exception

        self._icon = qt_icon(*check_iterable(value))


class Debug(Base):

    def update(self, scroll: bool = None,
               click: bool = None, arguments: bool = None) -> None:
        self.scroll: bool = scroll
        self.click: bool = click
        self.arguments: bool = arguments

    def json(self) -> Dict[str, Any]:
        return {'scroll': self.scroll, 'click': self.click,
                'arguments': self.arguments}

    @property
    def scroll(self) -> bool: return self._scroll

    @property
    def click(self) -> bool: return self._click

    @property
    def arguments(self) -> bool: return self._arguments

    @scroll.setter
    def scroll(self, value: bool) -> None:
        self._set('_scroll', DEBUG_SCROLL, value, (str, bool), bool)

    @click.setter
    def click(self, value: bool) -> None:
        self._set('_click', DEBUG_CLICK, value, (str, bool), bool)

    @arguments.setter
    def arguments(self, value: bool) -> None:
        self._set('_arguments', DEBUG_ARGUMENTS, value, (str, bool), bool)


class Config(Base):

    def __init__(self, *args, **kwargs) -> None:
        self.event_end: Event = Event()
        self.stamp: int = 0
        self.argument_parser: ArgumentParser = ArgumentParser(
            **PARSER_INITIALIZER)
        for argument in ARGUMENTS:
            self.argument_parser.add_argument(*argument[0], **argument[1])

        self.update(*args, **kwargs)

    def update(self, enable: bool = None, path: str = None,
               listen: bool = None) -> None:
        self.path: str = path
        self.listen: bool = listen
        self.enable: bool = enable

    def parse_argv(self) -> Dict[str, Any]: return self._parse()

    def parse_string(self, value: str) -> Dict[str, Any]:
        return self._parse(value.split())

    def parse_config_file(self) -> Dict[str, Any]:
        if not self.enable:
            raise AttributeError(CONFIG_ERROR_PARSE)
        with open(self.path, 'r') as config_file:
            config = config_file.read()
        return self.parse_string(config.replace('\n', ' '))

    def _parse(self, *args, **kwargs) -> Dict[str, Any]:
        return parse_arguments(
            vars(self.argument_parser.parse_args(*args, **kwargs)))

    def _check(self) -> None:
        if not self._file_changed():
            return

    def _file_changed(self) -> bool:
        stamp = os_stat(self.path).st_mtime
        if stamp == self.stamp:
            return False
        self.stamp = stamp
        return True

    @ property
    def listen(self) -> bool: return self._listen

    @ property
    def enable(self) -> bool: return self._enable

    @ property
    def path(self) -> str: return self._path

    @property
    def sleep(self) -> int: return self._sleep

    @ listen.setter
    def listen(self, value: Union[bool, str]) -> None:
        self._set('_listen', CONFIG_LISTEN, value, (bool, str))

    @ enable.setter
    def enable(self, value: Union[bool, str]) -> None:
        self._set('_enable', CONFIG_ENABLE, value, (bool, str), bool)
        if self.enable and not self.path:
            self._enable = False
            raise ValueError(f'{CONFIG_ERROR_ENABLE}, path - {self.path}')

    @ path.setter
    def path(self, value: str) -> None:
        self._set('_path', CONFIG_PATH, value, str)

    @sleep.setter
    def sleep(self, value: Union[str, int]) -> None:
        self._set('_sleep', CONFIG_SLEEP, value, (int, str), int)

    def json(self) -> Dict[str, Any]:
        return {'path': self.path, 'listen': self.listen,
                'enable': self.enable}
