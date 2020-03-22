from cmd import Cmd
from energenie import Energenie


class EnergenieShell(Cmd):
    prompt = " > "
    intro = "Interactive configuration press ? for help."

    def __init__(self):
        super(EnergenieShell, self).__init__()
        self.energenie = Energenie()

    def do_add(self, device_type, device_id):
        """
        Add a devjce
        """

    def do_remove(self, device_name=None, device_id=None):
        """
        Remove a device
        """

    def do_list(self):
        """
        List configured devices
        """

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
