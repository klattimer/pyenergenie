from energenie.Devices.LegacyDevice import LegacyDevice


class OOKSwitch(LegacyDevice):
    _product_name = "OOKSwitch"
    _product_rf = "OOK()"

    """Any OOK controlled switch"""
    def __init__(self, name=None, device_id=None):
        LegacyDevice.__init__(self, name, device_id)
        self.radio_config.inner_times = 8
        self.capabilities.switch = True
        self.capabilities.receive = True

    def __repr__(self):
        return "OOKSwitch(%s,%s)" % (str(hex(self.device_id[0])), str(hex(self.device_id[1])))

    def turn_on(self):
        # TODO: should this be here, or in LegacyDevice??
        # addressing should probably be in LegacyDevice
        # child devices might interpret the command differently
        payload = {
            "house_address": self.device_id[0],
            "device_index": self.device_id[1],
            "on": True
        }
        self.send_message(payload)

    def turn_off(self):
        # TODO: should this be here, or in LegacyDevice???
        # addressing should probably be in LegacyDevice
        # child devices might interpret the command differently
        payload = {
            "house_address": self.device_id[0],
            "device_index": self.device_id[1],
            "on": False
        }
        self.send_message(payload)

    def set_switch(self, state):
        if state:
            self.turn_on()
        else:
            self.turn_off()
