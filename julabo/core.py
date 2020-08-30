import enum
import time
import logging
import functools
import threading

import serial


# TODO: set latency (see pag.72 of CF31 manual "Important times for a command transmission")
# 250ms after command
# 10ms after query
COMMAND_LATENCY = 0.250
QUERY_LATENCY = 0.01


def serial_for_url(
    url, *args,
    baudrate=9600,
    bytesize=serial.SEVENBITS,
    parity=serial.PARITY_EVEN,
    stopbits=serial.STOPBITS_ONE,
    timeout=1,
    xonxoff=True
):
    conn = serial.serial_for_url(
        url, *args, baudrate=baudrate, bytesize=bytesize,
        parity=parity, stopbits=stopbits,
        xonxoff=xonxoff, timeout=timeout)
    lock = threading.Lock()
    last_query = 0
    last_command = 0

    def back_pressure():
        nonlocal last_query, last_command
        now = time.monotonic()
        future = max(last_query + QUERY_LATENCY, last_command + COMMAND_LATENCY)
        wait = future - now
        if wait > 0:
            time.sleep(wait)

    def consume():
        data = []
        while(conn.in_waiting):
            data.append(conn.read(conn.in_waiting))
        return b''.join(data)

    def send(data):
        back_pressure()
        try:
            conn.write(data)
        finally:
            nonlocal last_command
            last_command = time.monotonic()

    def write_readline(data):
        back_pressure()
        try:
            with lock:
                garbage = conn.consume()
                if garbage:
                    logging.warning('disposed of %r', garbage)
                conn.write(data)
                return conn.readline()
        finally:
            nonlocal last_query
            last_query = time.monotonic()
    conn.consume = consume
    conn.send = send
    conn.write_readline = write_readline
    return conn


def member(read=None, write=None, decode=lambda x: x, encode=lambda x: x):
    if read:
        if write:
            def member(self, value=None):
                if value is None:
                    return decode(self._ask(read))
                else:
                    self._send("{} {}".format(write, encode(value)))
        else:
            def member(self):
                return decode(self._ask(read))
    else:
        def member(self, value=None):
            if value is None:
                self._send(write)
            else:
                self._send("{} {}".format(write, encode(value)))
    return member


Float1 = functools.partial(member, decode=float, encode=lambda x: '{.1f}'.format(x))
Float2 = functools.partial(member, decode=float, encode=lambda x: '{.2f}'.format(x))
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


class BaseJulabo:

    def __init__(self, connection):
        """
        Args:
            connection (object): any object with write_readline method.
                Typical are sockio.TCP or serialio.aio.tcp.Serial
        """
        self._log = logging.getLogger("julabo.{}".format(type(self).__name__))
        self._conn = connection

    def close(self):
        self._conn.close()

    def _ask(self, request):
        request = (request + "\r").encode()
        self._log.debug("request: %r", request)
        reply = self._conn.write_readline(request)
        self._log.debug("reply: %r", reply)
        return reply.decode().strip()

    def _send(self, request):
        request = (request + "\r").encode()
        self._log.debug("command: %r", request)
        self._conn.send(request)

    version = member("VERSION")
    status = member("STATUS")

    is_started = member("IN_MODE_05", decode=lambda x: x == "1")

    def start(self):
        self._send("OUT_MODE_05 1")

    def stop(self):
        self._send("OUT_MODE_05 0")


class JulaboCF(BaseJulabo):

    bath_temperature = Float2("IN_PV_00")
    heating_power = Float2("IN_PV_01")
    external_temperature = Float2("IN_PV_02")
    safety_temperature = Float2("IN_PV_03")
    set_point_1 = Float2("IN_SP_00", "OUT_SP_00")
    set_point_2 = Float2("IN_SP_01", "OUT_SP_01")
    set_point_3 = Float2("IN_SP_02", "OUT_SP_02")
    high_temperature_warning = Float2("IN_SP_02", "OUT_SP_02")
    low_temperature_warning = Float2("IN_SP_03", "OUT_SP_03")
    active_set_point_channel = member(
        "IN_MODE_01", "OUT_MODE_01",
        decode=lambda v: int(v) + 1,
        encode=lambda v: str(int(v) - 1)
    )
    self_tunning = Enum("IN_MODE_02", "OUT_MODE_02", SelfTunning)
    external_input = Enum("IN_MODE_03", "OUT_MODE_03", ExternalInput)
    temperature_control = Enum("IN_MODE_04", "OUT_MODE_04", TemperatureControl)


class JulaboFC(BaseJulabo):

    working_temperature = Float1("IN_SP_00", "OUT_SP_00")
    high_temperature = Int("IN_SP_01", "OUT_SP_01")
    low_temperature = Int("IN_SP_02", "OUT_SP_02")
    control_ratio = Int("IN_SP_03", "OUT_SP_03")
    feed_temperature = Float2("IN_PV_00")
    external_sensor_temperature = Float2("IN_PV_01")
    heater_capacity = Float2("IN_PV_02")
    return_temperature = Float2("IN_PV_03")
    safety_temperature = Float2("IN_PV_04")

