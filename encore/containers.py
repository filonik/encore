import collections

from . import accessors, iterables


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
    for key in iterkeys(container):
        yield accessors.getitem(container, key)


def iteritems(container):
    for key in iterkeys(container):
        yield key, accessors.getitem(container, key)


def index(container, key):
    if isinstance(container, collections.Sequence):
        return key
    if isinstance(container, collections.Mapping):
        return list(iterkeys(container)).index(key)


def key(container, index):
    if isinstance(container, collections.Sequence):
        return index
    if isinstance(container, collections.Mapping):
        return iterables.nth(iterkeys(container), index)


def insert(container, key, value):
    if isinstance(container, collections.MutableMapping):
        return accessors.setitem(container, key, value)
    if isinstance(container, collections.MutableSequence):
        try:
            return accessors.setitem(container, key, value)
        except IndexError:
            return container.insert(key, value)


def remove(container, key):
    return accessors.delitem(container, key)
