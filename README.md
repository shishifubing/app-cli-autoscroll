# Information

Enables universal autoscroll.

Pretty pointless since on Linux you can achieve it using config files
(see [the example](#xorg-server-config-example)) and for Windows there are usually drivers.

Supports only mouse buttons.

## Usage
You can pass file contents as arguments using `@path` syntax, every argument in
that case should begin on the new line.

If you want to dynamically pass arguments without restarting the process you can use `--config` options for it.

Once you press `--buttons-start`, you can scroll vertically and horizontally just by moving your mouse untill you press `--buttons-end`.

If `--buttons-hold` is set, the srolling ends once you release `--buttons-start`.

You can change arguments on runtime by enabling a config file, you can do so by setting `--config-enable` and `--config-path`.

By default, an icon is shown once the scrolling starts, you can disable it by setting `--icon-disable`.

Once `--buttons-start` is pressed, the scroll thread starts looping. Every loop consists of sleeping for an interval, then scrolling for either 0, 1, or -1 pixels on both axis towards the starting point.

Starting point is the point where `--buttons-start` was pressed.

Sleep interval is recalculated on every mouse move as such:
```
100 / (--scrolling-acceleration * max(distance) + --scrolling-speed)
```

If `--scrolling-acceleration` is not 0, the speed of scrolling will be faster
the farther away you are from the starting point.

If `--scrolling-acceleration` is 0, the speed of the scrolling will be constant.

### environment

requirements:
```
pynput
pyside6
```
`pyside6` is a `Qt` library, if you would rather avoid downloading it, you can
set `--icon-disable`, in that case icon will not be displayed.

```
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
python -m autoscroll.main
```

### examples

#### start
```
python3 -m autoscroll.main --buttons-start 1 --debug-click --icon-disable
```

#### start with the configuration file passed once

```python
python3 -m autoscroll.main @config.txt
```
If config.txt is defined like this, its contents will be used as command line arguments - they will be loaded only once.
Arguments can be placed wherever - on one line, on several lines.
For example,
```
--buttons-start 1
--buttons-hold --debug_click
```

#### start with the process listening to the changes in the configuration file

```python
python3 -m autoscroll.main --config-enable --config-path config.txt
```
If config.txt is defined like this, the process will listen for changes in that
file and update itself.
Arguments can be placed wherever - on one line, on several lines
It checks the file for changes every `--config-interval`.
For example:
```
--buttons-start 1 --buttons-hold
--debug_click
```

### --help output

```
usage: linux-xorg-autoscroll [-h] [-ss SCROLLING_SPEED] [-sd SCROLLING_DEAD_AREA]
                             [-sa SCROLLING_ACCELERATION] [-bh] [-bs BUTTON_START] [-be BUTTON_END]
                             [-ce] [-cp CONFIG_PATH] [-ci CONFIG_INTERVAL] [-id] [-ip ICON_PATH]
                             [-is ICON_SIZE] [-dc] [-ds]

Enables universal autoscroll.

Pretty pointless since on Linux you can achieve it using config files and for Windows there are usually drivers.

Supports only mouse buttons.

You can pass file contents as arguments using '@path' syntax, every argument in that case should begin on the new line.

If you want to dynamically pass arguments without restarting the process you can use '--config' options for it.

Once you press '--buttons-start', you can scroll vertically or horizontally just by moving your mouse untill you press '--buttons-end'.

If '--buttons-hold' is set, the srolling ends once you release '--buttons-start'.

You can change arguments on runtime by enabling a config file, you can do so by setting '--config-enable' and '--config-path'.

By default, an icon is shown once the scrolling starts, you can disable it by setting '--icon-disable'.

Once '--buttons-start' is pressed, the scroll thread starts looping. Every loop consists of sleeping for an interval, then scrolling for either 0, 1, or -1 pixels on both axis towards the starting point.

Starting point is the point where '--buttons-start' was pressed.

Sleep interval is recalculated on every mouse move as such:

    100 / ('--scrolling-acceleration' * max(distance) + '--scrolling-speed')

If '--scrolling-acceleration' is not 0, the speed of scrolling will be faster

the farther away you are from the starting point.

If '--scrolling-acceleration' is 0, the speed of the scrolling will be constant.

options:
  -h, --help            show this help message and exit

scrolling options:

  -ss, --scrolling-speed int
                        constant part of the scrolling speed
                        [default: 300]
  -sd, --scrolling-dead-area int
                        size of the square area aroung the starting point where scrolling will stop, in
                        pixels
                        [default: 50]
  -sa, --scrolling-acceleration int
                        dynamic part of the scrolling speed, depends on the distance from the point
                        where the scrolling started, can be set to 0
                        [default: 10]

button options:

  -bh, --button-hold    if set, the scrolling will end once you release --buttons-start
  -bs, --button-start int
                        button that starts the scrolling
                        [default: 2]
  -be, --button-end int
                        button that ends the scrolling
                        [default: --buttons-start]

config options:

  -ce, --config-enable  if set, arguments from the configuration file on --config-path will be loaded
                        every --config-interval
  -cp, --config-path str
                        path to the configuration file
                        [default: /home/kongrentian/.config/autoscroll/config.txt]
  -ci, --config-interval int
                        how often the config file should be checked for changes, in seconds
                        [default: 5]

icon options:

  -id, --icon-disable   if set, the icon will be disabled
  -ip, --icon-path str  path to the icon
                        [default: resources/img/icon.svg]
  -is, --icon-size int  size of the icon, in pixels
                        [default: 30]

debug options:

  -dc, --debug-click    if set, click info will be printed to stdout
  -ds, --debug-scroll   if set, scroll info will be printed to stdout
```


## xorg-server config example

```conf
# https://wiki.archlinux.org/title/Logitech_Marble_Mouse#Configuration_file
# https://help.ubuntu.com/community/Logitech_Marblemouse_USB
# https://bbs.archlinux.org/viewtopic.php?id=261138
# path - /etc/X11/xorg.conf.d/40-trackball.conf
Section "InputClass"
  Identifier   "Marble Mouse"
  MatchProduct "Logitech USB Trackball"
  Driver       "libinput"
  Option       "ScrollMethod"     "button"
  Option       "ScrollButton"     "1"
  Option       "MiddleEmulation"  "true"
  Option       "ButtonMapping"    "3 2 1 4 5 6 7 9 8"
  Option       "NaturalScrolling" "true"
EndSection
```
