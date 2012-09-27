#!/usr/bin/env python
# -*- coding: utf-8 -*-


class StaticWidget:
    """Static widget to just print passed string"""

    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text
