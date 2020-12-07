# energenie.py  24/05/2016  D.J.Whale
#
# Provides the app writer with a simple single module interface to everything.
# At the moment, this just hides the fact that the radio module needs to be initialised
# at the start and cleaned up at the end.
#
# Future versions of this *might* also start receive monitor or scheduler threads.

import time
import argparse
import threading
import logging
import json
import math
from queue import Queue

from . import radio
from . import Devices
from . import Registry
from . import OpenThings
from . import Shell
from . import Handlers
from .Config import Config
from enum import Enum


def test_dummy():
    """Dummy to quiet pytest for now"""
    assert True


class DiscoveryMode(Enum):
    ECHO = 1            # Echo signals that are received
    AUTO = 2            # Automatically add devices that are seen
    ASK = 3             # Ask the user if they wish to add the device
    AUTOJOIN = 4        # Automatically respond with acknowledment
    ASKJOIN = 5         # Respond with acknowledment when user agrees

    @classmethod
    def get(cls, name):
        return cls.__members__[name]

    @classmethod
    def list(cls):
        return [name for name in cls.__members__.keys()]


class Energenie(threading.Thread):
    def __init__(self):
        super(Energenie, self).__init__()
        self.command_queue = Queue(maxsize=0)
        """Start the Energenie system running"""

        radio.init()
        OpenThings.init(Devices.Device._crypt_pid)

        self.registry = Registry.DeviceRegistry.singleton()
        self.handlers = Handlers.HandlerRegistry.singleton()
        self.ask_fn = self.ask

    def __del__(self):
        self.stop()

    def loop(self, receive_time=1):
        """Handle receive processing"""
        radio.receiver(fsk=True)
        timeout = time.time() + receive_time
        handled = False

        while True:
            if radio.is_receive_waiting():
                payload = radio.receive_cbp()
                now = time.time()
                try:
                    msg        = OpenThings.decode(payload, receive_timestamp=now)
                    hdr        = msg["header"]
                    mfr_id     = hdr["mfrid"]
                    product_id = hdr["productid"]
                    device_id  = hdr["sensorid"]
                    address    = (mfr_id, product_id, device_id)

                    # print "received ", time.time()
                    self.registry.fsk_router.incoming_message(address, msg)
                    handled = True
                except OpenThings.OpenThingsException:
                    # print("Can't decode payload:%s" % payload)
                    # error = True
                    pass

            now = time.time()
            if now > timeout or handled: break

        return handled

    def start(self):
        self.running = True
        super().start()

    def run(self):
        # IMPROVE: Set up logging here
        logging.basicConfig(level=logging.DEBUG)
        while self.running is True:
            self.loop()

            # Process the command queue

    def stop(self):
        """Cleanly close the Energenie system when finished"""
        self.running = False
        radio.finished()

    def discover(self, mode):
        if type(mode) == str:
            mode = DiscoveryMode.get(mode)

        if mode == DiscoveryMode.ECHO:
            self.fsk_router.when_unknown(None)
        elif mode == DiscoveryMode.AUTO:
            Registry.AutoDiscovery(self.registry)
        elif mode == DiscoveryMode.ASK:
            Registry.ConfirmedDiscovery(self.registry, self.ask_fn)
        elif mode == DiscoveryMode.AUTOJOIN:
            Registry.JoinAutoDiscovery(self.registry)
        elif mode == DiscoveryMode.ASKJOIN:
            Registry.JoinConfirmedDiscovery(self.registry, self.ask_fn)

    def ask(self, address, message):
        MSG = "Do you want to register the device (Y/n): %s? " % str(address)
        if message is not None:
            MSG += message
        y = input(MSG)

        if y == "": return True
        y = y.upper()
        if y in ['Y', 'YES']: return True
        return False


def format_report(report_data):
    print ("Supported devices")
    print ("--------------------------------------------------------")

    indent_length = 4

    for k in report_data['supported_devices'].keys():
        l = len(k)
        if l > indent_length:
            indent_length = l
    if indent_length % 4 < 2:
        indent_length += 4
    indent_length += 4
    indent_length = math.ceil(indent_length / 4) * 4

    for k in report_data['supported_devices'].keys():
        l = len(k)
        d = report_data['supported_devices'][k]
        num_spaces = indent_length - l
        print ("%s%sID: %d, Name: %s" % (k, ' ' * num_spaces, d['name']))
        print ("%s%s: %s" % (' ' * indent_length, 'Description', d['description']))
        print ("%s%s: %s\n" % (' ' * indent_length, 'Product URL', d['url']))
        print ("%sFeatures" % (' ' * indent_length))
        print ("%s-----------------------------------" % (' ' * indent_length))
        for f in d['features'].keys():
            rtype = None
            if 'get' in d['features'][f]:
                rtype = d['features'][f]['return']
            print ("%s%s, %s" % (' ' * indent_length, f, rtype))

    print ("\nRegistered devices")
    print ("--------------------------------------------------------")

    for k in report_data['registered_devices'].keys():
        l = len(k)
        if l > indent_length:
            indent_length = l
    if indent_length % 4 < 2:
        indent_length += 4
    indent_length += 4
    indent_length = math.ceil(indent_length / 4) * 4

    for k in report_data['registered_devices'].keys():
        l = len(k)
        d = report_data['registered_devices'][k]
        num_spaces = indent_length - l
        print ("%s%sModel: %s" % (k, ' ' * num_spaces, d['type']))
        print ("%s%s:%s" % (' ' * indent_length, 'UUID', d['uuid']))
        print ("%s%s:%s" % (' ' * indent_length, 'Device ID', d['device_id']))
        print ("%s%s:%s" % (' ' * indent_length, 'Location', str(d['location'])))
        print ("%s%s:%s" % (' ' * indent_length, 'Enabled', str(d['enabled'])))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interactive", action="store_true", help="Start interactive mode")
    parser.add_argument("-d", "--discover", action="store_true", help="Start discovery mode")
    parser.add_argument("-b", "--daemon", action="store_true", help="Start daemon mode")
    parser.add_argument("-m", "--monitor", action="store_true", help="Start monitor mode")
    parser.add_argument("-l", "--list", action="store_true", help="List devices and capabilities")
    parser.add_argument("-f", "--format", type=str, choices=['TERM', 'JSON'], help="Set the format of the output")
    parser.add_argument("-j", "--discover-mode", type=str, choices=DiscoveryMode.list(), help="Set the discovery mode")
    parser.add_argument("-s", "--save", action="store_true", help="Save config")
    parser.add_argument("device", type=str, nargs='?', help="Select device")

    args = parser.parse_args()

    config = Config.singleton()
    config.load_command_line_args(args)

    if args.save:
        config.apply_command_line_args()

    if args.interactive:
        e = Energenie()
        Shell.EnergenieShell(e).cmdloop()

    elif args.list:
        registry = Registry.DeviceRegistry.singleton()
        report_data = {}
        report_data['supported_devices'] = {k: Devices.DeviceFactory[k].describe() for k in Devices.DeviceFactory.keys()}
        report_data['registered_devices'] = {k: registry.get(k).serialise() for k in registry.list()}

        if args.format == 'JSON':
            print(json.dumps(report_data, indent=4, sort_keys=True))
        else:
            print(format_report(report_data))

    elif args.monitor:
        print("Starting PyEnergenie Monitor Mode")
        e = Energenie()
        e.discover("ECHO")
        e.start()
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print('interrupted!')
            e.stop()

    elif args.discover:
        print("Starting PyEnergenie Discovery Mode with auto-join")
        e = Energenie()
        if args.discover_mode:
            e.discover(args.discover_mode)
        else:
            e.discover(DiscoveryMode.AUTOJOIN)
        e.start()
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print('interrupted!')
            if args.save:
                e.registry.save()
            e.stop()
    elif args.daemon:
        e = Energenie()
        e.start()
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            if args.save:
                e.registry.save()
            e.stop()
    else:
        parser.print_usage()

    if args.save:
        config.save()

if __name__ == '__main__':
    main()
