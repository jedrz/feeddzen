#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import datetime

from feeddzen import feeddzen, utils


class BatteryWidget(feeddzen.Widget):
    """Battery Widget.

    Infomation about battery is taken from
    /sys/class/power_supply/BAT_NUMBER/uevent file.

    Several templates can be used according to the current state
    of the battery to print proper kind of information:
    - `template_discharging`,
    - `template_charging`,
    - `template`.

    Supported special delimeters:
    - '{percentage}' - estimated capacity of the battery in percentage
    - '{hours}' - estimated hours to discharge or charge
    - '{minutes}' - estimated minutes
    - '{seconds}' - estimated seconds
    - '{hour_et}' - estimated hour when the battery will be
       discharged or charged
    - '{minute_et}' - estimated minute
    - '{second_et}' - estimated second
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

    def __init__(self, timeout, template, template_discharging=None,
                 template_charging=None, bat_name='BAT0', full_design=True):
        """Arguments:
        - `template` - is used when the battery is not discharging or charging,
        - `template_discharging` - the battery is discharging, if None
          then `template` is used,
        - `template_charging` - the battery is charging, if None
          then `template` is used,
        - `bat_name` - the name of battery, by default BAT0,
        - `full_design` - whether to use full design or real values
          of the capacity of the battery. If your battery is worn
          and full_design is True (which by default is) then
          you will get lower than 100% the percentage value.
          Set the variable to False if you don't like it.
        """
        super().__init__(timeout, template)
        self.template_discharging = \
            template if template_discharging is None else template_discharging
        self.template_charging = \
            template if template_charging is None else template_charging
        self.bat_name = bat_name
        self.full_design = full_design
        self._define_update()

    def _get_all_matches(self, s):
        """Return a dictionary with all regexp matches.

        The result looks like:
        {'charge_full': int(self._rx_charge_full.search(s).group(1))
                        if ...search(s) is not None else None
        ...}

        Beginning '_rx_' is stripped in keys.
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
        """Return estimated capacity of battery as percentage (str).

        `matches` - a dictionary returned by `_get_all_matches`.
        """
        full = 'full_design' if self.full_design else 'full'
        # Try to use CHARGE_NOW and CHARGE_FULL firstly if they are present,
        # if not then use ENERGY_*.
        present = matches['charge_now'] or matches['energy_now']
        design = matches['charge_{}'.format(full)] \
            or  matches['energy_{}'.format(full)]
        percentage = present / design * 100.0
        # Change accuracy and and percent sign.
        return '{:.2f}%'.format(percentage)

    def _get_remaining(self, matches):
        """Return seconds to get fully discharged or charged battery.

        The returned value is only an *approximation*.

        `matches` - a dictionary returned by `_get_all_matches`.
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
        else:   # there is nothing to measure
            return None

    def _get_emptytime(self, matches, remaining=None):
        """Return time when the battery will be fully charged or discharged.

        A `datetime.datetime` object is returned with *estimated* time.

        `matches` - a dictionary returned by `_get_all_matches`,
        `remaining` - remaining seconds to discharge.
        """
        remaining = remaining or self._get_remaining(matches)
        if remaining:
            delta = datetime.timedelta(seconds=remaining)
            date = datetime.datetime.now() + delta
            return date
        return remaining

    def _define_update(self):
        @utils.memoize(self.timeout)
        def update():
            try:
                # open file with information we need
                file_obj = open(self._bat_path.format(battery=self.bat_name))
            except IOError:
                # FIXME: Maybe some logging would be better.
                return 'ERROR'
            s = file_obj.read()
            file_obj.close()
            matches = self._get_all_matches(s)
            percentage = self._get_percentage(matches)
            status = matches['status']
            # The same calculations have to done when
            # the battery is discharging or charging.
            if status.lower().endswith('charging'):
                remaining = self._get_remaining(matches)
                hours, remainder = divmod(remaining, 3600)
                minutes, seconds = divmod(remainder, 60)
                # Pass 'remaining' as an argument not to call
                # _get_remaining method twice.
                emptytime = self._get_emptytime(matches, remaining)
                # Choose proper template.
                template = getattr(self,
                                   'template_{}'.format(status.lower()))
                return template.format(
                    percentage=percentage,
                    hours=hours,
                    minutes=minutes,
                    seconds=seconds,
                    hour_et=emptytime.hour,
                    minute_et=emptytime.minute,
                    second_et=emptytime.second)
            else:
                return self.template.format(
                    percentage=percentage,
                    hours='',
                    minutes='',
                    seconds='',
                    hour_et='',
                    minute_et='',
                    second_et='')
        self.update = update

    def __str__(self):
        return self.update()
