from tango import DevState
from tango.server import Device, attribute, command, device_property

from julabo import JulaboCF as _JulaboCF, JulaboFC as _JulaboFC, serial_for_url


class BaseJulabo(Device):

    url = device_property(dtype=str)
    baudrate = device_property(dtype=int, default_value=9600)
    bytesize = device_property(dtype=int, default_value=8)
    parity = device_property(dtype=str, default_value='N')

    Julabo = None

    def init_device(self):
        super().init_device()
        conn = serial_for_url(self.url, baudrate=self.baudrate,
                              bytesize=self.bytesize, parity=self.parity)
        self.julabo = self.Julabo(conn)

    def dev_state(self):
        status_code = int(self.julabo.status()[:2])
        if status_code in {0, 2}:
            return DevState.OFF
        elif status_code in {1, 3}:
            return DevState.ON
        elif status_code < 0:
            return DevState.ALARM
        return DevState.FAULT

    def dev_status(self):
        return self.julabo.status()

    @attribute(dtype=str)
    def version(self):
        return self.julabo.version()

    @attribute(dtype=bool)
    def is_started(self):
        return self.julabo.is_started()

    @command
    def start(self):
        self.julabo.start()

    @command
    def stop(self):
        self.julabo.stop()


class JulaboCF(BaseJulabo):

    Julabo = _JulaboCF

    @attribute(dtype=float)
    def bath_temperature(self):
        return self.julabo.bath_temperature()

    @attribute(dtype=float)
    def heating_power(self):
        return self.julabo.heating_power()

    @attribute(dtype=float)
    def external_temperature(self):
        return self.julabo.external_temperature()

    @attribute(dtype=float)
    def safety_temperature(self):
        return self.julabo.safety_temperature()

    @attribute(dtype=float)
    def set_point_1(self):
        return self.julabo.set_point_1()

    @set_point_1.setter
    def set_point_1(self, value):
        self.julabo.set_point_1(value)

    @attribute(dtype=float)
    def set_point_2(self):
        return self.julabo.set_point_2()

    @set_point_2.setter
    def set_point_2(self, value):
        self.julabo.set_point_2(value)

    @attribute(dtype=float)
    def set_point_3(self):
        return self.julabo.set_point_3()

    @set_point_3.setter
    def set_point_3(self, value):
        self.julabo.set_point_3(value)

    @attribute(dtype=float)
    def high_temperature_warning(self):
        return self.julabo.high_temperature_warning()

    @high_temperature_warning.setter
    def high_temperature_warning(self, value):
        self.julabo.high_temperature_warning(value)

    @attribute(dtype=float)
    def low_temperature_warning(self):
        return self.julabo.low_temperature_warning()

    @low_temperature_warning.setter
    def low_temperature_warning(self, value):
        self.julabo.low_temperature_warning(value)

    @attribute(dtype=int, min_value=1, max_value=3)
    def active_set_point_channel(self):
        return self.julabo.active_set_point_channel()

    @active_set_point_channel.setter
    def active_set_point_channel(self, value):
        self.julabo.active_set_point_channel(value)

    @attribute(dtype=str)
    def self_tunning(self):
        return self.julabo.self_tunning().name

    @self_tunning.setter
    def self_tunning(self, value):
        self.julabo.self_tunning(value)

    @attribute(dtype=str)
    def external_input(self):
        return self.julabo.external_input().name

    @external_input.setter
    def external_input(self, value):
        self.julabo.external_input(value)

    @attribute(dtype=str)
    def temperature_control(self):
        return self.julabo.temperature_control().name

    @temperature_control.setter
    def temperature_control(self, value):
        self.julabo.temperature_control(value)

    @attribute(dtype=bool)
    def is_started(self):
        return self.julabo.is_started()

    @command
    def start(self):
        self.julabo.start()

    @command
    def stop(self):
        self.julabo.stop()


class JulaboFC(BaseJulabo):

    Julabo = _JulaboFC

    @attribute(dtype=float)
    def working_temperature(self):
        return self.julabo.working_temperature()

    @working_temperature.setter
    def working_temperature(self, value):
        self.julabo.working_temperature(value)

    @attribute(dtype=int)
    def high_temperature(self):
        return self.julabo.high_temperature()

    @attribute(dtype=int)
    def low_temperature(self):
        return self.julabo.low_temperature()

    @attribute(dtype=int)
    def control_ratio(self):
        return self.julabo.control_ratio()

    @control_ratio.setter
    def control_ratio(self, value):
        self.julabo.control_ratio(value)

    @attribute(dtype=float)
    def feed_temperature(self):
        return self.julabo.feed_temperature()

    @feed_temperature.setter
    def feed_temperature(self, value):
        self.julabo.feed_temperature(value)

    @attribute(dtype=float)
    def external_temperature(self):
        return self.julabo.external_temperature()

    @attribute(dtype=float)
    def heater_capacity(self):
        return self.julabo.heater_capacity()

    @attribute(dtype=float)
    def return_temperature(self):
        return self.julabo.return_temperature()

    @attribute(dtype=float)
    def safety_temperature(self):
        return self.julabo.safety_temperature()
