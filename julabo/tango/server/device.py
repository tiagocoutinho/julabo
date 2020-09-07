import functools

from tango import DevState
from tango.server import Device, attribute, command, device_property

from julabo import (
    JulaboCF as _JulaboCF,
    JulaboHL as _JulaboHL,
    JulaboFC as _JulaboFC,
    connection_for_url
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
        self.connection = connection_for_url(self.url, **kwargs)
        self.julabo = self.Julabo(self.connection)

    async def delete_device(self):
        await self.connection.close()

    async def dev_state(self):
        try:
            if not self.connection.is_open:
                await self.connection.open()
            status_code = int((await self.julabo.status())[:2])
        except:
            return DevState.FAULT
        if status_code in {0, 2}:
            return DevState.STANDBY
        elif status_code in {1, 3}:
            return DevState.RUNNING
        elif status_code < 0:
            return DevState.ALARM
        return DevState.FAULT

    async def dev_status(self):
        try:
            if not self.connection.is_open:
                await self.connection.open()
            self.__status = await self.julabo.status()
        except Exception as error:
            import traceback
            self.__status = "{!r}\n\nDetails:\n{}".format(
                error, traceback.format_exc()
            )
        return self.__status

    @attribute(dtype=str, label="Identification")
    async def identification(self):
        """Device identification (model and version)"""
        return await self.julabo.identification()

    @attribute(dtype=bool, label="Is started?")
    async def is_started(self):
        """Is device started or not"""
        return await self.julabo.is_started()

    @command
    async def start(self):
        """Start the device"""
        await self.julabo.start()

    @command
    async def stop(self):
        """Stop the device"""
        await self.julabo.stop()


class BaseJulaboCirculator(BaseJulabo):

    @attribute(dtype=float, label="Bath temperature", unit="degC")
    async def bath_temperature(self):
        """Actual bath temperature"""
        return await self.julabo.bath_temperature()

    @attribute(dtype=float, label="Heating power", unit="%")
    async def heating_power(self):
        """Heating power being used"""
        return await self.julabo.heating_power()

    @attribute(dtype=float, label="External temperature", unit="degC")
    async def external_temperature(self):
        """Temperature registered by external PT100 sensor"""
        return await self.julabo.external_temperature()

    @attribute(dtype=float, label="Safety temperature", unit="degC")
    async def safety_temperature(self):
        """Temperature registered by the safety sensor"""
        return await self.julabo.safety_temperature()

    @attribute(dtype=float, label="Set point 1", unit="degC")
    async def set_point_1(self):
        """Working temperature set point channel 1"""
        return await self.julabo.set_point_1()

    @set_point_1.setter
    async def set_point_1(self, value):
        await self.julabo.set_point_1(value)

    @attribute(dtype=float, label="Set point 2", unit="degC")
    async def set_point_2(self):
        """Working temperature set point channel 2"""
        return await self.julabo.set_point_2()

    @set_point_2.setter
    async def set_point_2(self, value):
        await self.julabo.set_point_2(value)

    @attribute(dtype=float, label="Set point 3", unit="degC")
    async def set_point_3(self):
        """Working temperature set point channel 3"""
        return await self.julabo.set_point_3()

    @set_point_3.setter
    async def set_point_3(self, value):
        await self.julabo.set_point_3(value)

    @attribute(dtype=float, label="High temperature", unit="degC")
    async def high_temperature(self):
        """High temperature warning limit"""
        return await self.julabo.high_temperature()

    @high_temperature.setter
    async def high_temperature(self, value):
        await self.julabo.high_temperature(value)

    @attribute(dtype=float, label="Low temperature", unit="degC")
    async def low_temperature(self):
        """Low temperature warning limit"""
        return await self.julabo.low_temperature()

    @low_temperature.setter
    async def low_temperature(self, value):
        await self.julabo.low_temperature(value)

    @attribute(dtype=int, label="Active set point channel", min_value=1, max_value=3)
    async def active_set_point_channel(self):
        return await self.julabo.active_set_point_channel()

    @active_set_point_channel.setter
    async def active_set_point_channel(self, value):
        await self.julabo.active_set_point_channel(value)

    @attribute(dtype=str, label="Self tunning")
    async def self_tunning(self):
        """Self tunning (off|once|always)"""
        return (await self.julabo.self_tunning()).name

    @self_tunning.setter
    async def self_tunning(self, value):
        await self.julabo.self_tunning(value)

    @attribute(dtype=str, label="External input")
    async def external_input(self):
        """External programmer input (voltage|current)"""
        return (await self.julabo.external_input()).name

    @external_input.setter
    async def external_input(self, value):
        await self.julabo.external_input(value)

    @attribute(dtype=str, label="Temperature control")
    async def temperature_control(self):
        """Temperature control (internal|external)"""
        return (await self.julabo.temperature_control()).name

    @temperature_control.setter
    async def temperature_control(self, value):
        await self.julabo.temperature_control(value)


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
