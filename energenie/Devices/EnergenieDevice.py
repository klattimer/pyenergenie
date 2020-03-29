from energenie.Devices import Device


class EnergenieDevice(Device):
    _manufacturer_id = 0x04
    _broadcast_id = 0xFFFFFF

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, str(self.device_id))
