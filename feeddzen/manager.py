#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import subprocess
import shlex

from . import utils
from .plugins.core import StaticWidget


class Manager:
    """Manager for plugins and dzen process.

    :param widgets: a list of widgets to display in dzen
    :param dzen_command: a command to invoke dzen
    """

    def __init__(self, widgets=[], dzen_command='dzen2'):
        self._scheduler = utils.ContScheduler(time.time, time.sleep)
        self.widgets = widgets
        self._init_dzen(dzen_command)
        self._init_events()

    def _init_dzen(self, dzen_command):
        """Create dzen process and set up its standard input."""
        dzen_proc = subprocess.Popen(shlex.split(dzen_command),
                                     stdin=subprocess.PIPE)
        self._dzen_stdin = dzen_proc.stdin

    def _init_events(self):
        """Add events to the scheduler.

        Basically only one event is added several times with different
        timeout.

        If timeout is reached it means particular widget should
        be updated and new data send to dzen. But this requires also
        to print all widgets, whose output is already cached, to get
        complete line for dzen.
        """
        for widget in self.widgets:
            # `StaticWidget`s don't need to be updated.
            if not isinstance(widget, StaticWidget):
                self._scheduler.enter(
                    widget.timeout, 1, self._print_status_bar, ())

    def _print_status_bar(self):
        """Send all widgets' output to dzen's stdin."""
        status_bar = ''.join(str(w) for w in self.widgets) + '\n'
        self._dzen_stdin.write(bytes(status_bar.encode('utf-8')))

    def start(self):
        """Run scheduler and start sending data to dzen."""
        self._print_status_bar()
        self._scheduler.run()
