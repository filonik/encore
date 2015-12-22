import contextlib as cl

from . import accessors


@cl.contextmanager
def attrset(obj, name, value=accessors.Delete):
    value = accessors.swapattr(obj, name, value)
    try:
        yield
    finally:
        value = accessors.swapattr(obj, name, value)
    return value


@cl.contextmanager
def itemset(obj, name, value=accessors.Delete):
    value = accessors.swapitem(obj, name, value)
    try:
        yield
    finally:
        value = accessors.swapitem(obj, name, value)
    return value
