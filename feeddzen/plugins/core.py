#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Widget:
    """Simple class to build widget upon it"""

    def __init__(self, timeout, template):
        self.timeout = timeout
        self.template = template

    def __str__(self):
        raise NotImplementedError
