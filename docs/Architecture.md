# Architecture

## Overview

## The Threads

The Energenie class operates in it's own thread, receiving input from the SPI device and triggering
the appropriate functions. The WebSocket Handler operates in it's own thread using asyncio and the MQTT
Handler operates a thread for subscriptions. To top it all off the flask webserver has to operate in a thread
too which doesn't make flask too happy and therefore auto-reload is disabled.

The main thread is blocked by either the command loop or the iterative loop holding the application running.

## Devices

The basic device driver architecture follows a plugin type system where the files in the folder
"Devices" are registered for use, devices describe themselves in such a way as they
are usable within the system without other external configuration. That is to say that
each plugin is self-contained.

Plugins are registered and are created using the DeviceFactory. Devices are registered as
usable in the DeviceRegistry Devices which exist in the registry are configured for routing
incoming messages on initialisation, devices which are routed must have classes in the
DeviceFactory's available classes.

### Development guidelines

A plugin must inherit from either ```Device``` or a subclass, and can provide the following information
used to classify it:

```
_product_id = None
_product_name = None
_product_description = None
_product_rf = None
_product_url = None
_product_user_guide = None
```

_product_id relates to the OpenThings product ID.

_product_rf must be in the format of ```<AIR_INTERFACE_TYPE>(tx, rx)``` for instance:

```FSK(tx)```
```FSK(tx, rx)```
```OOK(rx)```

A minimal implementation would only need to specify some of the information above in order
to be operable. For instance an OOK switch is provided with the address information during
configuration, and therefore only requires a template describing the device in physical terms.

More complex devices will require implementation of getter and setter functions in order to
expose these values to the available interfaces. An example of a deeper implementation of a
device can be fount in Devices/MIHO013.py which operates eTRV radiator valves.

Essentially subclasses should look to implement the following methods:
```
def handle_message(self, payload):
def get_*(self):
def set_*(self, value):
```


## Handlers

Handlers are based on a plugin system much like Devices and can be designed to use a minimal
set of the Handler base class features.

### Development guidelines
