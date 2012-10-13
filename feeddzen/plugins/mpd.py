#!/USSR/bin/env python
# -*- coding: utf-8 -*-

# TODO: Use some python library.

import subprocess
import re

from .. import utils
from .core import BaseWidget


class MPDWidgetMPC(BaseWidget):
    """MPD widget using *mpc* to get info.

    Arguments which will be passed to the function:

    1. `True` if a song is playing, otherwise `False`,
    2. A dictionary with keys:

       - `'artist'` - artist file tag,
       - `'album'` - album file tag,
       - `'albumartist'` - album Artist file tag,
       - `'composer'` - composer file tag,
       - `'title'` - title file tag,
       - `'track'` - track file tag,
       - `'time'` - duration of file,
       - `'file'` - path of file,
       - `'position'` - playlist track number.
    """

    # List of possible delimiters which are recognised by 'mpc'.
    _delimeters = (
        '%artist%',
        '%album%',
        '%albumartist%',
        '%composer%',
        '%title%',
        '%track%',
        '%time%',
        '%file%',
        '%position%'
    )
    # Remove '%'.
    _keys = tuple(d[1:-1] for d in _delimeters)
    # 'mpc' command to get all tags. Delimiters are separated by '<>'
    _mpc_command = ['mpc', '--format',  '<>'.join(_delimeters) + '<>']
    # Regexp to capture one tag.
    _rx_delimeter = re.compile('(.*?)<>')

    def __init__(self, timeout, func):
        super().__init__(timeout, func)
        self._define_update()

    def _define_update(self):
        @utils.memoize(self.timeout)
        def update():
            output_bytes = subprocess.check_output(self._mpc_command)
            output = output_bytes.decode('utf-8').splitlines()
            if len(output) == 1:    # nothing is playing
                return self.func(False, None)
            else:
                matches = {key: match for key, match in zip(
                               self._keys,
                               self._rx_delimeter.findall(output[0]))}
                return self.func(True, matches)
        self.update = update

    def __str__(self):
        return self.update()
