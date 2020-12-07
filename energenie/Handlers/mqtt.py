from energenie.Handlers import Handler
from energenie import Registry


class MQTTHandler(Handler):
    _protocol = 'mqtt'
    _description = 'Mosquitto Handler'
    _args = {
        'host': 'str',
        'port': 'int',
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

        self.username = kw_args.get('username')
        self.password = kw_args.get('password')
        self.host = kw_args.get('host')
        self.port = kw_args.get('port')
        self.topic_prefix = kw_args.get('topic_prefix')

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
            'host': self.host,
            'username': self.username,
            'password': self.password,
            'port': self.port,
            'topic_prefix': self.topic_prefix
        })
        return data

    def handle_reading(self, device, key, value):
        # Set the MQTT Topic for this device/key = value
        pass
