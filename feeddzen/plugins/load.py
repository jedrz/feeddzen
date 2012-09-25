#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from .. import utils
from .core import Widget


class LoadWidget(Widget):
    """Average load widget.

    Available special delimeters:
    - `{load}` - average load over the last 1, 5, 15 minutes
    - `{load1}` - average load over the last 1 minute
    - `{load5}` - 5 minutes
    - `{load15}` - 15 minutes
    """

    def __init__(self, timeout, template):
        super().__init__(timeout, template)
        self._define_update()

    def _define_update(self):
        @utils.memoize(self.timeout)
        def update():
            load = os.getloadavg()
            return self.template.format(load=' '.join(str(i) for i in load),
                                        load1=load[0],
                                        load5=load[1],
                                        load15=load[2])
        self.update = update

    def __str__(self):
        return self.update()
