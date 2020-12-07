# Simple terminal monitoring plugin
from energenie.Handlers import Handler


class TerminalEchoHandler(Handler):
    _description = "Simple terminal output handler"

    def __init__(self, **kw_args):
        super.__init__(self, **kw_args)

    def handle_reading(self, device, key, value):
        print ("Received reading: %s -> %s = %s" % (str(device), str(key), str(value)))
