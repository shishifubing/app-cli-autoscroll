# Information

Enables autoscroll on linux using xorg-server

Yes, you can use a config file in `/etc/X11/xorg.conf.d/` to achieve the autoscrolling (see [the example](#xorg-server-config-example)), but it does not
work in Firefox, only in Chrome (tested on `Linux 5.16.15-arch1-1 #1 SMP PREEMPT Thu, 17 Mar 2022 00:30:09 +0000`, `Firefox 98.0.1` and `Chrome 96.0.4664.110 (Official Build, ungoogled-chromium)`)

Autoscroll means that once you press "--button_start",
you can scroll just by moving your mouse untill you press "--button_end"

If "--button_hold" is set, the scrolling will end once you release "--button_start"

To find the number of the button you can use xinput (requires xinput package) or set "--show_buttons"

How to use xinput:
    "xinput list" -> find your mouse's name or id -> "xinput test <name or id>"

# Usage

## environment

python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
python linux-autoscroll.start

## command

```
usage: linux-xorg-autoscroll [-h] [--delay DELAY] [--button_start BUTTON_START]
                             [--button_hold | --no-button_hold] [--button_end BUTTON_END]
                             [--dead_area DEAD_AREA] [--icon_path ICON_PATH] [--icon_size ICON_SIZE]
                             [--show_buttons | --no-show_buttons] [--show_movement | --no-show_movement]

Enables autoscroll on linux using xorg-server

Autoscroll means that once you press "--button_start",
you can scroll just by moving your mouse untill you press "--button_end"

If "--button_hold" is set, the scrolling will end once you release "--button_start"

To find the number of the button you can use xinput (requires xinput package) or set "--show_buttons"

How to use xinput:
"xinput list" -> find your mouse's name or id -> "xinput test <name or id>"

options:
  -h, --help            show this help message and exit
  --delay DELAY         sets the speed of scrolling, defaults to 5
  --button_start BUTTON_START
                        the button that starts the scrolling when pressed, defaults to 2 (middle click)
  --button_hold, --no-button_hold
                        if set, button_end is ignored and the scrolling will be active only while
                        button_start is pressed
  --button_end BUTTON_END
                        the button that ends the scrolling when pressed, defaults to 2 (middle click)
  --dead_area DEAD_AREA
                        the size (in px) of the area below and above the starting point where scrolling
                        is paused, defaults to 20
  --icon_path ICON_PATH
                        if specified, the icon on the path will be displayed while the scrolling mode is
                        active, supported formats: svg, png, jpg, jpeg, gif, bmp, pbm, pgm, ppm, xbm,
                        xpm, the path must be absolute, defaults resources/img/icon.svg (relative to the
                        package)
  --icon_size ICON_SIZE
                        the size of the icon in px, only svg images can be resized without loss of
                        quality
  --show_buttons, --no-show_buttons
                        if set, button clicks will be printed to stdout
  --show_movement, --no-show_movement
```

# Examples

## xorg-server config example
```conf
# https://bbs.archlinux.org/viewtopic.php?id=261138
Section "InputClass"
     ### general
     ## id, obtained from "xinput list"
     Identifier "Logitech USB Trackball"
     ## driver, obtained from "xinput list-props <id>"
     Driver "libinput"

     ### options
     ## name
     # Option "Name" "Logitech USB Trackball"
     ## scrolling with the button
     Option "ScrollMethod" "button"
     ## specifies the scroll button
     ## middle click
     Option "ScrollButton" "2"
     ## if 1, instead of scrolling while pressing the button,
     ## it makes the scroll active untill you press the button again
     Option "ScrollButtonLock" "0"
     ## acceleration of scrolling
     Option "AccelSpeed" "0"
     ## maps buttons to each over, button numbers
     ## can be obtained from "xinput list <id>"
     Option "ButtonMapping" "1 0 3 0 0 0 0 2 0"
     ## skips pixels to move faster
     # Option "TransformationMatrix" "2.4 0 0 0 2.4 0 0 0 1"
EndSection
```
