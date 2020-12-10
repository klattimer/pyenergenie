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
            'protocol': cls.protocol,
            'description': cls.description,
            'args': cls.args
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
            try:
                module = importlib.import_module('.' + m, 'energenie.Handlers')
            except:
                logging.exeption("Module import failed: " + m)
                continue

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
        cls.singleton()._handle_reading(device, key, value)

    @classmethod
    def device_detected(cls, device):
        cls.singleton()._device_detected(device)

    @classmethod
    def device_removed(cls, device):
        cls.singleton()._device_removed(device)

    @classmethod
    def device_added(cls, device):
        cls.singleton()._device_added(device)

    def __init__(self):
        # Load settings from config
        self.__handler_factory = HandlerFactory.singleton()
        handlers = Config.singleton()['handlers']
        self._handlers = {}
        for (name, handler_args) in handlers.items():
            if handler_args.get('enabled') is not True:
                continue
            try:
                handler = self.__handler_factory[handler_args['type']](**handler_args)
            except:
                logging.exception("Failed to initialise handler of type %s" % handler_args['type'])
                return
            logging.debug("Adding handler: " + name)
            self._handlers[name] = handler

    def save(self):
        """ Set config handlers to new settings """
        pass

    def list(self):
        return list(self._handlers.keys())

    def add(self, name, **kw_args):
        handler = self.__handler_factory[kw_args['type']](**kw_args)
        self._handlers[name] = handler

    def get(self, name):
        return self._handlers[name]

    def _device_detected(self, device):
        pass

    def _device_removed(self, device):
        for handler in self._handlers.values():
            if handler.enabled is False: continue
            handler.device_removed(device)

    def _device_added(self, device):
        for handler in self._handlers.values():
            if handler.enabled is False: continue
            handler.device_added(device)

    def _handle_reading(self, device, key, value):
        for handler in self._handlers.values():
            if handler.enabled is False: continue
            handler.handle_reading(device, key, value)

    def ask(self):
        pass
