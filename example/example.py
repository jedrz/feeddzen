#!/usr/bin/env python
# -*- coding: utf-8 -*-

import locale
import os
import time

# If you would like to test this script without installing,
# then uncomment below two lines and run it from directory where
# setup.py file and feeddzen directory is located.

#import sys
#sys.path.insert(0, os.path.abspath('.'))

from feeddzen.manager import Manager
from feeddzen.plugins import *    # Import all plugins


# Set preferred locale.
#locale.setlocale(locale.LC_TIME, ('pl_PL', 'UTF-8'))

# Create widgets.
# separator
sep = core.StaticWidget(' << ')

# clock widget
def clock_f():
    return time.strftime('%a, %d %b %Y, %H:%M:%S')
clock_w = core.Widget(60,      # timeout
                      clock_f) # function which result should be send to dzen

# alsa widget
def vol_f(volume, muted):
    state = 'off' if muted else 'on'
    return 'Vol: {}% [{}]'.format(volume, state)
vol_w = volume.AlsaWidget(40, vol_f)

# battery widget
def bat_f(state, d):
    if state == 'charging':
        return 'BAT: {percentage}% [{hours}:{minutes}:{seconds}]'.format(**d)
    elif state == 'discharging':
        return '^fg(#fff)BAT: {percentage}% [{hours}:{minutes}:{seconds}]^fg()'.format(**d)
    else:
        return 'BAT: {percentage}%'.format(**d)
bat_w = battery.BatteryWidget(61, bat_f)

# load widget
def load_f():
    load = os.getloadavg()
    load1 = load[0]
    load5 = load[1]
    load15 = load[2]
    return 'Load: {} {} {}'.format(load1, load5, load15)
load_w = core.Widget(97, load_f)

# mpd widget
#def mpd_f(playing, d):
#    if playing:
#        return 'MPD: {artist} - {title}'.format(**d)
#    else:
#        return 'MPD: stop'
#mpd_w = mpd.MPDWidgetMPC(35, mpd_f)

# Create a list of widgets.
# The first item will placed at left side.
widgets = [
    load_w, sep,
    #mpd_w, sep,
    bat_w, sep,
    vol_w, sep,
    clock_w
]

# Your dzen2 command
dzen_command = 'dzen2'

# Create manager and run dzen
manager = Manager(widgets, dzen_command)
manager.start()
