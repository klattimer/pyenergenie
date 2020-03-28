from energenie.Devices import Device


class EnergenieDevice(Device):
    _manufacturer_id = 0x04
    _broadcast_id = 0xFFFFFF

    """An abstraction for any kind of Energenie connected device"""
    def __init__(self, **kw_args):
        Device.__init__(self, **kw_args)

    def __repr__(self):
        return "EnergenieDevice(%s)" % str(self.device_id)
