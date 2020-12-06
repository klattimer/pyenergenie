import os
import importlib
import logging


class Handler:
    _protocol = None
    _description = None
    _args = {}

    @classmethod
    def describe(cls):
        return {
            'protocol': cls._protocol,
            'description': cls._description,
            'args': cls._args
        }

    def __init__(self, **kw_args):
        pass

    def serialise(self):
        return {
            'type': self.__class__.__name__
        }

    def device_added(self, device):
        pass

    def device_removed(self, device):
        pass

    def set(self, device, key, value):
        pass

    def get(self, device, key):
        pass

    def handle_reading(self, device, key, value):
        pass


class HandlerFactory:
    __single = None

    @classmethod
    def singleton(cls):
        if cls.__single is None:
            cls.__single = cls()
        return cls.__single

    @classmethod
    def keys(cls):
        return list(cls.singleton().handlers.keys())

    def __init__(self):
        self.handlers = {}

        p = os.path.dirname(os.path.abspath(__file__))
        files = os.listdir(p)
        for f in files:
            if f.startswith("__"): continue
            if not f.endswith(".py"): continue
            m = f.replace('.py', '')
            module = importlib.import_module('.' + m, 'energenie.Plugins')
            try:
                plugin = getattr(module, m)

                if m in self.handlers.keys():
                    raise Exception("Plugin already registered %s" % m)

                self.handlers[m] = plugin

                logging.info("Plugin loaded \"%s\"" % m)
            except:
                logging.exception("Plugin failed to load: \"%s\"" % m)

    def __getitem__(self, k):
        return self.handlers[k]


class HandlerRegistry:
    __single = None

    @classmethod
    def singleton(cls):
        if cls.__single is None:
            cls.__single = cls()
        return cls.__single

    @classmethod
    def handle_reading(cls, device, key, value):
        cls.singleton().handle_reading(key, value)

    def __init__(self):
        # Load settings from config

        # Instantiate the handlers
        self._handlers = []
        pass

    def handle_reading(self, device, key, value):
        for handler in self._handlers:
            handler.handle_reading(device, key, value)
