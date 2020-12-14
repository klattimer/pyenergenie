# pyenergenie

A python interface to energenie and OpenThings products designed for RaspberryPi.
Using either the ENER314-RT or homebrew hardware with the RFM69HCW.

This project is a fork - refactor and redesign of the software originally provided by
energenie. [https://github.com/Energenie/pyenergenie] I've pulled additional features
from a variety of other forks and am willing to accept patches and pull requests.

## Features

 - Completely rewritten device registry
 - Completely rewritten device factory & plugin system
 - Introduced new "Handlers" factory and registry for handling events/changes
     - MQTT integration
     - Websocket service
 - Flask webserver for polling status and device metadata
 - Supports almost every energenie branded device.
    - MiHome range of lights and sockets
    - Energy monitors
    - eTRV valves

## Get involved

We need help testing devices and adding support for devices such as double sockets
and other devices we don't own.

## Usage

```
python3 setup.py install
pyenergenie
```

The default command will provide help, from there you can choose interactive mode
or just issue commands via the command line to get started.

pyenergenie is best run in daemon mode with an MQTT handler configured, this
allows for the lowest latency of interaction.

Configuration can be performed interactively, via the command line, or editing the
json file directly. Examples are included in the docs folder.

## Limitations

It's currently impossible to listen in OOK and FSK mode simultaneously, the solution to
this is to add an RTL SDR device to the system via an available USB port, which is planned
in some way along the line.

## Future support


### Full transmit/receive support OOK/FSK

Transmitting OOK messages shouldn't be limited to the Energenie product range. The project
pilight which seems almost abandoned provides support for many more types of remote control.

In some way providing the raw transmit/receive functionality of the pilight via drv/radio.c
seems to be a great option for expanding the capabilities. Along with using rtl 433 for the listen
mode it would make PyEnergenie a pretty decent way to bridge the 433/IoT gap.

### Training and learning

The user experience for the interaction with devices is clunky, in order to bridge this the missing
feature is being able to learn codes from installed transmitters. Then to use these codes, applying them
to the receivers would be ideal.

## Contributions

We welcome any contributions, currently the following areas need some work.

 - support for dimmable switches
 - support for double light switches and sockets
 - Populating the device templates which are currently missing (check the Devices/*.py files)
 - Testing devices which haven't been fully tested
 - Testing anything and everything
 - Porting the pilight transmit/rececive for raw codes so we can add learning capabilities
 - Fixing the build scripts such that it will build for raspberry pi 1 and raspberry pi 2+
   without requiring editing the gpio base.
 - Fixing the setup.py such that it executes the drv/build_rpi on raspberry pi and build_mac on mac
 - Adding a build_win for windows builds (some brave windows dev can handle that if they like)
 - Authentication and authorisation of some kind, read/write groups

## Site Index
- [Architecture](docs/Architecture.md)
- [MQTT integration](docs/MQTT.md)
- [WebSocket integration](docs/WebSockets.md)
- [REST API documentation](docs/API.md)
- [Hardware](docs/RFM69.md)
