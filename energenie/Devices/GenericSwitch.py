from energenie.Devices.Generic import Generic


class GenericSwitch(Generic):
    def __init__(self, **kw_args):
        Generic.__init__(self, **kw_args)
        self.state = None

    def __repr__(self):
        return "GenericRemoteSwitch(%s)" % str(self.device_id)

    def turn_on(self):
        # TODO: should this be here, or in LegacyDevice??
        # addressing should probably be in LegacyDevice
        # child devices might interpret the command differently
        payload = {
            "house_address": self.device_id[0],
            "cmd": self.device_id[1],
        }
        self.state = True
        self.send_message(payload)

    def turn_off(self):
        # TODO: should this be here, or in LegacyDevice???
        # addressing should probably be in LegacyDevice
        # child devices might interpret the command differently
        payload = {
            "house_address": self.device_id[0],
            "cmd": self.device_id[2],
        }
        self.state = False
        self.send_message(payload)

    def set_switch_state(self, state: bool):
        if state is True:
            self.turn_on()
        else:
            self.turn_off()

    def get_switch_state(self) -> bool:
        return self.state
