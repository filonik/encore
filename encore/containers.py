import collections

from . import accessors


def is_ordered(container):
    return isinstance(container, (collections.Sequence, collections.OrderedDict))


def iterkeys(container):
    def _iterkeys(container):
        if isinstance(container, collections.Sequence):
            return iter(range(len(container)))
        if isinstance(container, collections.Mapping):
            return iter(container.keys())
        return iter([])
    result = _iterkeys(container)
    return result if is_ordered(container) else sorted(result)


def itervalues(container):
    for key in keys(container):
        yield accessors.getitem(container, key)


def iteritems(container):
    for key in keys(container):
        yield key, accessors.getitem(container, key)


def insert(container, key, value):
    if isinstance(container, collections.MutableMapping):
        return accessors.setitem(container, key, value)
    if isinstance(container, collections.MutableSequence):
        try:
            return accessors.setitem(container, key, value)
        except IndexError:
            return container.insert(key, value)
