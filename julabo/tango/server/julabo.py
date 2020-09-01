from tango import DevState
from tango.server import Device, attribute, command, device_property

from julabo import (
    JulaboCF as _JulaboCF,
    JulaboHL as _JulaboHL,
    JulaboFC as _JulaboFC,
    protocol_for_url,
    SelfTunning, ExternalInput, TemperatureControl, ControlMode
)


class BaseJulabo(Device):

    url = device_property(dtype=str)
    baudrate = device_property(dtype=int, default_value=9600)
    bytesize = device_property(dtype=int, default_value=8)
    parity = device_property(dtype=str, default_value='N')

    Julabo = None

    async def init_device(self):
        await super().init_device()
        kwargs = dict(concurrency="asyncio")
        if self.url.startswith("serial") or self.url.startswith("rfc2217"):
            kwargs = dict(baudrate=self.baudrate, bytesize=self.bytesize,
                          parity=self.parity)

        protocol = protocol_for_url(self.url, **kwargs)
        self.julabo = self.Julabo(protocol)

    async def dev_state(self):
        status_code = int((await self.julabo.status())[:2])
        if status_code in {0, 2}:
            return DevState.STANDBY
        elif status_code in {1, 3}:
            return DevState.RUNNING
        elif status_code < 0:
            return DevState.ALARM
        return DevState.FAULT

    async def dev_status(self):
        return await self.julabo.status()

    @attribute(dtype=str)
    async def identification(self):
        return await self.julabo.identification()

    @attribute(dtype=bool)
    async def is_started(self):
        return await self.julabo.is_started()

    @command
    async def start(self):
        await self.julabo.start()

    @command
    async def stop(self):
        await self.julabo.stop()


class BaseJulaboCirculator(BaseJulabo):

    @attribute(dtype=float)
    async def bath_temperature(self):
        return await self.julabo.bath_temperature()

    @attribute(dtype=float)
    async def heating_power(self):
        return await self.julabo.heating_power()

    @attribute(dtype=float)
    async def external_temperature(self):
        return await self.julabo.external_temperature()

    @attribute(dtype=float)
    async def safety_temperature(self):
        return await self.julabo.safety_temperature()

    @attribute(dtype=float)
    async def set_point_1(self):
        return await self.julabo.set_point_1()

    @set_point_1.setter
    async def set_point_1(self, value):
        await self.julabo.set_point_1(value)

    @attribute(dtype=float)
    async def set_point_2(self):
        return await self.julabo.set_point_2()

    @set_point_2.setter
    async def set_point_2(self, value):
        await self.julabo.set_point_2(value)

    @attribute(dtype=float)
    async def set_point_3(self):
        return await self.julabo.set_point_3()

    @set_point_3.setter
    async def set_point_3(self, value):
        await self.julabo.set_point_3(value)

    @attribute(dtype=float)
    async def high_temperature(self):
        return await self.julabo.high_temperature()

    @high_temperature.setter
    async def high_temperature(self, value):
        await self.julabo.high_temperature(value)

    @attribute(dtype=float)
    async def low_temperature(self):
        return await self.julabo.low_temperature()

    @low_temperature.setter
    async def low_temperature(self, value):
        await self.julabo.low_temperature(value)

    @attribute(dtype=int, min_value=1, max_value=3)
    async def active_set_point_channel(self):
        return await self.julabo.active_set_point_channel()

    @active_set_point_channel.setter
    async def active_set_point_channel(self, value):
        await self.julabo.active_set_point_channel(value)

    @attribute(dtype=SelfTunning)
    async def self_tunning(self):
        return await self.julabo.self_tunning()

    @self_tunning.setter
    async def self_tunning(self, value):
        await self.julabo.self_tunning(value)

    @attribute(dtype=ExternalInput)
    async def external_input(self):
        return await self.julabo.external_input()

    @external_input.setter
    async def external_input(self, value):
        await self.julabo.external_input(value)

    @attribute(dtype=TemperatureControl)
    async def temperature_control(self):
        return await self.julabo.temperature_control()

    @temperature_control.setter
    async def temperature_control(self, value):
        await self.julabo.temperature_control(value)

    @attribute(dtype=bool)
    async def is_started(self):
        return await self.julabo.is_started()


class JulaboCF(BaseJulaboCirculator):
    """Julabo cryo-compact circulator"""

    Julabo = _JulaboCF


class JulaboHL(BaseJulaboCirculator):
    """Julabo heating circulator"""

    Julabo = _JulaboHL


class JulaboFC(BaseJulabo):
    """Julabo recirculating cooler"""

    Julabo = _JulaboFC

    @attribute(dtype=float)
    async def working_temperature(self):
        return await self.julabo.working_temperature()

    @working_temperature.setter
    async def working_temperature(self, value):
        await self.julabo.working_temperature(value)

    @attribute(dtype=int)
    async def high_temperature(self):
        return await self.julabo.high_temperature()

    @attribute(dtype=int)
    async def low_temperature(self):
        return await self.julabo.low_temperature()

    @attribute(dtype=int)
    async def control_ratio(self):
        return await self.julabo.control_ratio()

    @control_ratio.setter
    async def control_ratio(self, value):
        await self.julabo.control_ratio(value)

    @attribute(dtype=float)
    async def feed_temperature(self):
        return await self.julabo.feed_temperature()

    @feed_temperature.setter
    async def feed_temperature(self, value):
        await self.julabo.feed_temperature(value)

    @attribute(dtype=float)
    async def external_temperature(self):
        return await self.julabo.external_temperature()

    @attribute(dtype=float)
    async def heater_capacity(self):
        return await self.julabo.heater_capacity()

    @attribute(dtype=float)
    async def return_temperature(self):
        return await self.julabo.return_temperature()

    @attribute(dtype=float)
    async def safety_temperature(self):
        return await self.julabo.safety_temperature()
