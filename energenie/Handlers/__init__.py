import os
import importlib, inspect
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
        # Lookup the device, and set the key to value
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
            for name, obj in inspect.getmembers(module):
                try:
                    if not inspect.isclass(obj):
                        continue

                    if not issubclass(obj, Handler):
                        continue

                    if name == "Handler":
                        continue

                    plugin = getattr(module, name)

                    if name in self.handlers.keys():
                        logging.debug("Plugin already registered %s" % name)
                        continue

                    self.handlers[name] = plugin
                    logging.info("Plugin loaded \"%s\"" % name)
                except:
                    logging.exception("Plugin failed to load: \"%s\"" % name)

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
        logging.debug("Handling message 1")
        cls.singleton()._handle_reading(device, key, value)

    def __init__(self):
        # Load settings from config
        self.__handler_factory = HandlerFactory.singleton()
        handlers = Config.singleton()['handlers']
        self._handlers = {}
        for (class_name, handler_args) in handlers.values():
            if handler_args.get('enabled') is not True:
                continue
            handler = self.__handler_factory[class_name](**handler_args)
            self._handlers[handler_args['name']] = handler

    def add(self, class_name, **kw_args):
        handler = self.__handler_factory[class_name](**kw_args)
        self._handlers[kw_args['name']] = handler

    def _handle_reading(self, device, key, value):
        logging.debug("Handling message 2")
        for handler in self._handlers.values():
            logging.debug("Handling message 3")
            handler.handle_reading(device, key, value)
