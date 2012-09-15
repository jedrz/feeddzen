#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from feeddzen import feeddzen, utils


class ClockWidget(feeddzen.Widget):
    """A clock widget"""

    def __init__(self, _format, timeout):
        """Arguments:
        - `_format` - see `man 3 strftime` for supported special characters
        """
        super().__init__(_format, timeout)
        self.define_update()

    def define_update(self):
        @utils.memoize(self.timeout)
        def update():
            return time.strftime(self.format, time.localtime())
        self.update = update

    def __str__(self):
        return self.update()
