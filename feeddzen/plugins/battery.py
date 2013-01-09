#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import datetime

from .. import utils
from .core import BaseWidget


class BatteryWidget(BaseWidget):
    """Battery Widget.

    Infomation about battery is taken from
    ``/sys/class/power_supply/BAT_NUMBER/uevent`` file.

    Arguments which will be passed to the function:

    1. state - a string, *charging*, *discharging*, *full* or *unknown*.
    2. A dictionary with keys:

       - `'percentage'` - estimated capacity of the battery in percentage.

       Only if battery is charging or discharging:

       - `'hours'` - estimated hours to discharge or charge,
       - `'minutes'` - estimated minutes,
       - `'seconds'` - estimated seconds,
       - `'hour_et'` - estimated hour when the battery will be discharged
         or charged,
       - `'minute_et'` - estimated minute,
       - `'second_et'` - estimated second.

    :param bat_name: battery identifier, replaces *BAT_NUMBER* in the above path.
    :param full_design: specify whether full design battery values should
     be used to compute the capacity. If your battery is worn out
     and `full_design` is `True` (which by default is) then you will probably
     get lower than 100% the capacity value. Pass `False` if you don't
     like this behaviour.
    :param time_as_string: controls time type returned. If is `True` then
     time is filled with zeros and return as string otherwise an integers
     are returned.
    """

    _bat_path = '/sys/class/power_supply/{battery}/uevent'
    # A note about units:
    # CHARGE_* attributes represents capacity in µAh
    # ENERGY_* attributes represents capacity in µWh
    # CURRENT_* attributes in µA
    _rx_charge_full_design = re.compile(
        r'POWER_SUPPLY_CHARGE_FULL_DESIGN=(\d+)')
    _rx_charge_full = re.compile(r'POWER_SUPPLY_CHARGE_FULL=(\d+)')
    _rx_charge_now = re.compile(r'POWER_SUPPLY_CHARGE_NOW=(\d+)')
    _rx_energy_full_design = re.compile(
        r'POWER_SUPPLY_ENERGY_FULL_DESIGN=(\d+)')
    _rx_energy_full = re.compile(r'POWER_SUPPLY_ENERGY_FULL=(\d+)')
    _rx_energy_now = re.compile(r'POWER_SUPPLY_ENERGY_NOW=(\d+)')
    _rx_current_now = re.compile(r'POWER_SUPPLY_CURRENT_NOW=(\d+)')
    _rx_voltage_now = re.compile(r'POWER_SUPPLY_VOLTAGE_NOW=(\d+)')
    _rx_status = re.compile(r'POWER_SUPPLY_STATUS=(\w+)')

    def __init__(self, timeout, func, bat_name='BAT0', full_design=True,
                 time_as_string=True):
        super().__init__(timeout, func)
        self.bat_name = bat_name
        self.full_design = full_design
        self.time_as_string = time_as_string
        self._define_update()

    def _get_all_matches(self, s):
        """Return a dictionary with all regexp matches.

        The result looks like::

            {'charge_full': int(self._rx_charge_full.search(s).group(1))
                            if ...search(s) is not None else None
            ...}

        Beginning *_rx_* are stripped in keys.
        """
        d = {}
        for attr in dir(self):
            if attr.startswith('_rx_'):
                match = getattr(self, attr).search(s)
                name = attr[4:] # strip '_rx_'
                match_res = match.group(1) if match else None
                # If match result is digit then convert it to integer
                # otherwise return as it is.
                if match_res and match_res.isdigit():
                    d[name] = int(match_res)
                else:
                    d[name] = match_res
        return d

    def _get_percentage(self, matches):
        """Return estimated capacity of battery as percentage.

        :param matches: a dictionary returned by `_get_all_matches`.
        :rtype: integer
        """
        full = 'full_design' if self.full_design else 'full'
        # Try to use CHARGE_NOW and CHARGE_FULL firstly if they are present,
        # if not then use ENERGY_*.
        present = matches['charge_now'] or matches['energy_now']
        design = matches['charge_{}'.format(full)] \
            or  matches['energy_{}'.format(full)]
        percentage = present / design * 100.0
        # I suppose such an 'accuracy' is not needed.
        return round(percentage, 2)

    def _get_remaining(self, matches):
        """Return seconds to get fully discharged or charged battery.

        The returned value is only an *approximation*.

        :param matches: a dictionary returned by `_get_all_matches`.
        :rtype: integer
        """
        full = 'full_design' if self.full_design else 'full'
        status = matches['status']
        charge_now = matches['charge_now']
        # If `charge_now` is None then compute the value
        # using ENERGY_NOW and VOLTAGE_NOW.
        if not charge_now:
            charge_now = matches['energy_now'] / matches['voltage_now']
        current_now = matches['current_now']
        if status == 'Discharging':
            # remaining seconds = µAh * 3600 / µA
            remaining_seconds = int(charge_now * 3600 / current_now)
            return remaining_seconds
        elif status == 'Charging':
            charge_full = matches['charge_{}'.format(full)]
            if not charge_full:
                charge_full = \
                    matches['energy_{}'.format(full)] / matches['voltage_now']
            # `charge_full` - `charge_now` is the remaining capacity
            # for fully charged battery.
            remaining_seconds = int((charge_full - charge_now) \
                * 3600 / current_now)
            return remaining_seconds
        else:    # There is nothing to measure
            return None

    def _get_remaining_time(self, matches, remaining=None):
        """Return remaining time to get fully discharged or charged battery.

        A tuple - (hours, minutes, seconds) is returned.

        :param matches: a dictionary returned by `_get_all_matches`.
        :param remaining: remaining seconds to discharge or charge.
        """
        remaining = remaining or self._get_remaining(matches)
        if remaining:
            hours, remainder = divmod(remaining, 3600)
            minutes, seconds = divmod(remainder, 60)
            if self.time_as_string:
                return tuple('{:02d}'.format(n)
                             for n in (hours, minutes, seconds))
            else:
                return (hours, minutes, seconds)
        return None

    def _get_empty_time(self, matches, remaining=None):
        """Return time when the battery will be fully charged or discharged.

        A tuple - (hours, minutes, seconds) is returned. I assume it will
        take no longer than one day.

        :param matches: a dictionary returned by `_get_all_matches`.
        :param remaining: remaining seconds to discharge or charge.

        """
        remaining = remaining or self._get_remaining(matches)
        if remaining:
            delta = datetime.timedelta(seconds=remaining)
            date = datetime.datetime.now() + delta
            if self.time_as_string:
                return tuple('{:02d}'.format(n)
                             for n in (date.hour, date.minute, date.second))
            else:
                return (date.hour, date.minute, date.second)
        return None

    def _define_update(self):
        @utils.memoize(self.timeout)
        def update():
            try:
                # Open file with information we need.
                file_obj = open(self._bat_path.format(battery=self.bat_name))
            except IOError:
                # FIXME: Maybe some logging would be better.
                return 'ERROR'
            s = file_obj.read()
            file_obj.close()
            matches = self._get_all_matches(s)
            percentage = self._get_percentage(matches)
            status = matches['status'].lower()
            # The same calculations have to done when
            # the battery is discharging or charging.
            if status.endswith('charging'):
                remaining = self._get_remaining(matches)
                # Pass 'remaining' as an argument not to call
                # _get_remaining method twice.
                remaining_time = self._get_remaining_time(matches, remaining)
                empty_time = self._get_empty_time(matches, remaining)
                return self.func(
                    status, {
                        'percentage': percentage,
                        'hours': remaining_time[0],
                        'minutes': remaining_time[1],
                        'seconds': remaining_time[2],
                        'hour_et': empty_time[0],
                        'minute_et': empty_time[1],
                        'second_et': empty_time[2]
                    }
                )
            else:
                return self.func(
                    status, {
                        'percentage': percentage
                    }
                )
        self.update = update

    def __str__(self):
        return self.update()
