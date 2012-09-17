#!/usr/bin/env python
# -*- coding: utf-8 -*-

import functools
import time
import sched
import heapq
from collections import namedtuple


class memoize:
    """Decorator to cache returned value by a function
    for `timeout` seconds.
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

    def __init__(self, timeout):
        self._timeout = timeout
        self._memo = (None, None)

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwds):
            # cache the returned value if
            # cache doesn't exist or cache expires
            if not self._memo[1] or \
                    time.time() - self._memo[1] > self._timeout:
                self._memo = (func(*args, **kwds), time.time())
            return self._memo[0]
        return wrapper


class EventWithDelay(
        namedtuple('Event', 'time, delay, priority, action, argument'),
        sched.Event):
    pass


class CronLikeScheduler(sched.scheduler):

    def _enterabs(self, time, delay, priority, action, argument):
        """Enter a new event in the queue at the absolute time.

        `delay` argument should be equal time - timefunc()

        Returns an ID for the event which can be used to remove it,
        if necessary.
        """
        event = EventWithDelay(time, delay, priority, action, argument)
        heapq.heappush(self._queue, event)
        return event # The ID

    def enterabs(self, time, priority, action, argument):
        """Enter a new event in the queue at an absolute time.

        Returns an ID for the event which can be used to remove it,
        if necessary.
        """
        return self._enterabs(time, time - self.timefunc(),
                              priority, action, argument)

    def enter(self, delay, priority, action, argument):
        """A variant that specifies the time as a relative time.

        This is actually the more commonly used interface.
        """
        time = self.timefunc() + delay
        return self._enterabs(time, delay, priority, action, argument)

    def run(self):
        """Execute the first event in the queue and add it again.

        When there is a positive delay until the first event, the
        delay function is called and the event is left in the queue;
        otherwise, the event is removed from the queue and executed
        (its action function is called, passing it the argument).
        Then the event is added again to the queue. If
        the delay function returns prematurely, it is simply
        restarted.
        """
        # localize variable access to minimize overhead
        # and to improve thread safety
        q = self._queue
        delayfunc = self.delayfunc
        timefunc = self.timefunc
        pop = heapq.heappop
        push = heapq.heappush
        while q:
            time, delay, priority, action, argument = checked_event = q[0]
            now = timefunc()
            if now < time:
                delayfunc(time - now)
            else:
                event = pop(q)
                # Verify that the event was not removed or altered
                # by another thread after we last looked at q[0].
                if event is checked_event:
                    action(*argument)
                    delayfunc(0)   # Let other threads run
                    # add the event again
                    self.enter(delay, priority, action, argument)
                else:
                    heapq.heappush(q, event)
