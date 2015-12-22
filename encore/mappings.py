import collections
import copy

from .accessors import getitem, setitem, delitem
from .utilities import identity, constant


class DefineMap(dict):
    def __add__(self, other):
        result = copy.copy(self)
        for key in other:
            setitem(result, key, other[key])
        return result
    
    def __sub__(self, other):
        result = copy.copy(self)
        for key in other:
            delitem(self, key)
        return result


class AttrMap(collections.MutableMapping):
    def __init__(self, mapping=None, *args, **kwargs):
        self.__dict__['_data'] = dict() if mapping is None else mapping

    def __getitem__(self, key):
        return self._data.__getitem__(key)

    def __setitem__(self, key, value):
        self._data.__setitem__(key, value)

    def __delitem__(self, key):
        self._data.__delitem__(key)

    __getattr__ = __getitem__
    __setattr__ = __setitem__
    __delattr__ = __delitem__

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return repr(self._data)


class CustomMap(collections.MutableMapping):
    def __init__(self, items=None, factory=None, key=None, *args, **kwargs):
        super(CustomMap, self).__init__(*args, **kwargs)
        
        self._data = dict()
        self._factory = constant(None) if factory is None else factory
        self._key = identity if key is None else key

        if items is not None:
            self.update(items)

    def __getitem__(self, key):
        key = self._key(key)
        if not (key in self._data):
            setitem(self._data, key, self._factory(key))
        return getitem(self._data, key)
     
    def __setitem__(self, key, value):
        key = self._key(key)
        setitem(self._data, key, value)

    def __delitem__(self, key):
        key = self._key(key)
        delitem(self._data, key)
    
    def __contains__(self, key):
        key = self._key(key)
        return key in self._data
    
    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return repr(self._data)


class LowerCaseMap(CustomMap):
    def __init__(self, items=None, factory=None):
        super(LowerCaseMap, self).__init__(items, factory=factory, key=lambda k: k.lower())


class UpperCaseMap(CustomMap):
    def __init__(self, items=None, factory=None):
        super(UpperCaseMap, self).__init__(items, factory=factory, key=lambda k: k.upper())
