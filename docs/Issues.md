# Issues

I've chosen to inherit this code in an absolute mess, a single devices file with all devices supported in there but obviously no index of supported devices other than in code, blocks of pre-defined code for lookup tables and metadata and a snow balls chance in hell of passing a basic lint...

So I'm basically rewriting the project and heres a quick list of what needs to be done

- Make it work as a proper python library **IN PROGRESS**
- Replace KVS with JSON based configuration file **DONE**
- Replace the Logger class with logging
- Separate devices out into a plugins folder **DONE**
- Refactor classes so they "own" the knowledge about themselves. **DONE**
- Strip back any useless code **DONE**
- Refactor device registry and related **IN PROGRESS**
  - Need to save the current state of the device registry
- Passing "air_interface" around appears completely useless **FIXED**
- Develop command line tool & daemon
- Fix lint issues top to bottom **DONE**
- Develop hardware guides, if someone wants to use a raspi keep the cost down to the hoperf module.
- Redesign tests
- 

### Add support for MQQT reporting

- Each device has each property exposed as an MQTT path
- Each device property which effects an output begins a subscription for those paths

## Command line utility

- Mode that allows the tool to be used to discover devices and
  appropriately configure them
- Mode that runs as a daemon, the daemon simply captures the events and sends
  signals based on MQTT paths
- Mode which dumps live JSON representation of the signal received
-

## Wishlist

- Can we integrate or replace pilight functionality? pilight seems mostly abandoned now anyway, so it make sense to try and capture some functionality here. I think openthings has an overlap.
- Can we integrate with rtl_433 or maybe just rtlsdr directly?
- Fix up radio support so we can support multiple frequency HOPERF, and maybe
  even other module types.
    - Radio also requires having pin setting done properly