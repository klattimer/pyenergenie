from energenie.Handlers import Handler
from energenie import Registry
import paho.mqtt.client as mqtt
import logging
import time


class MQTTHandler(Handler):
    protocol = 'mqtt'
    description = 'Mosquitto Handler'
    args = {
        'host': {
            'type': 'str',
            'prompt': 'Hostname or IP Address'
        },
        'port': {
            'type': 'int',
            'prompt': 'Port number (default: 1883)',
            'default': 1883
        },
        'username': {
            'type': 'str',
            'prompt': 'Username if required'
        },
        'password': {
            'type': 'str',
            'prompt': 'Password'
        },
        'topic_prefix': {
            'type': 'str',
            'prompt': 'Topic Prefix (default: energenie)',
            'default': 'energenie'
        }
    }

    def __init__(self, **kw_args):
        super(MQTTHandler, self).__init__(**kw_args)

        self.registry = Registry.DeviceRegistry.singleton()

        self.username = kw_args.get('username')
        self.password = kw_args.get('password')
        self.host = kw_args.get('host')
        self.port = kw_args.get('port')
        self.topic_prefix = kw_args.get('topic_prefix')

        self.client = mqtt.Client()
        self.client.username_pw_set(self.username, self.password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(self.host, self.port, 60)
        self.client.loop_start()

        for d in self.registry.list():
            device = self.registry.get(d)
            topic = '/'.join([self.topic_prefix, device.location if device.location else "default", device.uuid, "name"])
            self.client.publish(topic, device.name)
            topic = '/'.join([self.topic_prefix, device.location if device.location else "default", device.uuid, "type"])
            self.client.publish(topic, device.__class__.__name__)
            topic = '/'.join([self.topic_prefix, device.location if device.location else "default", device.uuid, "id"])
            self.client.publish(topic, device.device_id)

            features = device.features()
            for f in features.keys():
                topic = '/'.join([self.topic_prefix, device.location if device.location else "default", device.uuid, f])
                if 'get' in features[f]:
                    # Create the MQTT topic and push the current value
                    value = getattr(device, 'get_' + f)()
                    logging.debug(f"Initialising MQTT topic {topic} value: {value}")
                    self.client.publish(topic, value)
                elif 'set' in features[f]:
                    self.client.publish(topic, False)

                if 'set' in features[f]:
                    # Subscribe to setter topic, retrieve the current value
                    logging.debug(f"Subscribing to MQTT topic {topic}")
                    self.client.subscribe(topic)

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

    def on_connect(self, client, userdata, flags, rc):
        logging.debug("Connected to mqtt server %s with result code %s" % (self.host, str(rc)))
        client.subscribe("$SYS/#")

    def on_message(self, client, userdata, msg):
        value = msg.payload.decode()
        topic = msg.topic
        try:
            _, topic_prefix, device, key = topic.split('/')
        except:
            return

        if topic_prefix != self.topic_prefix:
            return

        logging.debug("Received set on mqtt for %s, %s = %s" % (device, key, str(value)))
        self.set(device, key, value)

    def handle_reading(self, device, key, value):
        # Set the MQTT Topic for this device/key = value
        device = self.registry.get(device)
        topic = '/'.join([self.topic_prefix, device.location if device.location else "default", device.uuid, key])
        result = self.client.publish(topic, value)

        status = result[0]
        if status != 0:
            logging.error(f"Failed to send message to topic {topic}")

    def device_detected(self, device):
        pass

    def device_added(self, device):
        topic = '/'.join([self.topic_prefix, device.location if device.location else "default", device.uuid, "name"])
        self.client.publish(topic, device.name)
        topic = '/'.join([self.topic_prefix, device.location if device.location else "default", device.uuid, "type"])
        self.client.publish(topic, device.__class__.__name__)
        topic = '/'.join([self.topic_prefix, device.location if device.location else "default", device.uuid, "id"])
        self.client.publish(topic, device.device_id)

    def device_removed(self, device):
        topic = '/'.join([self.topic_prefix, device.location if device.location else "default", device.uuid, "removed_on"])
        self.client.publish(topic, time.time())

    def ask(self):
        pass
