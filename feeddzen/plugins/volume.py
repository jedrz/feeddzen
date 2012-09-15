#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import subprocess

from feeddzen import feeddzen, utils


class AlsaWidget(feeddzen.Widget):

    """Volume widget to use with alsa.

    Available special strings:
    - `{volume}` - percentage volume
    - `{state}` - 'off' if mixer is muted or 'on'"""

    _rx_volume = re.compile(r'(\d{1,3}%)')
    _rx_muted = re.compile(r'\[off\]')

    def __init__(self, timeout, template, template_muted=None,
                 mixer='Master', card='0', device='default'):
        """Arguments:
        - `template` - is used when mixer is not muted
        - `template_muted` - is used when mixer is muted, when is None,
          equals `template`
        - `mixer` - name of mixer, by default 'Master'
        - `card` - card number, by default 0
        - `device` - device id, by default 'default
        """
        super().__init__(timeout, template)
        self.template_muted = template if template_muted is None \
            else template_muted
        # build amixer command
        self.mixer_option = ['get', mixer]
        self.card_option = ['-c', card]
        self.device_option = ['-D', device]
        self.amixer_command = ['amixer'] + self.card_option + \
            self.device_option + self.mixer_option
        self.define_update()

    def define_update(self):
        @utils.memoize(self.timeout)
        def update():
            output_bytes = subprocess.check_output(self.amixer_command)
            output = output_bytes.decode('utf-8')
            muted = self._rx_muted.search(output)
            volume = self._rx_volume.search(output).group()
            if muted:
                return self.template_muted.format(volume=volume, state='off')
            else:
                return self.template.format(volume=volume, state='on')
        self.update = update

    def __str__(self):
        return self.update()
