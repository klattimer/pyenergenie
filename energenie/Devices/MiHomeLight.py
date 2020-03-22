from energenie.Devices.LegacyDevice import LegacyDevice


class MiHomeLight(LegacyDevice):
    """Base for all MiHomeLight variants. Receive only OOK device"""
    def __init__(self, name=None, device_id=None, enabled=True):
        LegacyDevice.__init__(self, name, device_id, enabled=True)
        self.radio_config.inner_times = 75
        self.capabilities.switch = True
        self.capabilities.receive = True

    def __repr__(self):
        return "MiHomeLight(%s,%s)" % (str(hex(self.device_id[0])), str(hex(self.device_id[1])))

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
