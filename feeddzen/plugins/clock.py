#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from .. import utils
from .core import Widget


class ClockWidget(Widget):
    """Clock widget.

    See `man 3 strftime` for supported delimiters
    """

    def __init__(self, timeout, template):
        super().__init__(timeout, template)
        self._define_update()

    def _define_update(self):
        @utils.memoize(self.timeout)
        def update():
            return time.strftime(self.template, time.localtime())
        self.update = update

    def __str__(self):
        return self.update()
