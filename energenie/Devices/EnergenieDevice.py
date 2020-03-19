from Devices import Device


class EnergenieDevice(Device):
    _manufacturer_id = 0x04
    _broadcast_id = 0xFFFFFF

    """An abstraction for any kind of Energenie connected device"""
    def __init__(self, name=None, device_id=None):
        Device.__init__(self, name, device_id)

    def get_device_id(self):  # -> id:int
        return self.device_id

    def __repr__(self):
        return "EnergenieDevice(%s)" % str(self.device_id)
