import collections


def coerce_tuple(obj):
    if isinstance(obj, tuple):
        return obj
    if isinstance(obj, collections.Iterable) and not isinstance(obj, str):
        return tuple(obj)
    return tuple([obj])


def coerce_list(obj):
    if isinstance(obj, tuple):
        return obj
    if isinstance(obj, collections.Iterable) and not isinstance(obj, str):
        return list(obj)
    return list([obj])