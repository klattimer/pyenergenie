from energenie.Devices.EnergenieDevice import EnergenieDevice


class LegacyDevice(EnergenieDevice):
    DEFAULT_HOUSE_ADDRESS = 0x6C6C6

    """An abstraction for Energenie green button legacy OOK devices"""
    def __init__(self, name=None, device_id=None):
        if device_id is None:
            device_id = (LegacyDevice.DEFAULT_HOUSE_ADDRESS, 1)
        elif type(device_id) == int:
            device_id = (LegacyDevice.DEFAULT_HOUSE_ADDRESS, device_id)
        elif type(device_id) == tuple and device_id[0] is None:
            device_id = (LegacyDevice.DEFAULT_HOUSE_ADDRESS, device_id[1])

        EnergenieDevice.__init__(self, name, device_id)
        # TODO: These are now just be implied by the ook_interface adaptor
        # self.radio_config.frequency  = 433.92
        # self.radio_config.modulation = "OOK"
        # self.radio_config.codec      = "4bit"

    def __repr__(self):
        return "LegacyDevice(%s)" % str(self.device_id)

    def get_config(self):
        """Get the persistable config, enough to reconstruct this class from a factory"""
        return {
            "type": self.__class__.__name__,
            "device_id": self.device_id
        }

    def send_message(self, payload):
        if self.air_interface is not None:
            self.air_interface.send(payload, radio_config=self.radio_config)
        else:
            d = self.device_id
            print("send_message(mock[%s]):%s" % (str(d), payload))
