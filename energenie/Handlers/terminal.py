# Simple terminal monitoring plugin
from energenie.Handlers import Handler


class TerminalEchoHandler(Handler):
    description = "Simple terminal output handler"

    def __init__(self, **kw_args):
        super(TerminalEchoHandler, self).__init__(**kw_args)

    def handle_reading(self, device, key, value):
        print ("Received reading: %s -> %s = %s" % (str(device), str(key), str(value)))
