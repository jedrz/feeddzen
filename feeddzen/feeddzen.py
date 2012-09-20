#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import subprocess
import shlex

from feeddzen import utils


class Widget:

    def __init__(self, timeout, template):
        self.timeout = timeout
        self.template = template

    def __str__(self):
        raise NotImplementedError


class StaticWidget:

    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


class Manager:

    def __init__(self, widgets=[], dzen_command='dzen2'):
        self._scheduler = utils.ContScheduler(time.time, time.sleep)
        self.widgets = widgets
        self._init_dzen(dzen_command)
        self._init_events()

    def _init_dzen(self, dzen_command):
        dzen_proc = subprocess.Popen(shlex.split(dzen_command),
                                     stdin=subprocess.PIPE)
        self._dzen_stdin = dzen_proc.stdin

    def _init_events(self):
        for widget in self.widgets:
            if not isinstance(widget, StaticWidget):
                self._scheduler.enter(
                    widget.timeout, 1, self._print_status_bar, ())

    def _print_status_bar(self):
        status_bar = ''.join(str(w) for w in self.widgets) + '\n'
        self._dzen_stdin.write(bytes(status_bar.encode('utf-8')))

    def start(self):
        self._print_status_bar()
        self._scheduler.run()
