# -*- coding: utf-8 -*-
from .. import OnAir
from .. import Registry
import os
import importlib
import time
from uuid import uuid4
import logging


class Device():
    _manufacturer_id = None
    _broadcast_id = None
    _crypt_pid = 242
    _crypt_pip = 0x0100

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
        if value is True:
            Registry.DeviceRegistry.singleton().setup_device_routing(self)
        else:
            Registry.DeviceRegistry.singleton().remove_device_routing(self)
        self._enabled = value

    @classmethod
    def describe(cls):
        return {
            'type': cls.__name__,
            'id': cls._product_id,
            'name': cls._product_name,
            'description': cls._product_description,
            'rf': cls._product_rf,
            'url': cls._product_url
        }

    @classmethod
    def header(cls):
        return {
            "mfrid": cls._manufacturer_id,
            "productid": cls._product_id,
            "encryptPIP": cls._crypt_pid,
            "sensorid": 0
        }

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
                # TODO: This is probably an error condition.
                self.air_interface = None
        self.device_id = self.parse_device_id(device_id)
        self.name = name
        self._enabled = enabled
        if uuid is None:
            uuid = str(uuid4())
        self.uuid = uuid

        class RadioConfig(): pass
        self.radio_config = RadioConfig()

        class Capabilities(): pass
        self.capabilities = Capabilities()

        self.updated_cb = None
        self.rxseq = 0
        self.lastHandledMessage = 0

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
            res = []
            for p in device_id:
                res.append(Device.parse_device_id(p))
            # TODO: could usefully convert to tuple here to be helpful
            return res

        if type(device_id) == str:
            # could be hex or decimal or strtuple or strlist
            if device_id == "":
                raise ValueError("device_id is blank, not allowed")
            elif device_id.startswith("0x"):
                return int(device_id, 16)
            elif device_id[0] == '(' and device_id[-1] == ')':
                # print("**** parse tuple")
                inner = device_id[1:-1]
                parts = inner.split(',')
                # print(parts)
                res = []
                for p in parts:
                    res.append(Device.parse_device_id(p))
                # print(res)
                return res

            elif device_id[0] == '[' and device_id[-1] == ']':
                # print("**** parse list")
                inner = device_id[1:-1]
                parts = inner.split(',')
                # print(parts)
                res = []
                for p in parts:
                    res.append(Device.parse_device_id(p))
                # TODO: could usefully change to tuple here
                # print(res)
                return res
            else:
                return int(device_id, 10)

        else:
            raise ValueError("device_id unsupported type or format, got: %s %s" % (type(device_id), str(device_id)))

    def has_switch(self):
        return hasattr(self.capabilities, "switch")

    def can_send(self):
        return hasattr(self.capabilities, "send")

    def can_receive(self):
        return hasattr(self.capabilities, "receive")

    def get_radio_config(self):
        return self.radio_config

    def get_last_receive_time(self):  # ->timestamp
        """The timestamp of the last time any message was received by this device"""
        return self.last_receive_time

    def get_next_receive_time(self):  # -> timestamp
        """An estimate of the next time we expect a message from this device"""
        pass

    def get_readings_summary(self):
        """Try to get a terse summary of all present readings"""

        try:
            r = self.readings
        except AttributeError:
            return "(no readings)"

        if r is None:
            return "(no readings)"

        def shortname(name):
            parts = name.split('_')
            sn = ""
            for p in parts:
                sn += p[0].upper()
            return sn

        line = ""
        for rname in dir(self.readings):
            if not rname.startswith("__"):
                value = getattr(self.readings, rname)
                line += "%s:%s " % (shortname(rname), str(value))

        return line

        # for each reading
        #   call get_x to get the reading
        #   think of a very short name, perhaps first letter of reading name?
        #   add it to a terse string
        # return the string

    def get_receive_count(self):
        return self.rxseq

    def incoming_message(self, payload):
        """Entry point for a message to be processed"""
        # This is the base-class entry point, don't  override this, but override handle_message
        self.rxseq += 1
        self.handle_message(payload)
        if self.updated_cb is not None:
            self.updated_cb(self, payload)
        self.lastHandledMessage = time.time()

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
        return cls.singleton().product_name_index.keys()

    def __getitem__(self, key):
        try:
            key = int(key)
        except Exception:
            pass

        if type(key) == int:
            return self.product_id_index[key]

        return self.product_name_index[key]

    @classmethod
    def get_device_from_name(cls, name, **kw_args):
        if name not in cls.keys():
            raise ValueError("Unsupported device:%s" % name)

        c = cls.singleton().product_name_index[name]
        return c(**kw_args)

    @classmethod
    def get_device_from_id(cls, id, **kw_args):
        if id not in cls.singleton().product_id_index.keys():
            raise ValueError("Unsupported device id:%s" % id)
        c = cls.singleton().product_id_index[id]
        return c(**kw_args)

    def __init__(self):
        self.product_id_index = {}
        self.product_name_index = {}

        p = os.path.dirname(os.path.abspath(__file__))
        files = os.listdir(p)
        for f in files:
            if f.startswith("__"): continue
            if not f.endswith(".py"): continue
            m = f.replace('.py', '')
            module = importlib.import_module('.' + m, 'energenie.Devices')
            try:
                plugin = getattr(module, m)
            except:
                logging.exception("Plugin failed to load, no such class \"%s\"" % m)

            self.product_id_index[plugin._product_id] = plugin
            self.product_name_index[m] = plugin
