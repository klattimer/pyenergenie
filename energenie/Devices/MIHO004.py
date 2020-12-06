from energenie.Devices.MiHomeDevice import MiHomeDevice
from energenie.Plugins import HandlerRegistry
import energenie.OpenThings as OpenThings


class MIHO004(MiHomeDevice):
    _product_id = 0x01
    _product_name = "Socket Monitor adaptor"
    _description = "The Monitor adapter allows you to monitor the power being used by an attached appliance."
    _product_rf = "FSK(tx)"
    _product_url = "https://energenie4u.co.uk/catalogue/product/MIHO004"

    """Energenie Monitor-only Adaptor"""
    def __init__(self, **kw_args):
        MiHomeDevice.__init__(self, **kw_args)

        class Readings():
            voltage        = None
            frequency      = None
            current        = None
            apparent_power = None
            reactive_power = None
            real_power     = None
        self.readings = Readings()
        self.radio_config.inner_times = 4

    @staticmethod
    def get_join_req(deviceid):
        """Get a synthetic join request from this device, for testing"""
        return MiHomeDevice.get_join_req(MIHO004._manufacturer_id, MIHO004._product_id, deviceid)

    def handle_message(self, payload):
        # print("MIHO005 new data %s %s" % (self.device_id, payload))
        for rec in payload["recs"]:
            paramid = rec["paramid"]
            # TODO: consider making this table driven and allowing our base class to fill our readings in for us
            #  then just define the mapping table in __init__ (i.e. paramid->Readings field name)
            value = rec["value"]
            if paramid == OpenThings.PARAM_VOLTAGE:
                self.readings.voltage = value
                HandlerRegistry.handle_reading(self.uuid, 'voltage', value)
            elif paramid == OpenThings.PARAM_CURRENT:
                self.readings.current = value
                HandlerRegistry.handle_reading(self.uuid, 'current', value)
            elif paramid == OpenThings.PARAM_REAL_POWER:
                self.readings.real_power = value
                HandlerRegistry.handle_reading(self.uuid, 'real_power', value)
            elif paramid == OpenThings.PARAM_APPARENT_POWER:
                self.readings.apparent_power = value
                HandlerRegistry.handle_reading(self.uuid, 'apparent_power', value)
            elif paramid == OpenThings.PARAM_REACTIVE_POWER:
                self.readings.reactive_power = value
                HandlerRegistry.handle_reading(self.uuid, 'reactive_power', value)
            elif paramid == OpenThings.PARAM_FREQUENCY:
                self.readings.frequency = value
                HandlerRegistry.handle_reading(self.uuid, 'frequency', value)
            else:
                try:
                    param_name = OpenThings.param_info[paramid]['n']  # name
                except:
                    param_name = "UNKNOWN_%s" % str(hex(paramid))
                print("unwanted paramid: %s" % param_name)

    def get_voltage(self) -> float:  # -> voltage:float
        """Last stored state of voltage reading, None if unknown"""
        if self.readings.voltage is None:
            raise RuntimeError("No voltage reading received yet")
        return self.readings.voltage

    def get_frequency(self) -> float:  # -> frequency:float
        """Last stored state of frequency reading, None if unknown"""
        if self.readings.frequency is None:
            raise RuntimeError("No frequency reading received yet")
        return self.readings.frequency

    def get_current(self) -> float:  # ->power:float
        """Last stored state of current reading, None if unknown"""
        if self.readings.apparent_power is None:
            raise RuntimeError("No current reading received yet")
        return self.readings.apparent_power

    def get_apparent_power(self) -> float:  # ->power:float
        """Last stored state of apparent power reading, None if unknown"""
        if self.readings.apparent_power is None:
            raise RuntimeError("No apparent power reading received yet")
        return self.readings.apparent_power

    def get_reactive_power(self) -> float:  # -> power:float
        """Last stored state of reactive power reading, None if unknown"""
        if self.readings.reactive_power is None:
            raise RuntimeError("No reactive power reading received yet")
        return self.readings.reactive_power

    def get_real_power(self) -> float:  # -> power:float
        """Last stored state of real power reading, None if unknown"""
        if self.readings.real_power is None:
            raise RuntimeError("No real power reading received yet")
        return self.readings.real_power
