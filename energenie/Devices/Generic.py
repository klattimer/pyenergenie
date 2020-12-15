from energenie.Devices import Device


class Generic(Device):
    DEFAULT_HOUSE_ADDRESS = 0x6CC9D0
    _product_rf = "EV1527(rx)"

    def __init__(self, **kw_args):
        if 'device_id' not in kw_args.keys() or kw_args['device_id'] is None:
            kw_args['device_id'] = (Generic.DEFAULT_HOUSE_ADDRESS, 1)
        elif type(kw_args['device_id']) == int:
            kw_args['device_id'] = (Generic.DEFAULT_HOUSE_ADDRESS, kw_args['device_id'])
        elif type(kw_args['device_id']) == tuple and kw_args['device_id'][0] is None:
            kw_args['device_id'] = (Generic.DEFAULT_HOUSE_ADDRESS, kw_args['device_id'][1])
        Device.__init__(self, **kw_args)

    def __repr__(self):
        return "Generic(%s)" % str(self.device_id)

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
