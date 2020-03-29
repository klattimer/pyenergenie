# -*- coding: utf-8 -*-
from .. import OnAir
# from .. import Registry
import os
import importlib
import inspect
import time
from collections import defaultdict, Counter
from uuid import uuid4
import logging


class Device():
    _manufacturer_id = None
    _broadcast_id = None
    _crypt_pid = 0x00F2  # 242
    _crypt_pip = 0x0100  # 256

    _product_id = None
    _product_name = "Base Device Class"
    _product_description = "Base Class used for OpenThings devices"
    _product_rf = None
    _product_url = None

    @property
    def address(self):
        return (self._manufacturer_id, self._product_id, self.device_id)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        # Causes circular import problem
        #
        # if value is True:
        #     Registry.DeviceRegistry.singleton().setup_device_routing(self)
        # else:
        #     Registry.DeviceRegistry.singleton().remove_device_routing(self)
        self._enabled = value

    @classmethod
    def features(cls):
        """
        Extract the features provided by this class
        """
        # Capabilities and Readings aren't exported by the class,
        # they're settings on the instance itself, so we collect up
        # a detailed spec from the function's available.
        #
        # This requires some specification, all features must have a get or set
        # method
        #
        # e.g. set_switch(enabled: bool) -> None:
        #      get_switch() -> bool:
        #
        # Constricting the method naming like this is necessary to provide a
        # list of supported features.
        #
        keys = cls.__dict__.keys()
        features = defaultdict(dict)

        for k in keys:
            # Check if it's not a function, continue
            if type(cls.__dict__[k]).__name__ != 'function':
                continue

            if not k.startswith("get_") and not k.startswith("set_"):
                continue

            # Get the function description, arguments, return etc...
            argspec = inspect.getfullargspec(cls.__dict__[k])

            def convarg(arg):
                t = argspec.annotations[arg]
                ret = {'arg': arg, 'type': t.__name__}
                if argspec.defaults is not None:
                    p = argspec.args.index(arg) - len(argspec.defaults)
                    if p >= 0: ret['default'] = argspec.defaults[p]
                return ret

            return_type = None
            if 'return' in argspec.annotations.keys():
                return_type = argspec.annotations['return'].__name__

            features[k[4:]][k[0:3]] = {
                'method': k,
                'args': [convarg(arg) for arg in argspec.args if arg != 'self'],
                'return': return_type
            }
        return features

    @classmethod
    def describe(cls):
        return {
            'type': cls.__name__,
            'id': cls._product_id,
            'name': cls._product_name,
            'description': cls._product_description,
            'rf': cls._product_rf,
            'url': cls._product_url,
            'features': cls.features()
        }

    @classmethod
    def header(cls):
        return {
            "mfrid": cls._manufacturer_id,
            "productid": cls._product_id,
            "encryptPIP": cls._crypt_pip,
            "sensorid": 0
        }

    @classmethod
    def can_send(cls):
        return cls._product_rf.contains('tx')

    def serialise(self):
        return {
            'type': self.__class__.__name__,
            'device_id': self.device_id,
            'name': self.name,
            'enabled': self.enabled,
            'uuid': self.uuid
        }

    """A generic connected device abstraction"""
    def __init__(self, name=None, device_id=None, enabled=True, uuid=None):
        if type(self.__class__._product_rf) == str:
            if self.__class__._product_rf.startswith('FSK'):
                self.air_interface = DeviceFactory.fsk_interface
            elif self.__class__._product_rf.startswith('OOK'):
                self.air_interface = DeviceFactory.ook_interface
            else:
                raise Exception("Air interface is undefined for this device %s(%s):%s" % (name, str(device_id), uuid))
        self.device_id = self.parse_device_id(device_id)
        self.name = name
        self._enabled = enabled
        if uuid is None: uuid = str(uuid4())
        self.uuid = uuid

        class RadioConfig(): pass
        self.radio_config = RadioConfig()

        class Capabilities(): pass
        self.capabilities = Capabilities()

        self.updated_cb = None
        self.rxseq = 0
        self.last_receive_time = 0
        self.__last_receive_intervals = []

    @staticmethod
    def parse_device_id(device_id):
        """device_id could be a number, a hex string or a decimal string"""
        logging.debug("**** parsing: %s" % str(device_id))
        if device_id is None:
            raise ValueError("device_id is None, not allowed")

        if type(device_id) == int:
            return device_id  # does not need to be parsed

        if type(device_id) == tuple or type(device_id) == list:
            # each part of the tuple could be encoded
            return tuple([Device.parse_device_id(p) for p in device_id])

        if type(device_id) == str and len(device_id) > 0:
            return eval(device_id)
        else:
            raise ValueError("device_id unsupported type or format, got: %s %s" % (type(device_id), str(device_id)))

    def get_last_receive_time(self):  # ->timestamp
        """The timestamp of the last time any message was received by this device"""
        return self.last_receive_time

    def get_next_receive_time(self):  # -> timestamp
        """An estimate of the next time we expect a message from this device"""
        #
        # based on the assumption that some incoming packets are corrupt, we take the
        # modal interval between hits, using a window of 30 seconds, we then collect the
        # values in that window and average them
        #
        min_interval = 30  # 30 seconds
        intervals = [min_interval * round(x / min_interval) for x in self.__last_receive_intervals]
        counted = Counter(intervals)
        most_common = counted.most_common(1)[0]
        segment = [x for x in self.__last_receive_intervals
                   if x > most_common - (min_interval / 2.) and
                   x < most_common + (min_interval / 2.)]
        return self.__last_receive_time + (sum(segment) / len(segment))

    def get_receive_count(self):
        return self.rxseq

    def incoming_message(self, payload):
        """Entry point for a message to be processed"""
        # This is the base-class entry point, don't  override this, but override handle_message
        self.rxseq += 1
        self.handle_message(payload)
        if self.updated_cb is not None:
            self.updated_cb(self, payload)
        l = time.time()
        if self.last_receive_time > 0:
            interval = l - self.last_receive_time
            self.__last_receive_intervals.append(interval)
        if self.__last_receive_intervals > 60:
            self.__last_receive_intervals = self.__last_receive_intervals[-60:]
        self.last_receive_time = l

    def handle_message(self, payload):
        """Default handling for a new message"""
        logging.warning("incoming(unhandled): %s" % payload)

    def send_message(self, payload):
        logging.warning("send_message %s" % payload)
        # A raw device has no knowledge of how to send, the sub class provides that.

    def when_updated(self, callback):
        """Provide a callback handler to be called when a new message arrives"""
        self.updated_cb = callback
        # signature: update(self, message)

    def __repr__(self):
        return "Device()"


class DeviceFactory:
    __single = None
    ook_interface = OnAir.TwoBitAirInterface()
    fsk_interface = OnAir.OpenThingsAirInterface()

    @classmethod
    def singleton(cls):
        if cls.__single is None:
            cls.__single = cls()
        return cls.__single

    @classmethod
    def keys(cls):
        return list(cls.singleton().product_model_index.keys())

    @classmethod
    def get_device_from_model(cls, model, **kw_args):
        if model not in cls.keys():
            raise ValueError("Unsupported device:%s" % model)

        c = cls.singleton().product_model_index[model]
        return c(**kw_args)

    @classmethod
    def get_device_from_id(cls, id, **kw_args):
        if id not in cls.singleton().product_id_index.keys():
            raise ValueError("Unsupported device id:%s" % id)
        c = cls.singleton().product_id_index[id]
        return c(**kw_args)

    @property
    def manufacturers(self):
        return self._manufacturers

    @property
    def products(self):
        return self.product_id_index.keys()

    def __init__(self):
        self.product_id_index = {}
        self.product_model_index = {}

        p = os.path.dirname(os.path.abspath(__file__))
        files = os.listdir(p)
        for f in files:
            if f.startswith("__"): continue
            if not f.endswith(".py"): continue
            m = f.replace('.py', '')
            module = importlib.import_module('.' + m, 'energenie.Devices')
            try:
                plugin = getattr(module, m)

                if m in self.product_model_index.keys():
                    raise Exception("Product model already registered %s" % m)

                self.product_model_index[m] = plugin

                if plugin._product_id is None: continue
                if int(plugin._product_id) in self.product_id_index.keys():
                    raise Exception("Product ID already registered %d" % int(plugin._product_id))
                self.product_id_index[int(plugin._product_id)] = plugin
            except:
                logging.exception("Plugin failed to load: \"%s\"" % m)

        self._manufacturers = list(set([self[d]._manufacturer_id for d in self.product_model_index.keys()]))
        self._manufacturers.sort()

    def __getitem__(self, key):
        try:
            key = int(key)
        except Exception:
            pass

        if type(key) == int:
            return self.product_id_index[key]

        return self.product_model_index[key]
