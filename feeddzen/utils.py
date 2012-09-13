#!/usr/bin/env python
# -*- coding: utf-8 -*-

import functools
import time


class memoize:
    """Decorator to cache returned value by a function
    for `interval` seconds.
    Functions' arguments are not taken into consideration.

    Example:
    >>> import time
    >>> @memoize(1)
    ... def func(arg):
    ...     return arg
    >>> print(func(1))
    1
    >>> time.sleep(0.9)
    >>> print(func(2)) # should print 1
    1
    >>> time.sleep(0.2)
    >>> print(func(3)) # should print 3
    3
    """

    def __init__(self, interval):
        self._interval = interval
        self._memo = (None, None)

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwds):
            # cache the returned value if
            # cache doesn't exist or cache expires
            if not self._memo[1] or \
                    time.time() - self._memo[1] > self._interval:
                self._memo = (func(*args, **kwds), time.time())
            return self._memo[0]
        return wrapper
