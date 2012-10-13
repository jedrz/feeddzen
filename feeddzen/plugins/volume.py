#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import subprocess
import shlex

from .. import utils
from .core import BaseWidget


class AlsaWidget(BaseWidget):
    """Volume widget to use with alsa.

    *amixer* command is used to get some information.

    Arguments which will be passed to function:

    1. volume - *integer*, current volume as percentage value,
    2. state - `True` if mixer is muted `False` otherwise.

    :param mixer: name of the mixer, by default `'Master'`.
    :param card: card number, by default 0.
    :param device: device id, by default `'default'`.
    """

    _rx_volume = re.compile(r'(\d{1,3})%')
    _rx_muted = re.compile(r'\[off\]')

    def __init__(self, timeout, func,
                 mixer='Master', card='0', device='default'):
        super().__init__(timeout, func)
        # Build amixer command.
        amixer_command_format = 'amixer get {mixer} -c {card} -D {device}'
        self._amixer_command = shlex.split(amixer_command_format.format(
            mixer=mixer, card=card, device=device))
        self._define_update()

    def _define_update(self):
        @utils.memoize(self.timeout)
        def update():
            output_bytes = subprocess.check_output(self._amixer_command)
            output = output_bytes.decode('utf-8')
            volume = self._rx_volume.search(output).group(1)
            muted = bool(self._rx_muted.search(output))
            return self.func(volume, muted)
        self.update = update

    def __str__(self):
        return self.update()
