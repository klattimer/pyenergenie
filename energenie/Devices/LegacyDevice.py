from energenie.Devices.EnergenieDevice import EnergenieDevice


class LegacyDevice(EnergenieDevice):
    DEFAULT_HOUSE_ADDRESS = 0x6C6C6

    """An abstraction for Energenie green button legacy OOK devices"""
    def __init__(self, **kw_args):
        if 'device_id' not in kw_args.keys() or kw_args['device_id'] is None:
            kw_args['device_id'] = (LegacyDevice.DEFAULT_HOUSE_ADDRESS, 1)
        elif type(kw_args['device_id']) == int:
            kw_args['device_id'] = (LegacyDevice.DEFAULT_HOUSE_ADDRESS, kw_args['device_id'])
        elif type(kw_args['device_id']) == tuple and kw_args['device_id'][0] is None:
            kw_args['device_id'] = (LegacyDevice.DEFAULT_HOUSE_ADDRESS, kw_args['device_id'][1])
        EnergenieDevice.__init__(self, **kw_args)
        # TODO: These are now just be implied by the ook_interface adaptor
        # self.radio_config.frequency  = 433.92
        # self.radio_config.modulation = "OOK"
        # self.radio_config.codec      = "4bit"

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, str(self.device_id))

    def send_message(self, payload):
        if self.air_interface is not None:
            self.air_interface.send(payload, radio_config=self.radio_config)
        else:
            d = self.device_id
            print("send_message(mock[%s]):%s" % (str(d), payload))
