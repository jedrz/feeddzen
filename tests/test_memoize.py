#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.abspath('.'))
import unittest
import time

import feeddzen.utils


class MemoizeTest(unittest.TestCase):

    def setUp(self):
        @feeddzen.utils.memoize(0.1)
        def function():
            return time.time()
        self.function = function

    def test_memoize(self):
        cached_value = self.function()
        for n in range(10):
            self.assertEqual(cached_value, self.function(),
                             "The value should be cached by 10 ms")
            time.sleep(0.01)


if __name__ == '__main__':
    unittest.main()
