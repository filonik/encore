import sys

import functools as ft

from . import accessors, coercions, decorators, utilities


Self = utilities.unique_instance("Self")


def _unself(obj, value):
    return value if obj is Self else obj


'''
def mangle(cls, parameters):
    def _str(obj):
        obj = _unself(obj, cls)
        return getattr(obj, '__name__', repr(obj))
    return "_".join(map(_str, (cls,) + parameters))
'''
def mangle(cls, parameters):
    uid = hex(hash(parameters) + sys.maxsize + 1)
    return "_".join([cls.__name__, uid])


class GenericClassFactory(object):
    def __init__(self, cls):
        super().__init__()
        
        self._cls = cls
        self._instantiations = {}
    
    def __getitem__(self, key):
        parameters = coercions.coerce_tuple(key)
        name = mangle(self._cls, parameters)
        try:
            new_cls = self._instantiations[name]
        except KeyError:
            new_cls = self._instantiations[name] = type(name, (self._cls,), {"_parameters": parameters})
        return new_cls
    
    def __call__(self, *args, **kwargs):
        return self._cls(*args, **kwargs)
    
    def __repr__(self):
        return repr(self._cls)
    
    def __str__(self):
        return str(self._cls)


def generic(cls):
    return GenericClassFactory(cls)


def latebind(func):
    @ft.wraps(func)
    def decorator(*args, **kwargs):
        def decorated(*parameters):
            return func[parameters](*args, **kwargs)
        return decorators.indexed(decorated)
    return decorator


def parameter(key, default=None):
    @decorators.universalproperty
    def _parameter(cls, obj):
        return _unself(accessors.getitem(cls._parameters, key, default), cls)
    return _parameter
