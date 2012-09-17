#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Widget:

    def __init__(self, timeout, template):
        self.timeout = timeout
        self.template = template

    def __str__(self):
        raise NotImplementedError


class StaticWidget:

    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


class FeedDzen:

    def __init__(self, plugins=[]):
        self.plugins = plugins

    def __call__(self):
        for plugin in plugins:
            print(plugin)
