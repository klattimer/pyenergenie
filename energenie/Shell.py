from cmd import Cmd
from energenie.Devices import DeviceFactory
from energenie.Handlers import HandlerFactory
from energenie.Config import Config
import time, math
import sys, select
import logging


#
# FIXME: This should be moved to a utils collection, as with other
# dump functions like registered devices and event monitoring
#
def describe_device(device):
    l = len(device['name'])
    indent_length = 4
    if indent_length % 4 < 2:
        indent_length += 4
    indent_length += 4
    indent_length = math.ceil(indent_length / 4) * 4

    num_spaces = indent_length - l
    print ("%s%sID: %d, Name: %s" % (device['id'], ' ' * num_spaces, device['name']))
    print ("%s%s: %s" % (' ' * indent_length, 'Description', device['description']))
    print ("%s%s: %s\n" % (' ' * indent_length, 'Product URL', device['url']))
    print ("%sFeatures" % (' ' * indent_length))
    print ("%s-----------------------------------" % (' ' * indent_length))
    for f in device['features'].keys():
        rtype = None
        if 'get' in device['features'][f]:
            rtype = device['features'][f]['return']
        print ("%s%s, %s" % (' ' * indent_length, f, rtype))


class EnergenieShell(Cmd):
    prompt = " > "
    intro = "Interactive configuration press ? for help."

    def __init__(self, energenie):
        super(EnergenieShell, self).__init__()
        self.energenie = energenie
        self.config = Config.singleton()

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
        try:
            self.energenie.discover(mode)
        except:
            logging.exception("Mode does not exist")
            print ("Mode %s does not exist" % mode)
            return

        self.energenie.start()

    def do_describe(self, device):
        """
        Describe a device's capabilities
        """
        try:
            device_description = DeviceFactory[device].describe()
        except:
            logging.exception("Device does not exist")
            print ("Device %s does not exist" % device)
        describe_device(device_description)

    def do_learn(self):
        """
        Learn OOK signals from transmitters

        Set the device to listen OOK mode and collect signals
        The goal is to decode a reasonable approximation of the
        transmitted bytes, such that it can then be correlated
        with the appropriate device type.

        This appears to require implementation in radio.c/radio.py to be completed
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

    def do_monitor(self):
        """
        Monitor incoming sensor readings
        """
        print("Starting PyEnergenie Monitor Mode")
        for handler in self.energenie.handlers.list():
            self.energenie.handlers.get(handler).enabled = False
        self.energenie.handlers.add("ECHO", type="TerminalEchoHandler")
        self.energenie.discover("ECHO")
        self.energenie.start()

        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print('interrupted!')
            self.energenie.stop()

    def do_add_handler(self, type):
        """
        Add a handler
        """
        # Enters into a sub-command loop for setting handler properties
        print ("Creating new handler of type " + type)
        handler_factory = HandlerFactory.singleton()
        try:
            cls = handler_factory[type]
        except:
            logging.exception("Type does not exist")
            print ("Handler type does not exist")
            return

        name = input("Name of the new handler: ")
        kw_args = {
            'type': type
        }
        for (key, value) in cls.args:
            kw_args[key] = input(value['prompt'] + ': ')

        self.energenie.handlers.add(name, **kw_args)

    def do_save(self):
        self.energenie.handlers.save()
        self.energenie.registry.save()
        self.config.save()

    def do_exit(self):
        """
        Exit pyenergenie shell
        """
        return True

    do_EOF = do_exit
