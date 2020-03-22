from cmd import Cmd


class EnergenieShell(Cmd):
    prompt = " > "
    intro = "Interactive configuration press ? for help."

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

    def do_discover(self):
        """
        Discover and register new devices
        """

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
