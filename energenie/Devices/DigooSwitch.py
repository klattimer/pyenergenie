from energenie.Devices.GenericSwitch import GenericSwitch


class DigooDevice(GenericSwitch):

    # Button 1: 0x01
    # Button 2: 0x02
    # Button 3: 0x04
    # Button 4: 0x08

    DEFAULT_HOUSE_ADDRESS = 0x6CC9D0
    ARM = 0x01
    DISARM = 0x02

    def __init__(self, **kw_args):
        if 'device_id' not in kw_args.keys() or kw_args['device_id'] is None:
            kw_args['device_id'] = (DigooDevice.DEFAULT_HOUSE_ADDRESS, DigooDevice.ARM, DigooDevice.DISARM)
        elif type(kw_args['device_id']) == int:
            kw_args['device_id'] = (DigooDevice.DEFAULT_HOUSE_ADDRESS, DigooDevice.ARM, DigooDevice.DISARM)
        elif type(kw_args['device_id']) == tuple and kw_args['device_id'][0] is None:
            kw_args['device_id'] = (DigooDevice.DEFAULT_HOUSE_ADDRESS, kw_args['device_id'][1], kw_args['device_id'][2])

        DigooDevice.__init__(self, **kw_args)

    def __repr__(self):
        return "DigooDevice(%s)" % str(self.device_id)
