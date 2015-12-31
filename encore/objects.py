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


def wrap_attr(self, value):
    if self._attr_cls is None:
        return value
    else:
        return self._attr_cls(value, parent=self)


def unwrap_attr(self, value):
    try:
        return value._data
    except AttributeError:
        return value


def wrap_item(self, value):
    if self._item_cls is None:
        return value
    else:
        return self._item_cls(value, parent=self)


def unwrap_item(self, value):
    try:
        return value._data
    except AttributeError:
        return value


def _getattr(self, key):
    if self._attrs is None:
        raise AttributeError(key)
    else:
        try:
            return self._wrap_attr(self._attrs[key])
        except KeyError:
            raise AttributeError(key)


def _setattr(self, key, value):
    if self._attrs is None:
        self.__dict__[key] = value
    else:
        if key in self.__dict__:
            self.__dict__[key] = value
        else:
            self._attrs[key] = self._unwrap_attr(value)


def _delattr(self, key):
    if self._attrs is None:
        del self.__dict__[key]
    else:
        if key in self.__dict__:
            del self.__dict__[key]
        else:
            del self._attrs[key]


def _getitem(self, key):
    return self._wrap_item(self._items[key])


def _setitem(self, key, value):
    self._items[key] = self._unwrap_item(value)


def _delitem(self, key):
    del self._items[key]


def getattrs(obj, default=None):
    try:
        return obj._attrs
    except AttributeError:
        return default


def getitems(obj, default=None):
    try:
        return obj._items
    except AttributeError:
        return default


@generics.generic
class Object(object):
    _attr_cls = generics.parameter(0)
    _attrs_cls = generics.parameter(1, dict)
    
    _type_key = "type"
    _attrs_key = "attrs"
   
    @property
    def _type(self):
        return self._data[self._type_key]
    
    @property
    def _attrs(self):
        return self._data[self._attrs_key]
    
    def __init__(self, data=None, parent=None):
        super().__init__()
        
        with direct_access(self):
            self._parent = parent
            self._data = {} if data is None else data
            self._data.setdefault(self._attrs_key, self._attrs_cls())
    
    _wrap_attr = wrap_attr
    _unwrap_attr = unwrap_attr
    
    __getattr__ = _getattr
    __setattr__ = _setattr
    __delattr__ = _delattr
    
    def save(self):
        return self._data
        
    def load(self, data):
        self._data = data
    
    def __str__(self):
        return "".join(map(str, filter(None, [self._type, self._attrs])))


@generics.generic
class Sequence(collections.MutableSequence):
    _item_cls = generics.parameter(0)
    _items_cls = generics.parameter(1, list)
    
    _attr_cls = generics.parameter(2)
    _attrs_cls = generics.parameter(3, dict)

    _type_key = "type"
    _attrs_key = "attrs"
    _items_key = "items"
   
    @property
    def _type(self):
        return self._data[self._type_key]
    
    @property
    def _attrs(self):
        return self._data[self._attrs_key]
    
    @property
    def _items(self):
        return self._data[self._items_key]
    
    def __init__(self, data=None, parent=None):
        super().__init__()
        
        with direct_access(self):
            self._parent = parent
            self._data = {} if data is None else data
            self._data.setdefault(self._attrs_key, self._attrs_cls())
            self._data.setdefault(self._items_key, self._items_cls())
    
    _wrap_attr = wrap_attr
    _unwrap_attr = unwrap_attr
    
    __getattr__ = _getattr
    __setattr__ = _setattr
    __delattr__ = _delattr
    
    _wrap_item = wrap_item
    _unwrap_item = unwrap_item
    
    __getitem__ = _getitem
    __setitem__ = _setitem
    __delitem__ = _delitem
    
    def __contains__(self, key):
        return key in self._items
    
    def __len__(self):
        return len(self._items)
    
    def insert(self, key, value):
        self._items.insert(key, self._unwrap_item(value))
    
    def save(self):
        return self._data
        
    def load(self, data):
        self._data = data
    
    def __str__(self):
        return "".join(map(str, filter(None, [self._type, self._attrs, self._items])))


@generics.generic
class Mapping(collections.MutableMapping):
    _item_cls = generics.parameter(0)
    _items_cls = generics.parameter(1, dict)
    
    _attr_cls = generics.parameter(2)
    _attrs_cls = generics.parameter(3, dict)
    
    _type_key = "type"
    _attrs_key = "attrs"
    _items_key = "items"
   
    @property
    def _type(self):
        return self._data[self._type_key]
    
    @property
    def _attrs(self):
        return self._data[self._attrs_key]
    
    @property
    def _items(self):
        return self._data[self._items_key]
    
    def __init__(self, data=None, parent=None):
        super().__init__()
        
        with direct_access(self):
            self._parent = parent
            self._data = {} if data is None else data
            self._data.setdefault(self._attrs_key, self._attrs_cls())
            self._data.setdefault(self._items_key, self._items_cls())
    
    _wrap_attr = wrap_attr
    _unwrap_attr = unwrap_attr
    
    __getattr__ = _getattr
    __setattr__ = _setattr
    __delattr__ = _delattr
    
    _wrap_item = wrap_item
    _unwrap_item = unwrap_item
    
    __getitem__ = _getitem
    __setitem__ = _setitem
    __delitem__ = _delitem
    
    def __contains__(self, key):
        return key in self._items
    
    def __len__(self):
        return len(self._items)
        
    def __iter__(self):
        return iter(self._items)
    
    def save(self):
        return self._data
        
    def load(self, data):
        self._data = data
    
    def __str__(self):
        return "".join(map(str, filter(None, [self._type, self._attrs, self._items])))


def load_json(obj, path):
    with open(path, 'r') as file:
        data = json.load(file, object_pairs_hook=collections.OrderedDict)
        obj.load(data)


def save_json(obj, path):
    with open(path, 'w') as file:
        data = obj.save()
        json.dump(data, file)