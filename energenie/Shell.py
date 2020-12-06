from cmd import Cmd
from energenie.Devices import DeviceFactory
import time
import sys, select


class EnergenieShell(Cmd):
    prompt = " > "
    intro = "Interactive configuration press ? for help."

    def __init__(self, energenie):
        super(EnergenieShell, self).__init__()
        self.energenie = energenie

    def do_add(self, name, device_type, device_id, location=None):
        """
        Add a device
        """
        device = DeviceFactory.get_device_from_model(device_type, **{
            "name": name,
            "device_id": device_id,
            "location": location
        })
        self.energenie.registry.add(device)

    def do_remove(self, device_name=None, device_id=None):
        """
        Remove a device
        """
        self.energenie.registry.delete(device_name if device_name else device_id)

    def do_drivers(self):
        drivers = DeviceFactory.singleton().keys()
        drivers = [DeviceFactory.singleton()[d].describe for d in drivers]
        for d in drivers:
            for k, v in d.items():
                print ("%s: %s" % (k, v))

    def do_list(self):
        """
        List configured devices
        """
        devices = self.energenie.registry.list()
        for d in devices:
            print ("%s: %s" % (d, self.energenie.registry.devices[d]))

    def do_discover(self, mode):
        """
        Discover and register new devices
        """
        self.energenie.start()

    def do_describe(self, device):
        """
        Describe a device's capabilities
        """
        print ("Not yet implemented")

    def do_learn(self):
        """
        Learn OOK signals from transmitters
        """
        print ("Not yet implemented")

    def do_teach(self, name, group_code, device_id, location=None):
        """
        Teach OOK signals to receivers
        """
        device = DeviceFactory.get_device_from_model("MiHomeLight", **{
            "name": name,
            "device_id": [group_code, device_id],
            "location": location
        })

        input("Please set the receiving device into learn mode and press enter to continue.")
        print ("Teaching device %s %s:%s" % (name, str(device_id)))
        print ("Press enter to stop.")
        interrupted = False
        for i in range(1000):
            if i % 2 == 0:
                device.turn_on()
            else:
                device.turn_off()

            time.sleep(0.5)
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                input()
                interrupted = True
                break

        if not interrupted:
            line = input("Did the device successfully respond? [Y/n]")
            if 'n' in line.lower():
                return

        self.energenie.registry.add(device)

    def do_exit(self):
        """
        Exit pyenergenie shell
        """
        return True

    do_EOF = do_exit
