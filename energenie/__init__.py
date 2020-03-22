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
from queue import Queue

from . import radio
from . import Devices
from . import Registry
from . import OpenThings
from . import Shell


class Energenie(threading.Thread):
    def __init__(self):
        super(Energenie, self).__init__()
        self.command_queue = Queue(maxsize=0)
        """Start the Energenie system running"""

        radio.init()
        OpenThings.init(Devices.Device._crypt_pid)

        self.registry = Registry.DeviceRegistry()
        self.ask_fn = self.ask

        # registry.list()

        # Default discovery mode, unless changed by app
        # #discovery_none()
        # #discovery_auto()
        # #discovery_ask(ask)
        # discovery_autojoin()
        # #discovery_askjoin(ask)
        self.discovery_auto()

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
        while self.running is True:
            self.loop()

            # Process the command queue

    def stop(self):
        """Cleanly close the Energenie system when finished"""
        self.running = False
        radio.finished()

    def discovery_none(self):
        self.fsk_router.when_unknown(None)

    def discovery_auto(self):
        Registry.AutoDiscovery(self.registry)
        # #print("Using auto discovery")

    def discovery_ask(self, ask_fn):
        Registry.ConfirmedDiscovery(self.registry, self.ask_fn)
        # #print("using confirmed discovery")

    def discovery_autojoin(self):
        Registry.JoinAutoDiscovery(self.registry)
        # #print("using auto join discovery")

    def discovery_askjoin(self, ask_fn):
        Registry.JoinConfirmedDiscovery(self.registry, ask_fn)
        # #print("using confirmed join discovery")

    def ask(self, address, message):
        MSG = "Do you want to register to device: %s? " % str(address)
        try:
            if message is not None:
                print(message)
            y = raw_input(MSG)

        except AttributeError:
            y = input(MSG)

        if y == "": return True
        y = y.upper()
        if y in ['Y', 'YES']: return True
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interactive", action="store_true", help="Start interactive mode")
    parser.add_argument("-d", "--discover", action="store_true", help="Start discovery mode")
    parser.add_argument("-l", "--list", action="store_true", help="List devices and capabilities")
    parser.add_argument("-f", "--format", type=str, choices=['TERM', 'JSON', 'XML'], help="List devices and capabilities")
    parser.add_argument("device", type=str, nargs=1, help="Select device")

    args = parser.parse_args()
    if args.interactive:
        Shell.EnergenieShell().cmdloop()

    elif args.discover:
        pass


if __name__ == '__main__':
    main()
