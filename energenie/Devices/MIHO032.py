from energenie.Devices.MiHomeDevice import MiHomeDevice
from energenie.Handlers import HandlerRegistry
import energenie.OpenThings as OpenThings


class MIHO032(MiHomeDevice):
    _product_id = 0x0c
    _product_name = "Motion Sensor"
    _product_description = "This allows you to monitor movement in your home."
    _product_rf = "FSK(tx)"
    _product_url = "https://energenie4u.co.uk/catalogue/product/MIHO032"
    _product_user_guide = "https://energenie4u.co.uk/res/pdfs/MIHO032-Motion-Sensor-User-Guide-v1.3-outlines.pdf"
    _product_image_url = "https://energenie4u.co.uk/res/images/products/large/MIHO032%20WEBSITE.jpg"

    """An Energenie Motion Sensor"""
    def __init__(self, **kw_args):
        MiHomeDevice.__init__(self, **kw_args)

        class Readings():
            switch_state = None
            battery_alarm = None
        self.readings = Readings()
        self.callback = None

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
                        HandlerRegistry.handle_reading(self.uuid, 'switch_state', state)
                        # print("MIHO032 new data %s %s" % (self.device_id, payload))
                        if self.callback is not None:
                            self.callback(self, state)
                elif paramid == OpenThings.PARAM_ALARM:
                    if value == 0x42:  # battery alarming
                        self.readings.battery_alarm = True
                        HandlerRegistry.handle_reading(self.uuid, 'battery_alarm', True)
                    elif value == 0x62:  # battery not alarming
                        self.readings.battery_alarm = False
                        HandlerRegistry.handle_reading(self.uuid, 'battery_alarm', False)
                else:
                    try:
                        param_name = OpenThings.param_info[paramid]['n']  # name
                    except:
                        param_name = "UNKNOWN_%s" % str(hex(paramid))
                    print("unwanted paramid: %s" % param_name)

    def get_switch_state(self) -> bool:  # -> switch:bool
        return self.readings.switch_state

    def get_battery_alarm(self) -> bool:  # -> alarm:bool
        return self.readings.battery_alarm
