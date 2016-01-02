import collections
import json

import contextlib as cl

from . import accessors, functions, generics, managers, utilities


@cl.contextmanager
def direct_access(obj):
    direct_getattr = managers.attrset(type(obj), "__getattr__", functions.raiser(lambda self, key: AttributeError(key)))
    direct_setattr = managers.attrset(type(obj), "__setattr__", object.__setattr__)
    direct_delattr = managers.attrset(type(obj), "__delattr__", object.__delattr__)
    with direct_getattr, direct_setattr, direct_delattr:
        yield


def combine_meta(meta, type=None):
    if type is not None:
        # Dynamic override of type
        if isinstance(meta, Meta):
            return Meta(type, attrs=meta._attrs, items=meta._items)
        else:
            return Meta(type)
    
    return meta


def dataof(obj):
    if isinstance(obj, Object):
        return obj._data
    return obj


def metaof(obj, default=None):
    def _metaof(obj):
        if isinstance(obj, Object):
            return obj._meta
        return default
    
    return combine_meta(_metaof(obj), typeof(obj))


def typeof(obj, default=None):
    if isinstance(obj, Object):
        data = dataof(obj)
        if isinstance(data, collections.Mapping):
            return data.get(obj._type_key, default)
    return default


def attrsof(obj, default=None):
    if isinstance(obj, Object):
        data = dataof(obj)
        if isinstance(data, collections.Mapping):
            return dataof(data.get(obj._attrs_key, default))
    return default

    
def itemsof(obj, default=None):
    if isinstance(obj, Object):
        data = dataof(obj)
        if isinstance(data, collections.Mapping):
            return dataof(data.get(obj._items_key, default))
    return default

    
def hastype(obj):
    return typeof(obj) is not None


def hasattrs(obj):
    return attrsof(obj) is not None


def hasitems(obj):
    return itemsof(obj) is not None


def _getattr(self, key):
    attrs = attrsof(self, dataof(self))
    if not isinstance(attrs, collections.MutableMapping):
        raise AttributeError(key)
    else:
        try:
            return accessors.getitem(attrs, key)
        except KeyError:
            raise AttributeError(key)
    
    
def _setattr(self, key, value):
    attrs = attrsof(self, dataof(self))
    if not isinstance(attrs, collections.MutableMapping):
        accessors.setitem(self.__dict__, key, value)
    else:
        if key in self.__dict__:
            accessors.setitem(self.__dict__, key, value)
        else:
            accessors.setitem(attrs, key, value)


def _delattr(self, key):
    attrs = attrsof(self, dataof(self))
    if not isinstance(attrs, collections.MutableMapping):
        accessors.delitem(self.__dict__, key)
    else:
        if key in self.__dict__:
            accessors.delitem(self.__dict__, key)
        else:
            accessors.delitem(attrs, key)


def _getitem(self, key):
    items = itemsof(self, dataof(self))
    return accessors.getitem(items, key)


def _setitem(self, key, value):
    items = itemsof(self, dataof(self))
    accessors.setitem(items, key, value)


def _delitem(self, key, value):
    items = itemsof(self, dataof(self))
    accessors.delitem(items, key)


def type_to_string(obj):
    if isinstance(obj, type):
        return obj.__qualname__
    return obj
    

def string_to_type(obj):
    if isinstance(obj, str):
        parts = obj.split('.')
        module_name, class_name = parts[:-1], parts[-1]
        if module_name:
            module_name = ".".join(module_name)
            m = __import__(module_name, globals(), locals(), class_name)
            c = accessors.getattr(m, class_name)
        else:
            c = accessors.getitem(globals(), class_name)
        return c
    return obj


def disambiguate_meta(meta):
    # Possibilities:
    # 1) isinstance(meta, Meta) -> Full meta information
    # 2) not isinstance(meta, Meta) and meta is not None -> No meta information, custom conversion function
    # 3) not isinstance(meta, Meta) and meta is None -> No meta information, default conversion
    
    if isinstance(meta, Meta):
        func_ = utilities.identity
        meta_ = meta
    else:
        func_ = utilities.identity if meta is None else meta
        meta_ = Meta()
    
    return meta_, func_

def _reify(obj, meta=None):
    if isinstance(obj, Object):
        obj = obj.cast(meta)
            
    meta = metaof(obj, meta)
    
    if meta._type is not None:
        result = meta._type()
        setstate(result, obj)
        return result
    else:
        result = dataof(obj)
        
        if isinstance(result, collections.Sequence) and not isinstance(result, str):
            result = type(result)(reify(value, meta=itemmeta(meta)) for value in result)
        
        if isinstance(result, collections.Mapping):
            result = type(result)((key, reify(value, meta=itemmeta(meta, key))) for key, value in result.items())
        
        return result


def reify(obj, meta=None):
    meta_, func_ = disambiguate_meta(meta)
    
    #print("reify", obj, meta_, func_)
    
    return func_(_reify(obj, meta_))


def defaultsetstate(self, other):
    data = dataof(other)
    attrs = attrsof(other)
    items = itemsof(other)
    
    if attrs is None and items is None:
        for key in data:
            #print("setattr", key, getattr(other, key))
            setattr(self, key, accessors.getattr(other, key))
        
    if attrs is not None:
        if isinstance(attrs, collections.Sequence):
            for key in range(len(attrs)):
                self.append(accessors.getattr(other, key))
        else:
            for key in attrs:
                #print("setattr", key, getattr(other, key))
                setattr(self, key, accessors.getattr(other, key))
    
    if items is not None:
        if isinstance(items, collections.Sequence):
            for key in range(len(items)):
                self.append(accessors.getitem(other, key))
        else:
            for key in items:
                #print("setitem", key, getitem(data, key))
                setitem(self, key, accessors.getitem(other, key))


def setstate(self, other):
    _setstate = accessors.getattr(type(self), "__setstate__", defaultsetstate)
    _setstate(self, other)


class Meta(object):
    def __init__(self, type=None, attrs=None, items=None):
        super().__init__()
        
        self._type = string_to_type(type)
        self._attrs = attrs
        self._items = items
    
    def __call__(self, data):
        return reify(data, meta=self)
    
    def __repr__(self):
        return "Meta{{{}}}".format(repr(self._type))
    
    def __str__(self):
        return "Meta{{{}}}".format(", ".join(map(repr, filter(None, [self._type, self._attrs, self._items]))))


def attrmeta(self, key=None):
    meta, _ = disambiguate_meta(self)
    if isinstance(meta._attrs, collections.Mapping):
        return meta._attrs.get(key)
    return meta._attrs


def itemmeta(self, key=None):
    meta, _ = disambiguate_meta(self)
    if isinstance(meta._items, collections.Mapping):
        return meta._items.get(key)
    return meta._items

    
class Object(object):
    _type_key = "type"
    _attrs_key = "attrs"
    _items_key = "items"
    
    def __init__(self, data=None, meta=None):
        super().__init__()
        
        with direct_access(self):
            self._data = data
            self._meta = meta

    def __getstate__(self):
        return self._data
    
    def __setstate__(self, data):
        self._data = data
    
    def __getattr__(self, key):
        value = _getattr(self, key)
        return reify(value, meta=attrmeta(metaof(self), key))
        
    def __setattr__(self, key, value):
        _setattr(self, key, value)
        
    def __delattr__(self, key):
        _delattr(self, key, value)
    
    def __getitem__(self, key):
        value = _getitem(self, key)
        return reify(value, meta=itemmeta(metaof(self), key))
    
    def __setitem__(self, key, value):
        _setitem(self, key, value)
        
    def __delitem__(self, key):
        _delitem(self, key)
    
    def insert(self, key, value):
        items = itemsof(self, dataof(self))
        
        if isinstance(items, collections.MutableSequence):
            items.insert(key, value)
        else:
            accessors.setitem(items, key, value)
        
    def __iter__(self):
        items = itemsof(self, dataof(self))
        
        if isinstance(items, collections.MutableSequence):
            return iter(reify(item, meta=itemmeta(metaof(self))) for item in items)
        else:
            return iter(items)
    
    def __len__(self):
        items = itemsof(self, dataof(self))
        return len(items)
    
    def cast(self, meta):
        return Object(self._data, meta)
    
    def __repr__(self):
        return "Object({})".format(repr(self._data))
        
    def __str__(self):
        return "Object({})".format("".join(map(str, filter(None, [typeof(self), attrsof(self), itemsof(self)]))))


class ObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Object):
            return obj.__getstate__()
        return json.JSONEncoder.default(self, obj)


class ObjectDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        object_hook = kwargs.pop("object_hook", utilities.identity)
        object_pairs_hook = kwargs.pop("object_pairs_hook", utilities.identity)
        
        def _object_hook(data):
            result = Object()
            result.__setstate__(data)
            return result
        
        kwargs["object_hook"] = lambda data: _object_hook(object_hook(data))
        kwargs["object_pairs_hook"] = lambda data: _object_hook(object_pairs_hook(data))
        
        super().__init__(*args, **kwargs)


def save_object(data, meta=None):
    return json.dumps(data, cls=ObjectEncoder)


def load_object(data, meta=None):
    return json.loads(data, cls=ObjectDecoder, object_pairs_hook=collections.OrderedDict)


def save(data, meta=None):
    return save_object(data, meta=meta)


def load(data, meta=None):
    data = load_object(data, meta=meta)
    return reify(data, meta=meta)

    
def save_file(file, data, meta=None):
    json.dump(data, file, cls=ObjectEncoder)


def load_file(file, meta=None):
    data = json.load(file, cls=ObjectDecoder, object_pairs_hook=collections.OrderedDict)
    return reify(data, meta=meta)


def save_path(path, data, meta=None):
    with open(path, 'w') as file:
        json.dump(data, file, cls=ObjectEncoder)


def load_path(path, meta=None):
    with open(path, 'r') as file:
        data = json.load(file, cls=ObjectDecoder, object_pairs_hook=collections.OrderedDict)
        return reify(data, meta=meta)
