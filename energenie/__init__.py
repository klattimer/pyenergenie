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


registry   = None
fsk_router = None
ook_router = None


class Energenie(threading.Thread):
    def __init__(self):
        super()
        self.command_queue = Queue(maxsize=0)
        """Start the Energenie system running"""

        radio.init()
        OpenThings.init(Devices.Device._crypt_pid)

        self.fsk_router = Registry.Router("fsk")
        self.ook_router = None
        # OOK receive not yet written
        # It will be used to be able to learn codes from Energenie legacy hand remotes
        # #self.ook_router = Registry.Router("ook")

        self.registry = Registry.DeviceRegistry()
        self.registry.set_fsk_router(self.fsk_router)
        # #self.registry.set_ook_router(self.ook_router

        # registry.list()
        # fsk_router.list()

        # Default discovery mode, unless changed by app
        # #discovery_none()
        # #discovery_auto()
        # #discovery_ask(ask)
        # discovery_autojoin()
        # #discovery_askjoin(ask)

    def __del__(self):
        super().__del__()
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
        Registry.AutoDiscovery(registry, fsk_router)
        # #print("Using auto discovery")

    def discovery_ask(self, ask_fn):
        Registry.ConfirmedDiscovery(self.registry, self.fsk_router, self.ask_fn)
        # #print("using confirmed discovery")

    def discovery_autojoin(self):
        Registry.JoinAutoDiscovery(registry, fsk_router)
        # #print("using auto join discovery")

    def discovery_askjoin(self, ask_fn):
        Registry.JoinConfirmedDiscovery(registry, fsk_router, ask_fn)
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
