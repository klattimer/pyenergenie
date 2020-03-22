from energenie.Devices.MiHomeDevice import MiHomeDevice
import energenie.OpenThings as OpenThings


class MIHO006(MiHomeDevice):
    _product_id = 0x05
    _product_name = "Whole house monitor"
    _product_description = "This allows you to monitor the power and energy usage of your entire home."
    _product_rf = "FSK(rx)"
    _product_url = "https://energenie4u.co.uk/catalogue/product/MIHO006"

    """An Energenie MiHome Home Monitor"""
    def __init__(self, name=None, device_id=None, enabled=True):
        MiHomeDevice.__init__(self, name, device_id, enabled)

        class Readings():
            battery_voltage = None
            current         = None
            apparent_power  = None
        self.readings = Readings()

        self.capabilities.send = True

    def __repr__(self):
        return "MIHO006(%s)" % str(hex(self.device_id))

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
                elif paramid == OpenThings.PARAM_CURRENT:
                    self.readings.current = value
                elif paramid == OpenThings.PARAM_APPARENT_POWER:
                    self.readings.apparent_power = value
                else:
                    try:
                        param_name = OpenThings.param_info[paramid]['n']  # name
                    except:
                        param_name = "UNKNOWN_%s" % str(hex(paramid))
                    print("unwanted paramid: %s" % param_name)
        pass

    def get_battery_voltage(self):  # -> voltage:float
        return self.readings.battery_voltage

    def get_current(self):  # -> current:float
        return self.readings.current

    def get_apparent_power(self):  # -> power:float
        return self.readings.apparent_power
