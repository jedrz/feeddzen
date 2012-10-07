#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .. import utils


class BaseWidget:
    """Simple class to build widgets upon it.

    .. tip::
       Have a look at `Widget` class for the simplest example.

    :param timeout: a number of seconds for storing the same result of `func`
    :param func: a function which result should be sent to dzen
    """

    def __init__(self, timeout, func):
        self.timeout = timeout
        self.func = func

    def __str__(self):
        raise NotImplementedError


class StaticWidget:
    """Static widget to just print passed string.

    :param text: text to print
    """

    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


class Widget(BaseWidget):
    """Widget which call `func` without any arguments.

    The result returned by `func` is cached for `timeout` seconds.

    Example usage - clock widget - it doesn't need any input.
    ::

        import time
        def clock_func():
            return time.strftime('%a, %d %b %Y, %H:%M')
        # Cache returned value every 60 seconds.
        clock_widget = Widget(60, clock_func)
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
