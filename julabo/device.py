import enum
import time
import asyncio
import logging
import functools

from .protocol import Protocol


__all__ = [
    "JulaboCF", "JulaboHL", "JulaboFC",
    "SelfTunning", "ExternalInput", "TemperatureControl", "ControlMode"
]


async def _call(func, coro):
    return func(await coro)


def _sync_call(func, arg):
    if asyncio.iscoroutine(arg):
        return _call(func, arg)
    else:
        return func(arg)


def member(read=None, write=None, decode=lambda x: x, encode=lambda x: x):

    if read:
        if write:
            def member(self, value=None):
                if value is None:
                    return _sync_call(decode, self.write_readline(read))
                else:
                    return self.write("{} {}".format(write, encode(value)))
        else:
            def member(self):
                return _sync_call(decode, self.write_readline(read))
    else:
        def member(self, value=None):
            if value is None:
                return self.write(write)
            else:
                return self.write("{} {}".format(write, encode(value)))
    return member


Float1 = functools.partial(member, decode=float, encode=lambda x: '{:.1f}'.format(float(x)))
Float2 = functools.partial(member, decode=float, encode=lambda x: '{:.2f}'.format(float(x)))
Int = functools.partial(member, decode=int, encode=lambda x: str(int(x)))


def Enum(read=None, write=None, enu=None):
    return member(read=read, write=write, decode=enu.decode, encode=enu.encode)


class IntEnum(enum.IntEnum):

    @classmethod
    def decode(cls, v):
        return cls(int(v))


def make_encoder(klass):
    def encode(value):
        if isinstance(value, klass):
            value = value.value
        elif isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                value = getattr(klass, value.capitalize()).value
        return str(value)
    klass.encode = encode


class SelfTunning(IntEnum):
    Off = 0
    Once = 1
    Always = 2
make_encoder(SelfTunning)


class ExternalInput(IntEnum):
    Voltage = 0
    Current = 1
make_encoder(ExternalInput)


class TemperatureControl(IntEnum):
    Internal = 0
    External = 1
make_encoder(TemperatureControl)


class ControlMode(IntEnum):
    Remote = 0
    Local = 1
make_encoder(ControlMode)


class BaseJulabo:

    def __init__(self, connection):
        self._log = logging.getLogger("julabo.{}".format(type(self).__name__))
        self.protocol = Protocol(connection)

    def write(self, request):
        return self.protocol.write(request)

    def write_readline(self, request):
        return self.protocol.write_readline(request)

    identification = member("VERSION")
    status = member("STATUS")

    is_started = member("IN_MODE_05", decode=lambda x: x == "1")

    def start(self):
        return self.write("OUT_MODE_05 1")

    def stop(self):
        return self.write("OUT_MODE_05 0")


class BaseJulaboCirculator(BaseJulabo):
    """Base julabo circulators"""

    bath_temperature = Float2("IN_PV_00")
    heating_power = Float2("IN_PV_01")
    external_temperature = Float2("IN_PV_02")
    safety_temperature = Float2("IN_PV_03")
    set_point_1 = Float2("IN_SP_00", "OUT_SP_00")
    set_point_2 = Float2("IN_SP_01", "OUT_SP_01")
    set_point_3 = Float2("IN_SP_02", "OUT_SP_02")
    high_temperature = Float2("IN_SP_02", "OUT_SP_02")
    low_temperature = Float2("IN_SP_03", "OUT_SP_03")
    active_set_point_channel = member(
        "IN_MODE_01", "OUT_MODE_01",
        decode=lambda v: int(v) + 1,
        encode=lambda v: str(int(v) - 1)
    )
    self_tunning = Enum("IN_MODE_02", "OUT_MODE_02", SelfTunning)
    external_input = Enum("IN_MODE_03", "OUT_MODE_03", ExternalInput)
    temperature_control = Enum("IN_MODE_04", "OUT_MODE_04", TemperatureControl)


class JulaboCF(BaseJulaboCirculator):
    """Julabo cryo-compact circulator"""


class JulaboHL(BaseJulaboCirculator):
    """Julabo heating circulator"""
    pass


class JulaboFC(BaseJulabo):
    """Julabo recirculating cooler"""

    working_temperature = Float1("IN_SP_00", "OUT_SP_00")
    high_temperature = Int("IN_SP_01")
    low_temperature = Int("IN_SP_02")
    control_ratio = Int("IN_SP_03", "OUT_SP_03")
    feed_temperature = Float2("IN_PV_00")
    external_emperature = Float2("IN_PV_01")
    heater_capacity = Float2("IN_PV_02")
    return_temperature = Float2("IN_PV_03")
    safety_temperature = Float2("IN_PV_04")
    control_mode = Enum("IN_MODE_04", "OUT_MODE_04", ControlMode)
