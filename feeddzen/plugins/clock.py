#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from feeddzen import feeddzen
from feeddzen import utils


class ClockWidget(feeddzen.Widget):

    def __init__(self, format, timeout):
        super().__init__(format, timeout)
        self.define_update()

    def define_update(self):
        @utils.memoize(self.timeout)
        def update():
            return time.strftime(self.format, time.localtime())
        self.update = update

    def __str__(self):
        return self.update()
