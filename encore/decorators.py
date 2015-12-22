import functools as ft

from . import coercions, indexers


def attrcached(attr):
    def decorator(func):
        @ft.wraps(func)
        def decorated(obj, *args, **kwargs):
            if not hasattr(obj, attr):
                setattr(obj, attr, func(obj, *args, **kwargs))
            return getattr(obj, attr)
        return decorated
    return decorator


class Indexed(object):
    def __init__(self, function):
        self._function = function
    def __getitem__(self, key):
        args = coercions.coerce_tuple(key)
        return self._function(*args)

indexed = Indexed


class UniversalProperty(object):
    def __init__(self, fget=None):
        super().__init__()
        
        self.fget = fget
    
    def __get__(self, obj, cls=None):
        if cls is None:
            cls = type(obj)
        
        return self.fget(cls, obj)

universalproperty = UniversalProperty


def universalbound(func):
    def decorator(cls, obj):
        @ft.wraps(func)
        def decorated(*args, **kwargs):
            return func(cls, obj, *args, **kwargs)
        return decorated
    return decorator


def universalmethod(func):
    return universalproperty(universalbound(func))


class IndexedProperty(object):
    _indexer_type = indexers.Indexer

    def __init__(self, fget=None, fset=None, fdel=None, fitr=None, flen=None, name=None):
        super().__init__()
        
        self._name = name

        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.fitr = fitr
        self.flen = flen

    @property
    def name(self):
        return self._name or self.fget.__name__

    @property
    def attr(self):
        return '__cached_%s_indexer' % (self.name,)

    def __get__(self, obj, cls=None):
        @attrcached(self.attr)
        def _get(obj):
            return self._indexer_type(obj, cls, self.name, self.fget, self.fset, self.fdel, self.fitr, self.flen)

        if obj is not None:
            return _get(obj)
        elif cls is not None:
            return self
        else:
            raise ValueError("%s: Cannot get without 'obj' or 'cls'."  % (self,))

    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.fitr, self.flen)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.fitr, self.flen)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.fitr, self.flen)

    def iterator(self, fitr):
        return type(self)(self.fget, self.fset, self.fdel, fitr, self.flen)

    def length(self, flen):
        return type(self)(self.fget, self.fset, self.fdel, self.fitr, flen)


indexedproperty = IndexedProperty


def flyweight(cls):
    _old_cls_new = cls.__new__

    @classmethod
    def _new_cls_new(cls, *args, **kargs):
        return cls.__instances.setdefault((args, tuple(kargs.items())), _old_cls_new(*args, **kargs))

    cls.__instances = dict()
    cls.__new__ = _new_cls_new
    return cls


def log(logger, level):
    def _decorator(func):
        @ft.wraps(func)
        def _decorated(*args,**kwargs):
            logger.log(level, "%s(%r,%r)", func.__name__ , args, kwargs)
            result = func(*args,**kwargs)
            logger.log(level, "%s(%r,%r) -> %r", func.__name__ , args, kwargs, result)
            return result
        return _decorated
    return _decorator
