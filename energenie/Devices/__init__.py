# -*- coding: utf-8 -*-
from .. import OnAir
# from .. import Registry
import os
import importlib
import inspect
import time
from collections import defaultdict, Counter
from energenie.Handlers import HandlerRegistry
from uuid import uuid4
import logging


class Device():
    _manufacturer_id = None
    _broadcast_id = None
    _crypt_pid = 0x00F2  # 242
    _crypt_pip = 0x0100  # 256

    _product_id = None
    _product_name = None
    _product_description = None
    _product_rf = None
    _product_url = None
    _product_user_guide = None
    _product_image_url = None

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
        keys = [func for func in dir(cls) if callable(getattr(cls, func))]
        features = defaultdict(dict)

        for k in keys:
            if not k.startswith("get_") and not k.startswith("set_"):
                continue

            # Get the function description, arguments, return etc...
            argspec = inspect.getfullargspec(getattr(cls, k))

            def convarg(arg):
                if arg in argspec.annotations.keys():
                    ret = {'arg': arg, 'type': argspec.annotations[arg].__name__}
                else:
                    ret = {'arg': arg, 'type': 'Any'}
                if argspec.defaults is not None:
                    p = argspec.args.index(arg) - len(argspec.defaults)
                    if p >= 0: ret['default'] = argspec.defaults[p]
                return ret

            return_type = None
            if 'return' in argspec.annotations.keys():
                return_type = argspec.annotations['return'].__name__

            features[k[4:]][k[0:3]] = {
                'method': k,
                'args': [convarg(arg) for arg in argspec.args if arg != 'self' and arg != 'cls'],
                'return': return_type
            }
        return features

    @classmethod
    def describe(cls):
        return {
            'type': cls.__name__,
            'manufacturer_id': cls._manufacturer_id,
            'product_id': cls._product_id,
            'name': cls._product_name,
            'description': cls._product_description,
            'rf': cls._product_rf,
            'url': cls._product_url,
            'image': cls._product__image_url,
            'user_guide': cls._product_user_guide,
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
        return 'tx' in cls._product_rf

    def serialise(self):
        return {
            'type': self.__class__.__name__,
            'device_id': self.device_id,
            'name': self.name,
            'enabled': self.enabled,
            'location': self.location,
            'uuid': self.uuid
        }

    def state(self):
        states = {}
        features = self.features()
        for f in features.keys():
            if 'get' in features[f]:
                func = getattr(self, 'get_' + f)
                states[f] = func()
        return states

    def do_set_state(self, key, value):
        features = self.features()
        if key in features.keys() and 'set' in features[key]:
            func = getattr(self, 'set_' + key)
            return func(value)
        raise KeyError("state with key %s not found" % key)

    """A generic connected device abstraction"""
    def __init__(self, name, device_id, enabled=True, uuid=None, location=None):
        if type(self.__class__._product_rf) == str:
            if self.__class__._product_rf.startswith('FSK'):
                self.air_interface = DeviceFactory.fsk_interface
            elif self.__class__._product_rf.startswith('OOK'):
                self.air_interface = DeviceFactory.ook_interface
            elif self.__class__._product_rf.startswith():
                self.air_interface = DeviceFactory.ev1527_interface
            else:
                raise Exception("Air interface is undefined for this device %s(%s):%s" % (name, str(device_id), uuid))
        self.device_id = self.parse_device_id(device_id)
        self.name = name
        self.location = location
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
        # logging.debug("**** parsing: %s" % str(device_id))
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

    def get_last_receive_time(self) -> int:  # ->timestamp
        """The timestamp of the last time any message was received by this device"""
        return self.last_receive_time

    def get_next_receive_time(self) -> int:  # -> timestamp
        """An estimate of the next time we expect a message from this device"""
        #
        # based on the assumption that some incoming packets are corrupt, we take the
        # modal interval between hits, using a window of 30 seconds, we then collect the
        # values in that window and average them
        #
        if len(self.__last_receive_intervals) < 2: return -1
        min_interval = 30  # 30 seconds
        intervals = [min_interval * round(x / min_interval) for x in self.__last_receive_intervals]
        counted = Counter(intervals)
        most_common = counted.most_common(1)[0][0]
        segment = [x for x in self.__last_receive_intervals
                   if x > most_common - (min_interval / 2.) and
                   x < most_common + (min_interval / 2.)]
        return self.last_receive_time + (sum(segment) / len(segment))

    def get_receive_count(self) -> int:
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
        if len(self.__last_receive_intervals) > 60:
            self.__last_receive_intervals = self.__last_receive_intervals[-60:]
        self.last_receive_time = l
        HandlerRegistry.handle_reading(self.uuid, 'last_receive_time', self.last_receive_time)
        HandlerRegistry.handle_reading(self.uuid, 'next_receive_time', self.get_next_receive_time())
        HandlerRegistry.handle_reading(self.uuid, 'receive_count', self.get_receive_count())

    def handle_message(self, payload):
        """Default handling for a new message"""
        logging.warning("incoming(unhandled): %s" % payload)

    def send_message(self, payload):
        logging.warning("send_message %s" % payload)
        # A raw device has no knowledge of how to send, the sub class provides that.

    # DEPRECATE
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
    ev1527_interface = OnAir.EV1527Interface()

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

                if plugin._product_name is None: continue
                self.product_model_index[m] = plugin

                if plugin._product_id is None: continue
                if int(plugin._product_id) in self.product_id_index.keys():
                    raise Exception("Product ID already registered %d" % int(plugin._product_id))
                self.product_id_index[int(plugin._product_id)] = plugin
                logging.info("Device driver loaded \"%s\"" % m)
            except:
                logging.debug("Device driver failed to load: \"%s\"" % m)

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
