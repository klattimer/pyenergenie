from energenie.Plugins import Handler
from energenie import Registry


class MQTTHandler(Handler):
    _protocol = 'mqtt'
    _description = 'Mosquitto Handler'
    _args = {
        'host': 'str',
        'username': 'str',
        'password': 'str',
        'topic_prefix': 'str'
    }

    @classmethod
    def describe(cls):
        return {
            'protocol': cls._protocol,
            'description': cls._description,
            'args': cls._args
        }

    def __init__(self, **kw_args):
        super.__init__(self, **kw_args)

        reg = Registry.DeviceRegistry.singleton()

        for d in reg.list():
            device = reg[d]
            features = device.feature()
            for f in features.keys():
                if 'set' in features[f]:
                    # Subscribe to setter topic, retrieve the current value
                    pass

                if 'get' in features[f]:
                    # Create the MQTT topic and push the current value
                    pass

        # Subscribe to relevant topics
        # i.e. any device which is rx and has setters
        # Get the current published state of the devices
        # Set the device states according to the MQTT values, if setters exist for the values
        # Publish information about this system
        # - IP address
        # - Available handlers 
        # - Supported devices
        pass

    def serialise(self):
        data = super.serialise()
        data.update({
            'type': self.__class__.__name__,
            'host': self.host,
            'username': self.username,
            'password': self.password
        })
        return data

    def handle_reading(self, device, key, value):
        # Set the MQTT Topic for this device/key = value
        pass
