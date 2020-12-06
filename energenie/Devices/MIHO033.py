from energenie.Devices.MiHomeDevice import MiHomeDevice
from energenie.Plugins import HandlerRegistry
import energenie.OpenThings as OpenThings


class MIHO033(MiHomeDevice):
    _product_id = 0x0d
    _product_name = "Door/Window Open Sensor"
    _product_description = "This allows you to monitor opening of windows and doors in your home."
    _product_rf = "FSK(tx)"
    _product_url = "https://energenie4u.co.uk/catalogue/product/MIHO033"

    """An Energenie Open Sensor"""
    def __init__(self, **kw_args):
        MiHomeDevice.__init__(self, **kw_args)

        class Readings():
            switch_state = None
        self.readings = Readings()

    def handle_message(self, payload):
        # print("MIHO033 new data %s %s" % (self.device_id, payload))
        for rec in payload["recs"]:
            paramid = rec["paramid"]
            # TODO: consider making this table driven and allowing our base class to fill our readings in for us
            # TODO: consider using @OpenThings.parameter as a decorator to the receive function
            # it will then register a handler for that message for itself as a handler
            # we still need Readings() defined too as a cache. The decorator could add
            # an entry into the cache too for us perhaps?
            if "value" in rec:
                value = rec["value"]
                if paramid == OpenThings.PARAM_DOOR_SENSOR:
                    self.readings.switch_state = ((value is True) or (value != 0))
                    HandlerRegistry.handle_reading(self.uuid, 'switch_state', self.readings.switch_state)
                else:
                    try:
                        param_name = OpenThings.param_info[paramid]['n']  # name
                    except:
                        param_name = "UNKNOWN_%s" % str(hex(paramid))
                    print("unwanted paramid: %s" % param_name)

    def get_switch_state(self) -> bool:  # -> switch:bool
        return self.readings.switch_state
