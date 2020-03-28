from energenie.Devices.LegacyDevice import LegacyDevice


class OOKSwitch(LegacyDevice):
    _product_name = "OOKSwitch"
    _product_rf = "OOK()"

    """Any OOK controlled switch"""
    def __init__(self, **kw_args):
        LegacyDevice.__init__(self, **kw_args)
        self.radio_config.inner_times = 8
        self.state = None

    def __repr__(self):
        return "%s(%s,%s)" % (self.__class__.__name__, str(hex(self.device_id[0])), str(hex(self.device_id[1])))

    def turn_on(self):
        # TODO: should this be here, or in LegacyDevice??
        # addressing should probably be in LegacyDevice
        # child devices might interpret the command differently
        payload = {
            "house_address": self.device_id[0],
            "device_index": self.device_id[1],
            "on": True
        }
        self.state = True
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
        self.state = False
        self.send_message(payload)

    def set_switch_state(self, state: boolean):
        if state is True:
            self.turn_on()
        else:
            self.turn_off()

    def get_switch_state(self) -> float:
        return self.state
