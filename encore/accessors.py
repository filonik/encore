from builtins import hasattr, getattr, setattr, delattr

from . import utilities

Create = utilities.unique_instance("Create")
Update = utilities.unique_instance("Update")
Delete = utilities.unique_instance("Delete")

AttrErrors = (TypeError, AttributeError)
ItemErrors = (TypeError, KeyError, IndexError)

iterattrs = utilities.compose(iter, dir)
lenattrs = utilities.compose(len, dir)


def hasitem(obj, key):
    try:
        obj[key]
    except ItemErrors:
        return False
    else:
        return True


def getitem(obj, key, default=utilities.Unspecified):
    if utilities.specified(default):
        try:
            return obj[key]
        except ItemErrors:
            return default
    else:
        return obj[key]


def setitem(obj, key, value):
    obj[key] = value


def delitem(obj, key):
    try:
        del obj[key]
    except ItemErrors:
        pass


def iteritems(obj):
    try:
        return iter(obj)
    except TypeError:
        return iter(())


def lenitems(obj):
    try:
        return len(obj)
    except TypeError:
        return 0


def swapattr(obj, name, value):
    result = getattr(obj, name, Delete)
    if value is Delete:
        delattr(obj, name)
    else:
        setattr(obj, name, value)
    return result


def swapitem(obj, name, value):
    result = getitem(obj, name, Delete)
    if value is Delete:
        delitem(obj, name)
    else:
        setitem(obj, name, value)
    return result


def lazy_setdefaultattr(obj, key, default):
    try:
        return getattr(obj, key)
    except AttrErrors:
        result = default()
        setattr(obj, key, result)
        return result


def lazy_setdefaultitem(obj, key, default):
    try:
        return getitem(obj, key)
    except ItemErrors:
        result = default()
        setitem(obj, key, result)
        return result


def setdefaultattr(obj, key, default):
    return lazy_setdefaultattr(obj, key, utilities.constant(default))


def setdefaultitem(obj, key, default):
    return lazy_setdefaultitem(obj, key, utilities.constant(default))
