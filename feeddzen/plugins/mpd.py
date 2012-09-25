#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO: use some python library

import subprocess
import re

from .. import utils
from .core import Widget


class MPDWidgetMPC(Widget):
    """MPD widget using mpc.

    Possible delimiters to use:
    %artist% - Artist file tag
    %album% - Album file tag
    %albumartist% - Album Artist file tag
    %composer% - Composer file tag
    %title% - Title file tag
    %track% - Track file tag
    %time% - Duration of file
    %file% - Path of file, relative to mpd's `music_directory` variable
    %position% - Playlist track number
    (from mpc man page)
    """

    def __init__(self, timeout, template, template_quiet=''):
        """Arguments:
        - `template` - is used when a song is playing
        - `template_quiet` - is used when no song is playing,
          by default empty string
        """
        super().__init__(timeout, template)
        self.template_quiet = template_quiet
        self._define_update()

    def _define_update(self):
        @utils.memoize(self.timeout)
        def update():
            # command has to be defined every time because the template
            # can be changed after init
            mpc_command = ['mpc', '--format', self.template]
            output_bytes = subprocess.check_output(mpc_command)
            output = output_bytes.decode('utf-8').splitlines()
            if len(output) == 1: # nothing is playing
                return self.template_quiet
            else:
                return output[0]
        self.update = update

    def __str__(self):
        return self.update()
