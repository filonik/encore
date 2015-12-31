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
    
    
def deep_coerce_tuple(obj):
    if isinstance(obj, collections.Mapping):
        return tuple(deep_coerce_tuple(i) for i in obj.items())
    elif isinstance(obj, collections.Iterable) and not isinstance(obj, str):
        return tuple(deep_coerce_tuple(i) for i in obj)
    else:
        return obj


def deep_coerce_list(obj):
    if isinstance(obj, collections.Mapping):
        return list(deep_coerce_list(i) for i in obj.items())
    if isinstance(obj, collections.Iterable) and not isinstance(obj, str):
        return list(deep_coerce_list(i) for i in obj)
    else:
        return obj
