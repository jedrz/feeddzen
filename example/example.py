#!/usr/bin/env python
# -*- coding: utf-8 -*-

import locale

from feeddzen.manager import Manager
from feeddzen.plugins import *    # Import all plugins


# Set preferred locale.
#locale.setlocale(locale.LC_TIME, ('pl_PL', 'UTF-8'))

# Create widgets.
# separator
sep = StaticWidget(' << ')
# clock widget
clock_w = ClockWidget(
    60,    # timeout
    # Preferred template. To see supported characters see `man 3 strftime`.
    # Obviously you can also use dzen2' commands such as ^fg(), ^i, etc.
    '^fg(#fff)%a, %d %b %Y, %H:%M:%S^fg()')
# alsa widget
volume_w = AlsaWidget(
    55,
    '^fg(#fff)Vol: {volume} [{state}]^fg()',    # Channel isn't muted
    '^fg(#fff)Vol: 0%^fg()')                    # Channel is muted
# battery widget
bat_w = BatteryWidget(43,
                      # Battery is not charging nor discharging.
                      'BAT: {percentage}',
                      # Battery is discharging.
                      'DCH: ^fg(#f99){percentage}^fg() [{hours}:{minutes}:{seconds}]',
                      # Battery is charging, I want to know when it will
                      # be fully charged.
                      'CHR: {percentage} [{hour_et}:{minute_et}]')
# load widget
load_w = LoadWidget(5 * 60, 'Load: {load5} {load15}')
# mpd widget
# mpd_w = MPDWidgetMPC(30,
#                      'MPD: %artist% - %title%',
#                      'MPD: stop')

# Create a list of widgets.
# The first item will placed at left side.
widgets = [
    load_w, sep,
    # mpd_w, sep,
    bat_w, sep,
    volume_w, sep,
    clock_w
]

# Your dzen2 command
dzen_command = 'dzen2'

# Create manager and run dzen
manager = Manager(widgets, dzen_command)
manager.start()
