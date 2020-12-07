import os
import importlib
import logging
from ..Config import Config


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
        self.name = kw_args.get('name')
        self.enabled = kw_args.get('enabled')

    def serialise(self):
        return {
            'type': self.__class__.__name__,
            'name': self.name,
            'enabled': self.enabled
        }

    def device_detected(self, device):
        pass

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
            module = importlib.import_module('.' + m, 'energenie.Handlers')
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
        cls.singleton()._handle_reading(key, value)

    def __init__(self):
        # Load settings from config
        self.__handler_factory = HandlerFactory.singleton()
        handlers = Config.singleton()['handlers']
        self._handlers = {}
        for (class_name, handler_args) in handlers.values():
            if handler_args.get('enabled') is not True:
                continue
            handler = self.__handler_factory[class_name](**handler_args)
            self._handlers[handler_args['name']](handler)

    def _handle_reading(self, device, key, value):
        for handler in self._handlers.values():
            handler.handle_reading(device, key, value)
