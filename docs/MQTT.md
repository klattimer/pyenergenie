
# MQTT configuration and usage

PyEnergenie offers MQTT integration. For this to work you will need an MQTT server which you can publish messages to
and subscribe to topics.

## Configuration

You'll need to add a handler, either in the handlers interactive console, or in the config.json file
the typical Mosquitto configuration looks like this:

    ```
    "handlers": {
        "MosquittoServer": {
            "type": "MQTTHandler",
            "host": "192.168.1.3",
            "port": 1883,
            "username": "myuser",
            "password": "secret",
            "topic_prefix": "energenie",
            "enabled": true
        }
    }
    ```
Multiple MQTT servers can be configured, all of them will be updated in the same loop. The specified port, and
topic_prefix are defaults and can be safely omitted if no adjustment is required.

## MQTT topics

PyEnergenie will set all of the available defaults for each device based on the topic pattern:

    ```<topic_prefix>/<device.location>/<device.uuid>/<reading/state>```

Different devices expose different features, using an MQTT debugging tool like MQTT explorer is
recommended.

Setting the topic on a settable feature will cause the radio to broadcast the message at the appropriate
time, this may be immediately or open incoming message receipt depending on the device features.
