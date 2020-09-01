# -*- coding: utf-8 -*-
#
# This file is part of the julabo project
#
# Copyright (c) 2020 Tiago Coutinho
# Distributed under the LGPLv3. See LICENSE for more info.

"""
.. code-block:: yaml

    devices:
    - class: JulaboCF
      package: julabo.simulator
      transports:
      - type: serial
        url: /tmp/julabo-cf31-1
"""

import time

from sinstruments.simulator import BaseDevice


class BaseJulabo(BaseDevice):

    DEFAULT = {}

    newline = b"\r"

    def __init__(self, name, **opts):
        kwargs = {}
        if "newline" in opts:
            kwargs["newline"] = opts.pop("newline")
        self._config = dict(self.DEFAULT, **opts)
        self._on = True
        super().__init__(name, **kwargs)


class BaseJulaboCirculator(BaseJulabo):

    DEFAULT = {
        "MODE_01": "0",       # use set point (0..2)
        "MODE_02": "0",       # self tunning (0 - off; 1 - once; 2 - always)
        "MODE_03": "0",       # external input (0 - voltage; 1 - current
        "MODE_04": "0",       # temp control (0 - internal bath; 1 - external via pt100)
        "MODE_05": "0",       # start/stop (0 - stop; 1 - start)
        "MODE_08": "0",       # control dynamics (0 - aperiodic; 1 - standard)
        "SP_00": "30",        # set point 1 temperature
        "SP_01": "31",        # set point 2 temperature
        "SP_02": "32",        # set point 3 temperature
        "SP_03": "300.01",    # high temperature warning threshold (OverTemp)
        "SP_04": "2.34",      # low temperature warning threshold (SubTemp)
        "SP_05": "22.22",     # set point temp of external programmer (read only)
        "SP_06": "00.00",     # manipulated variable for the heater via serial line (-100 .. 100 %)
        "SP_07": "1",         # pump pressure stage (1 .. 4)
        "SP_08": "99",        # value of flowrate sensor connected to E-prog input (read only)
        "PAR_00": "00.00",    # temp difference between working and safety sensors (read only)
        "PAR_01": "123",      # Te time constant of external bath (read only)
        "PAR_02": "22",       # Si internal slope (read only)
        "PAR_03": "321",      # Ti time constant of internal bath (read only)
        "PAR_04": "0.0",      # CoSpeed for external control (0 .. 5.0)
        "PAR_05": "11",       # Factor pk/ph0 (read only)
        "PAR_06": "00.0",     # Xp internal ctrl (0.1 .. 99.9)
        "PAR_07": "0",        # Tn internal ctrl (3 .. 9999)
        "PAR_08": "0",        # Tv internal ctrl (0 .. 999)
        "PAR_09": "0",        # Xp cascade ctrl (0.1 .. 99.9)
        "PAR_10": "0",        # Proportional portion cascade ctrl (1 .. 99.9)
        "PAR_11": "0",        # Tn cascade ctrl (3 .. 9999)
        "PAR_12": "0",        # Tv cascade ctrl (0 .. 999)
        "PAR_13": "0",        # Max temp cascade ctrl
        "PAR_14": "0",        # Min temp cascade ctrl
        "PAR_15": "0",        # Upper band limit (0 .. 200)
        "PAR_16": "0",        # Lower band limit (0 .. 200)
        "HIL_00": "-5",       # desired maximum cooling power (only CF41)
        "HIL_01": "15",       # max heating power (10 .. 100) %
        "VERSION": "JULABO CRYOCOMPACT CF31 VERSION 5.0", # version
        "STATUS": "00 MANUAL START",  # current status
        "PV_00": "29.45",     # actual bath temp
        "PV_01": "3",         # heating power %
        "PV_02": "28.22",     # temp. registered by external pt100 sensor
        "PV_03": "29.69",     # temp. registered by safety sensor
        "PV_04": "34.44",     # set point temp of the excess temp protection
    }

    def handle_message(self, line):
        self._log.debug("request: %r", line)
        line = line.decode().strip().upper()
        if line in {"VERSION", "STATUS"}:
            result = self._config[line]
        elif line.startswith("IN_"):
            result = self._config.get(line[3:])
        else:
            cmd, value = line.split(" ", 1)
            self._config[cmd[4:]] = value
            if cmd == "OUT_MODE_05":
                status = "02 REMOTE STOP" if value == "0" else "03 REMOTE START"
                self._config["STATUS"] = status
            result = None
        if result is None:
            return
        result = result.encode() + b"\r\n"
        self._log.debug("reply: %r", result)
        return result


class JulaboCF(BaseJulaboCirculator):

    DEFAULT = dict(BaseJulaboCirculator.DEFAULT)


class JulaboHL(BaseJulaboCirculator):

    DEFAULT = dict(
        BaseJulaboCirculator.DEFAULT,
        VERSION="JULABO HIGHTECH FL HL/SL VERSION 1.0"
    )
