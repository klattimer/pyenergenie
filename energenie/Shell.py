from cmd import Cmd
from energenie.Devices import DeviceFactory


class EnergenieShell(Cmd):
    prompt = " > "
    intro = "Interactive configuration press ? for help."

    def __init__(self, energenie):
        super(EnergenieShell, self).__init__()
        self.energenie = energenie

    def do_add(self, name, device_type, device_id):
        """
        Add a devjce
        """

    def do_remove(self, device_name=None, device_id=None):
        """
        Remove a device
        """

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

    def do_learn(self):
        """
        Learn OOK signals from transmitters
        """

    def do_teach(self):
        """
        Teach OOK signals to receivers
        """

    def do_exit(self):
        """
        Exit pyenergenie shell
        """
        return True

    do_EOF = do_exit
