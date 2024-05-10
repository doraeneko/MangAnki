######################################################################
# Manganki
# Anki plugin to help with vocab mining of online mangas
# Copyright 2024, Andreas Gaiser
######################################################################
# Resource represents a single data element; listeners can
# be added that are notified when the value is changing.
# Resources represents a dictionary for access to resources.
######################################################################

import typing

from aqt.qt import *
from PyQt6.QtGui import QImage

try:
    from .dict_lookup import DictionaryLookup, DictionaryEntry

    from . import dict_lookup
except:
    from dict_lookup import DictionaryLookup
    import dict_lookup


class Resource:
    def __init__(self, name, initial_value):
        self._name = name
        self._value = initial_value
        self._listeners = []

    def add_listener(self, listener: typing.Callable):
        self._listeners.append(listener)

    def get_value(self):
        return self._value

    def set_value(self, new_value):
        if new_value != self._value:
            print(
                "Set value of %s to %s, old value: %s."
                % (self._name, new_value, self._value)
            )
            self._value = new_value
            for listener in self._listeners:
                listener()


class Resources:
    """Dictionary for resources. Access can be either done via index notation (resource['MyResource'])
    or via dot notation (resource.MyResource). Register listeners using add_listener() method."""

    def __init__(self, res_dict: typing.Dict[str, typing.Any]):
        self._resources: typing.Dict[str, Resource] = {}
        for resource_name, init_value in res_dict.items():
            self._resources[resource_name] = Resource(resource_name, init_value)

    def __getitem__(self, item):
        return self._resources[item].get_value()

    def __setitem__(self, key, value):
        self._resources[key].set_value(value)

    def __getattr__(self, name):
        if name in self._resources:
            return self._resources[name].get_value()
        else:
            raise AttributeError(
                "'"
                + self.__class__.__name__
                + "' object has no attribute '"
                + name
                + "'"
            )

    def __setattr__(self, name, value):
        if name == "_resources":
            super().__setattr__(name, value)
        elif name in self._resources:
            self._resources[name].set_value(value)
        else:
            raise AttributeError(
                "'"
                + self.__class__.__name__
                + "' object has no attribute '"
                + name
                + "'"
            )

    def add_listener(self, resource, listener):
        self._resources[resource].add_listener(listener)
