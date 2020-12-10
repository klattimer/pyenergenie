# Architecture

## Overview

The basic architecture follows a plugin type system where the files in the folder
"Devices" are registered for use, devices describe themselves in such a way as they
are usable within the system without other external configuration. That is to say that
each plugin is self-contained.

Plugins are registered and are created using the DeviceFactory. Devices are registered as
usable in the DeviceRegistry Devices which exist in the registry are configured for routing
incoming messages on initialisation, devices which are routed must have classes in the
DeviceFactory's available classes.

Basic operation of PyEnergenie as a library requires first configuring how you wish to deal
with new incoming messages by defining a discovery mode, and then secondly starting the
radio receiver loop which will listen for and route incoming messages.

Interactively you can use the shell to add or remove devices from the registry. Once
configured incoming messages for registered devices are routed via the Router class
this class reads incoming messages and tries to identify where they are supposed to go
at the moment the Router only supports FSK routing of incoming messages. This is largely
due to the hardware limitations preventing both FSK and OOK listening simultaneously.
This may be avoidable by modifying radio.c to utilise the hardware functions better,
but this would require more research.

```Python
from Energenie import Energenie
...
```


## Writing plugins

Plugins expose features of a device with a get/set prefix on functions, these functions
essentially issue commands to the radio, or return results collected by the handler
upon routing incoming signals.
