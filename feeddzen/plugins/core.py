#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .. import utils


class BaseWidget:
    """Simple class to build widget upon it"""

    def __init__(self, timeout, func):
        self.timeout = timeout
        self.func = func

    def __str__(self):
        raise NotImplementedError


class StaticWidget:
    """Static widget to just print passed string"""

    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


class Widget(BaseWidget):
    """Widget which call `func` without any arguments.

    Also `func` value is cached for `timeout` seconds.

    Example usage - clock widget - it doesn't need any input.

    import time
    def clock_func():
        return time.strftime('%a, %d %b %Y, %H:%M')
    # Cache returned value every 60 seconds.
    clock_widget = SimpleWidget(60, clock_func)
    # That's all.
    """

    def __init__(self, timeout, func):
        super().__init__(timeout, func)
        self._define_update()

    def _define_update(self):
        @utils.memoize(self.timeout)
        def update():
            return self.func()
        self.update = update

    def __str__(self):
        return self.update()
