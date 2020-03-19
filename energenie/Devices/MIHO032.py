from Devices.MiHomeDevice import MiHomeDevice
import OpenThings


class MIHO032(MiHomeDevice):
    _product_id = 0x0c
    _product_name = "Motion Sensor"
    _product_description = "This allows you to monitor movement in your home."
    _product_rf = "FSK(tx)"
    _product_url = "https://energenie4u.co.uk/catalogue/product/MIHO032"

    """An Energenie Motion Sensor"""
    def __init__(self, name=None, device_id=None):
        MiHomeDevice.__init__(self, name, device_id)

        class Readings():
            switch_state = None
            battery_alarm = None
        self.readings = Readings()
        self.capabilities.send = True
        self.callback = None

    def __repr__(self):
        return "MIHO032(%s)" % str(hex(self.device_id))

    def setCallback(self, callback):
        self.callback = callback

    def handle_message(self, payload):
        # print("MIHO032 new data %s %s" % (self.device_id, payload))
        # sys.stdout.flush()
        for rec in payload["recs"]:
            paramid = rec["paramid"]
            # TODO: consider making this table driven and allowing our base class to fill our readings in for us
            # TODO: consider using @OpenThings.parameter as a decorator to the receive function
            # it will then register a handler for that message for itself as a handler
            # we still need Readings() defined too as a cache. The decorator could add
            # an entry into the cache too for us perhaps?
            if "value" in rec:
                value = rec["value"]
                if paramid == OpenThings.PARAM_MOTION_DETECTOR:
                    state = ((value is True) or (value != 0))
                    if self.readings.switch_state != state:
                        self.readings.switch_state = state
                        # print("MIHO032 new data %s %s" % (self.device_id, payload))
                        if self.callback is not None:
                            self.callback(self, state)
                elif paramid == OpenThings.PARAM_ALARM:
                    if value == 0x42:  # battery alarming
                        self.readings.battery_alarm = True
                    elif value == 0x62:  # battery not alarming
                        self.readings.battery_alarm = False
                else:
                    try:
                        param_name = OpenThings.param_info[paramid]['n']  # name
                    except:
                        param_name = "UNKNOWN_%s" % str(hex(paramid))
                    print("unwanted paramid: %s" % param_name)

    def get_switch_state(self):  # -> switch:bool
        return self.readings.switch_state

    def get_battery_alarm(self):  # -> alarm:bool
        return self.readings.battery_alarm
