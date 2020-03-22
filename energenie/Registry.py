# Registry.py  14/05/2016  D.J.Whale
#
# A simple registry of connected devices.
#
# NOTE: This is an initial, non persisted implementation only

import os
import json

from copy import copy
from . import Devices
from energenie.Devices.MiHomeDevice import MiHomeDevice
from . import OpenThings


search_config = [
    "/etc/pyenergenie/config.json",
    "/opt/venvs/pyenergenie/config/config.json",
    "~/.pyenergenie/config.json",

    # This is for testing only
    "data/config.json"
]


def find_config(writable=False):
    # We check for writable paths in reverse, so user paths can over-ride
    # system wide paths. Strictly this isn't necessary because only root
    # can run this...
    if writable is True:
        paths = copy(search_config)
        paths.reverse()
    else:
        paths = copy(search_config)

    for f in paths:
        f = os.path.expanduser(f)
        f = os.path.abspath(f)
        if os.path.exists(f):
            if writable is False:
                return f

        d = os.path.dirname(f)
        if os.path.exists(d):
            if writable is True and os.access(d, os.W_OK):
                return f
        elif writable is True and os.access(os.path.dirname(d), os.W_OK):
            os.makedirs(d)
            return f
    print ("Cannot find suitable config path to write, create one in %s" % ' or '.join(search_config))
    raise Exception("No config file")


# ----- NEW DEVICE REGISTRY ----------------------------------------------------

# Done as a class, so we can have multiple registries if we want.

class DeviceRegistry():  # this is actions, so is this the 'RegistRAR'??
    """A persistent registry for device class instance configurations"""

    def __init__(self):
        # # print("***Opening DeviceRegistry")
        config_path = find_config()
        self.devices = {}
        self.fsk_router = Router("fsk")

        # OOK receive not yet written
        # It will be used to be able to learn codes from Energenie legacy hand remotes
        self.ook_router = None  # Router("ook")
        self.config = {}
        self.load_from(config_path)

    def set_fsk_router(self, fsk_router):
        self.fsk_router = fsk_router

    def load_from(self, filename=None):
        """Start with a blank in memory registry, and load from the given filename"""
        with open(filename) as f:
            self.config = json.loads(f.read())
            for device in self.config['devices']:

                device_type = device['type']
                device_name = device['name']

                del device['type']
                del device['name']

                d = Devices.DeviceFactory.get_device_from_name(device_type, **device)
                self.devices[device_name] = d
                # TODO: Add enable/disable methods
                if device['enabled'] is not True:
                    continue
                self.setup_device_routing(d)

    def update_config(self):
        devices = []
        for device in self.devices.values():
            devices.append(device.serialise())
        self.config['devices'] = devices
        config_path = find_config(True)
        with open(config_path, 'wt') as f:
            f.write(json.dumps(self.config, indent=4, sort_keys=True))
        print('Saved configuration in %s' % config_path)

    def load_into(self, context):
        """auto-create variables in the provided context, for all persisted registry entries"""
        if context is None:
            raise ValueError("Must provide a context to hold new variables")

        for name in self.devices.keys():
            c = self.get(name)
            # This creates a variable inside the context of this name, points to class instance
            setattr(context, name, c)

    def add(self, device, name):
        """Add a device class instance to the registry, with a friendly name"""
        self.devices[name] = device

    def get(self, name):  # -> Device
        """Get the description for a device class from the store, and construct a class instance"""
        c = self.devices[name]
        # Check if device routing is enabled, turn it on if it is, and no address found
        return c

    def setup_device_routing(self, c):
        print("Configuring device routing")
        if self.fsk_router is not None:
            print("FSK Router started")
            if c.can_send():  # if can transmit, we can receive from it
                print("%s can send " % c.__class__.__name__)
                if isinstance(c, MiHomeDevice):
                    print("%s is a MiHomeDevice" % c.__class__.__name__)
                    address = (c._manufacturer_id, c._product_id, c.device_id)
                    print("Adding rx route for transmit enabled device %s" % str(address))
                    self.fsk_router.add(address, c)
        return c

    def rename(self, old_name, new_name):
        """Rename a device in the registry"""
        c = self.devices[old_name]  # get the class instance
        self.delete(old_name)  # remove from memory and from any disk version
        self.add(c, new_name)  # Add the same class back, but with the new name
        # Note: If rx routes are defined, they will still be correct,
        # because they wire directly to the device class instance

    def delete(self, name):
        """Delete the named class instance"""
        del self.devices[name]

    def list(self):
        """List the registry in a vaguely printable format, mostly for debug"""
        print("REGISTERED DEVICES:")
        for k in self.devices.keys():
            print("  %s -> %s" % (k, self.devices[k]))

    def size(self):
        """How many entries are there in the registry?"""
        return len(self.devices.keys())

    def devices(self):
        """A generator/iterator that can be used to get a list of device instances"""

        # Python2 and Python3 safe
        for k in self.devices.keys():
            device = self.devices[k]
            yield device

        # first get a list of all devices, in case the registry changes while iterating
        # #devices = self.devices.keys()

        # now 'generate' one per call
        # #i = 0
        # #while i < len(devices):
        # #    k = devices[i]
        # #    device = self.devices[k]
        # #    yield device
        # #    i += 1

    def names(self):
        """A generator/iterator that can be used to get a list of device names"""
        # first get a list of all devices, in case the registry changes while iterating
        devices = self.devices.keys()

        # now 'generate' one per call
        i = 0
        while i < len(devices):
            k = devices[i]
            yield k
            i += 1


# ----- DISCOVERY AND LEARNING -------------------------------------------------
# 5. LEARN/DISCOVER: To be able to instigate and manage learn mode from within an app
#
#   a. To send specific commands to green button devices so they can
#      learn the pattern
#   ? broadcast specific (house_code, index) repeatedly
#   ? user assisted start/stop

#   b. To sniff for any messages from MiHome devices and capture them
#      for later analysis and turning into device objects
#   ? either as a special receive-only learn mode
#   ? or as part of normal receive operation through routing unknown device id's
#   ? need a way to take a device id and consult active directory list,
#     and route to the correct class instance - a router for incoming messages

#   This means we need an incoming message 'router' with a message pump
#   that the app can call - whenever it is in receive, does a peek and
#   if there is a message, it knows what modulaton scheme is in use
#   so can route the message with (modulation, payload)

#   c. To process MiHome join requests, and send MiHome join acks
#   ? this would be routed by address to the device class

#   This also needs the message pump


# ----- MESSAGE ROUTER ---------------------------------------------------------

# a handler that is called whenever a message is received.
# routes it to the correct handling device class instance
# or instigates the unknown handler
# consults a RAM copy of part of the registry
# from mfrid,productid,sensorid -> handler

# The RAM copy is a routing table
# it must be updated whenever a factory returns a device class instance.

# Note, if you have a device class instance that is not registered,
# this means it cannot receive messages unless you pass them to it yourself.
# That's fine?

# might be one for OOK devices, a different one for FSK devices
# as they have different keying rules. OOK receive will only probably
# occur from another raspberry pi, or from a hand controller or MiHome hub.
# But it is possible to OOK receive a payload, it only has a house address
# and 4 index bits in it and no data, but those are routeable.

class Router():
    def __init__(self, name):
        self.name = name  # probably FSK or OOK
        self.routes = {}  # key(tuple of ids) -> value(device class instance)
        self.unknown_cb = None
        self.incoming_cb = None

    def add(self, address, instance):
        """Add this device instance to the routing table"""
        # When a message comes in for this address, it will be routed to its handle_message() method
        # address might be a string, a number, a tuple, but probably always the same for any one router
        self.routes[address] = instance

    def list(self):
        print("ROUTES:")
        for address in self.routes:
            print("  %s->%s" % (str(address), str(self.routes[address])))

    def incoming_message(self, address, message):
        if self.incoming_cb is not None:
            self.incoming_cb(address, message)

        # print("router.incoming addr=%s" % str(address))
        # print("routes:%s" % str(self.routes))

        if address in self.routes:
            ci = self.routes[address]
            ci.incoming_message(message)

        else:  # address has no route
            print ("No route to an object, for device:", str(address), str(message))
            # TODO: Could consult registry and squash if registry knows it
            self.handle_unknown(address, message)

    def when_incoming(self, callback):
        self.incoming_cb = callback

    def when_unknown(self, callback):
        """Register a callback for unknown messages"""
        # NOTE: this is the main hook point for auto discovery and registration
        self.unknown_cb = callback

    def handle_unknown(self, address, message):
        if self.unknown_cb is not None:
            self.unknown_cb(address, message)
        else:
            # Default action is just a debug message, and drop the message
            print("Unknown address: %s" % str(address))


# ---- DISCOVERY AGENT ---------------------------------------------------------
#
# Handles the discovery process when new devices appear and send reports.

class Discovery():
    """A Discovery agent that just reports any unknown devices"""
    def __init__(self, registry):
        self.registry = registry
        self.router   = self.registry.fsk_router
        self.registry.fsk_router.when_unknown(self.unknown_device)

    def unknown_device(self, address, message):
        print("message from unknown device:%s" % str(address))
        # default action is to drop message
        # override this method in sub classes if you want special processing

    def reject_device(self, address, message):
        print("message rejected from:%s" % (str(address)))
        # default action is to drop message
        # override this method if you want special processing

    def accept_device(self, address, message, forward=True):
        # #print("accept_device:%s" % str(address))
        # At moment, intentionally assume everything is mfrid=Energenie
        product_id = address[1]
        device_id  = address[2]
        # #print("**** wiring up registry and router for %s" % str(address))
        ci = Devices.DeviceFactory.get_device_from_id(product_id, device_id)
        self.registry.add(ci, "auto_%s_%s" % (str(hex(product_id)), str(hex(device_id))))
        self.router.add(address, ci)

        # Finally, forward the first message to the new device class instance
        if forward:
            # #print("**** routing first message to class instance")
            ci.incoming_message(message)

        # #self.registry.list()
        # #self.router.list()
        return ci  # The new device class instance that we created


class AutoDiscovery(Discovery):
    """A discovery agent that auto adds unknown devices"""
    def __init__(self, registry):
        Discovery.__init__(self, registry)

    def unknown_device(self, address, message):
        self.accept_device(address, message)


class ConfirmedDiscovery(Discovery):
    """A discovery agent that asks the app before accepting/rejecting"""
    def __init__(self, registry, ask):
        Discovery.__init__(self, registry)
        self.ask_fn = ask

    def unknown_device(self, address, message):
        y = self.ask_fn(address, message)
        if y:
            self.accept_device(address, message)
        else:
            self.reject_device(address, message)


class JoinAutoDiscovery(Discovery):
    """A discovery agent that looks for join requests, and auto adds"""
    def __init__(self, registry):
        Discovery.__init__(self, registry)

    def unknown_device(self, address, message):
        print("unknown device auto join %s\n%s" % (str(address), str(message)))

        # TODO: need to make this work with correct meta methods
        # #if not OpenThings.PARAM_JOIN in message:
        try:
            j = message[OpenThings.PARAM_JOIN]
        except KeyError:
            j = None

        # TODO: FIXME: Hack to bypass and send acknowledge for unknown valves
        if address[1] == 3:
            j = True

        if j is None:  # not a join
            Discovery.unknown_device(self, address, message)
        else:  # it is a join
            # but don't forward the join request as it will be malformed with no value
            ci = self.accept_device(address, message, forward=False)
            ci.join_ack()  # Ask new class instance to send a join_ack back to physical device
            print ("Acknowledged new device %s" % str(address))


class JoinConfirmedDiscovery(Discovery):
    """A discovery agent that looks for join requests, and auto adds"""
    def __init__(self, registry, ask):
        Discovery.__init__(self, registry)
        self.ask_fn = ask

    def unknown_device(self, address, message):
        print("**** unknown device confirmed join %s" % str(address))

        # TODO: need to make this work with correct meta methods
        # #if not OpenThings.PARAM_JOIN in message:
        try:
            j = message[OpenThings.PARAM_JOIN]
        except KeyError:
            j = None

        if j is None:  # not a join
            Discovery.unknown_device(self, address, message)
        else:  # it is a join
            y = self.ask_fn(address, message)
            if y:
                # but don't forward the join request as it will be malformed with no value
                ci = self.accept_device(address, message, forward=False)
                ci.join_ack()  # Ask new class instance to send a join_ack back to physical device
            else:
                self.reject_device(address, message)


# END
