import collections
import json

import contextlib as cl

from . import functions, generics, managers


@cl.contextmanager
def direct_access(obj):
    direct_getattr = managers.attrset(type(obj), "__getattr__", functions.raiser(lambda self, key: AttributeError(key)))
    direct_setattr = managers.attrset(type(obj), "__setattr__", object.__setattr__)
    direct_delattr = managers.attrset(type(obj), "__delattr__", object.__delattr__)
    with direct_getattr, direct_setattr, direct_delattr:
        yield


def _getattr(self, key):
    try:
        return self._data[key]
    except KeyError:
        raise AttributeError(key)


def _setattr(self, key, value):
    if key in self.__dict__:
        self.__dict__[key] = value
    else:
        self._data[key] = value


def _delattr(self, key):
    if key in self.__dict__:
        del self.__dict__[key]
    else:
        del self._data[key]


class Object(object):
    """ Quick and dirty serializable objects. """
    def __init__(self, data=None, parent=None):
        super().__init__()
        
        with direct_access(self):
            self._parent = parent
            self._data = {} if data is None else data
    
    __getattr__ = _getattr
    __setattr__ = _setattr
    __delattr__ = _delattr
    
    def save(self):
        return self._data
        
    def load(self, data):
        self._data = data


@generics.generic
class Sequence(collections.MutableSequence):
    _items_cls = generics.parameter(0, generics.Self)
    _items_key = "items"
    
    @property
    def _items(self):
        return self._data[self._items_key]
    
    def __init__(self, data=None, parent=None):
        super().__init__()
        
        with direct_access(self):
            self._parent = parent
            self._data = {} if data is None else data
            self._data.setdefault(self._items_key, [])
        
    __getattr__ = _getattr
    __setattr__ = _setattr
    __delattr__ = _delattr
    
    def save(self):
        return self._data
        
    def load(self, data):
        self._data = data
    
    def _wrap_item(self, data):
        return self._items_cls(data, parent=self)
    
    def _unwrap_item(self, item):
        return item._data
    
    def __contains__(self, key):
        return key in self._items
    
    def __getitem__(self, key):
        return self._wrap_item(self._items[key])
    
    def __setitem__(self, key, value):
        self._items[key] = self._unwrap_item(value)
    
    def __delitem__(self, key):
        del self._items[key]
    
    def __len__(self):
        return len(self._items)
    
    def insert(self, key, value):
        self._items.insert(key, self._unwrap_item(value))


@generics.generic
class Mapping(collections.MutableMapping):
    _items_cls = generics.parameter(0, generics.Self)
    _items_key = "items"
    
    @property
    def _items(self):
        return self._data[self._items_key]
    
    def __init__(self, data=None, parent=None):
        super().__init__()
        
        with direct_access(self):
            self._parent = parent
            self._data = {} if data is None else data
            self._data.setdefault(self._items_key, {})
    
    __getattr__ = _getattr
    __setattr__ = _setattr
    __delattr__ = _delattr
    
    def save(self):
        return self._data
        
    def load(self, data):
        self._data = data
    
    def _wrap_item(self, data):
        return self._items_cls(data, parent=self)
    
    def _unwrap_item(self, item):
        return item._data
    
    def __contains__(self, key):
        return key in self._items
    
    def __getitem__(self, key):
        return self._wrap_item(self._items[key])
    
    def __setitem__(self, key, value):
        self._items[key] = self._unwrap_item(value)
    
    def __delitem__(self, key):
        del self._items[key]
    
    def __len__(self):
        return len(self._items)
        
    def __iter__(self):
        return iter(self._items)


def load_json(obj, path):
    with open(path, 'r') as file:
        data = json.load(file, object_pairs_hook=collections.OrderedDict)
        obj.load(data)


def save_json(obj, path):
    with open(path, 'w') as file:
        data = obj.save()
        json.dump(data, file)