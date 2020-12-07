from energenie.Devices.MiHomeDevice import MiHomeDevice
from energenie.Handlers import HandlerRegistry
import energenie.OpenThings as OpenThings


class MIHO006(MiHomeDevice):
    _product_id = 0x05
    _product_name = "Whole house monitor"
    _product_description = "This allows you to monitor the power and energy usage of your entire home."
    _product_rf = "FSK(tx)"
    _product_url = "https://energenie4u.co.uk/catalogue/product/MIHO006"

    """An Energenie MiHome Home Monitor"""
    def __init__(self, **kw_args):
        MiHomeDevice.__init__(self, **kw_args)

        class Readings():
            battery_voltage = None
            current         = None
            apparent_power  = None
        self.readings = Readings()

    def handle_message(self, payload):
        for rec in payload["recs"]:
            paramid = rec["paramid"]
            # TODO: consider making this table driven and allowing our base class to fill our readings in for us
            # TODO: consider using @OpenThings.parameter as a decorator to the receive function
            # it will then register a handler for that message for itself as a handler
            # we still need Readings() defined too as a cache. The decorator could add
            # an entry into the cache too for us perhaps?
            if "value" in rec:
                value = rec["value"]
                if paramid == OpenThings.PARAM_VOLTAGE:
                    self.readings.battery_voltage = value
                    HandlerRegistry.handle_reading(self.uuid, 'battery_voltage', value)
                elif paramid == OpenThings.PARAM_CURRENT:
                    self.readings.current = value
                    HandlerRegistry.handle_reading(self.uuid, 'current', value)
                elif paramid == OpenThings.PARAM_APPARENT_POWER:
                    self.readings.apparent_power = value
                    HandlerRegistry.handle_reading(self.uuid, 'apparent_power', value)
                else:
                    try:
                        param_name = OpenThings.param_info[paramid]['n']  # name
                    except:
                        param_name = "UNKNOWN_%s" % str(hex(paramid))
                    print("unwanted paramid: %s" % param_name)
        pass

    def get_battery_voltage(self) -> float:  # -> voltage:float
        return self.readings.battery_voltage

    def get_current(self) -> float:  # -> current:float
        return self.readings.current

    def get_apparent_power(self) -> float:  # -> power:float
        return self.readings.apparent_power
