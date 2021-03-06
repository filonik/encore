import functools as ft
import itertools as it

from .functions import constant, counter, raiser


def identity(obj):
    return obj


def foldl(func, seq, *args):
    return ft.reduce(func, seq, *args)


def foldr(func, seq, *args):
    return ft.reduce(lambda x,y: func(y,x), reversed(seq), *args)


def compose(*funcs):
    def _compose(f, g):
        return lambda *args, **kwargs: f(g(*args, **kwargs))
    return ft.reduce(_compose, funcs)


def product_range(lower, upper):
    n = min(len(lower), len(upper))
    for index in it.product(*[range(lower[i], upper[i]) for i in range(n)]):
        yield index


def unique_instance(name, truth=True):
    cls = type(name, (object,), {'__bool__': lambda self: truth, '__repr__': lambda self: name, '__str__': lambda self: name})
    return cls()


Undefined = unique_instance("Undefined", False)
Unspecified = unique_instance("Unspecified", False)


def defined(obj):
    return obj is not Undefined

    
def specified(obj):
    return obj is not Unspecified

    
def getdefined(obj, default=None):
    return obj if defined(obj) else default


def getspecified(obj, default=None):
    return obj if specified(obj) else default


def truncate(value, n, indicator=None):
    if indicator is None:
        return (value[:n]) if len(value) > n else value
    else:
        return (value[:n] + indicator) if len(value) > n else value


class Bits(object):
    @property
    def mask(self):
        return ((1 << self.size) - 1) << self.offset
    
    def __init__(self, size, offset):
        self.size = size
        self.offset = offset
    
    def decode(self, value):
        return (value & self.mask) >> self.offset
    
    def encode(self, value):
        return (value << self.offset) & self.mask
