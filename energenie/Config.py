import os
import json
from copy import copy
import logging

search_config = [
    "/etc/pyenergenie/config.json",
    "/opt/venvs/pyenergenie/config/config.json",
    "~/.pyenergenie/config.json",

    # This is for testing only
    "data/config.json"
]


class Config:
    __single = None

    @classmethod
    def singleton(cls):
        if cls.__single is None:
            cls.__single = cls()
        return cls.__single

    def __init__(self):
        self.__preferences = {}
        self.__command_line = {}
        self.writable = None
        self.readable = None

        for path in search_config:
            path = os.path.expanduser(path)
            path = os.path.abspath(path)
            if os.path.exists(path) and os.access(path, os.W_OK) and self.writable is None:
                self.writable = path

            if os.path.exists(path) and self.readable is None:
                self.readable = path

            if not os.path.exists(path) and self.writable is None:
                dir = os.path.dirname(path)
                if (os.access(dir, os.W_OK)):
                    self.writable = path
                elif os.access(os.path.dirname(dir), os.W_OK):
                    self.writable = path

            if self.readable and self.writable:
                break

        if self.writable != self.readable:
            self.load(self.readable)

        self.load(self.writable)

    def __del__(self):
        self.save()

    def __getitem__(self, k):
        if k in self.__command_line.keys():
            return self.__command_line[k]
        elif k in self.__preferences.keys():
            return self.__preferences[k]

        return None

    def __setitem__(self, k, v):
        self.__preferences[k] = v

    def load_command_line_args(self, args):
        pass

    def apply_command_line_args(self):
        pass

    def save(self, filename=None):
        if filename is None:
            filename = self.writable
        dir = os.path.dirname(filename)
        if not os.path.exists(dir):
            os.makedirs(dir)
        with open(filename, 'wt') as f:
            f.write(json.dumps(self.__preferences, indent=4, sort_keys=True))

    def load(self, filename):
        with open(filename) as f:
            self.__preferences = json.loads(f.read())
