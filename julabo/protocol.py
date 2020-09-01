import time
import asyncio
import logging
import threading


def encode(data):
    if isinstance(data, str):
        data = data.encode()
    if not data.endswith(b"\r"):
        data += b"\r"
    return data


def decode(data):
    data = data.strip()                # remove '\r\n'
    data = data.replace(b"\x11", b"")  # remove DTS1 (XON)
    data = data.replace(b"\x13", b"")  # remove DTS3 (XOFF)
    return data.decode()


class BaseProtocol:
    """
    Handles communication protocol
    - latency
    - encode/decode bytes <-> text
    - serializes read calls
    """

    # set latency (see pag.72 of CF31 manual "Important times for
    # a command transmission"); 250ms after command; 10ms after query
    COMMAND_LATENCY = 0.250
    QUERY_LATENCY = 0.01

    def __init__(self, connection, log=None):
        self.conn = connection
        self._last_query = 0
        self._last_command = 0
        self._log = log or logging.getLogger('julabo.{}'.format(type(self).__name__))

    def _wait_time(self):
        now = time.monotonic()
        future = max(self._last_query + self.QUERY_LATENCY,
                     self._last_command + self.COMMAND_LATENCY)
        return future - now


class AIOProtocol(BaseProtocol):

    def __init__(self, connection, log=None):
        super().__init__(connection, log=log)
        self._lock = asyncio.Lock()

    async def _back_pressure(self):
        wait = self._wait_time()
        if wait > 0:
            await asyncio.sleep(wait)

    async def write(self, data):
        data = encode(data)
        self._log.debug("write: %r", data)
        await self._back_pressure()
        try:
            await self.conn.write(data)
        finally:
            self._last_command = time.monotonic()

    async def write_readline(self, data):  # aka: query or put_get
        data = encode(data)
        self._log.debug("write: %r", data)
        await self._back_pressure()
        try:
            async with self._lock:
                # TODO: maybe consume garbage in the buffer ?
                reply = await self.conn.write_readline(data)
            self._log.debug("read: %r", reply)
            return decode(reply)
        finally:
            self._last_query = time.monotonic()


class IOProtocol(BaseProtocol):

    def __init__(self, connection, log=None):
        super().__init__(connection, log=log)
        self._lock = threading.Lock()

    def _back_pressure(self):
        wait = self._wait_time()
        if wait > 0:
            time.sleep(wait)

    def write(self, data):
        data = encode(data)
        self._log.debug("write: %r", data)
        self._back_pressure()
        try:
            return self.conn.write(data)
        finally:
            self._last_command = time.monotonic()

    def write_readline(self, data):  # aka: query or put_get
        data = encode(data)
        self._log.debug("write: %r", data)
        self._back_pressure()
        try:
            with self._lock:
                # TODO: maybe consume garbage in the buffer ?
                reply = self.conn.write_readline(data)
            self._log.debug("read: %r", reply)
            return decode(reply)
        finally:
            self._last_query = time.monotonic()


def Protocol(connection):
    func = connection.write_readline
    klass = AIOProtocol if asyncio.iscoroutinefunction(func) else IOProtocol
    return klass(connection)


def protocol_for_url(url, *args, **kwargs):
    from .connection import connection_for_url
    conn = connection_for_url(url, *args, **kwargs)
    return Protocol(conn)
