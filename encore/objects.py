import sys

import collections
import contextlib as cl

import json

from . import accessors, defaults, functions, managers, utilities


@cl.contextmanager
def direct_access(obj):
    direct_getattr = managers.attrset(type(obj), "__getattr__", functions.raiser(lambda self, key: AttributeError(key)))
    direct_setattr = managers.attrset(type(obj), "__setattr__", object.__setattr__)
    direct_delattr = managers.attrset(type(obj), "__delattr__", object.__delattr__)
    with direct_getattr, direct_setattr, direct_delattr:
        yield


def type_to_str(obj):
    if isinstance(obj, type):
        return obj.__qualname__
    return obj
    

def str_to_type(obj):
    if isinstance(obj, str):
        parts = obj.rsplit('.', 1)
        if len(parts) > 1:
            m = __import__(parts[0], globals(), locals(), parts[1])
        else:
            m =  sys.modules['__main__']
        c = accessors.getattr(m, parts[-1])
        return c
    return obj


def is_primitive(data):
    return isinstance(data, (type(None), bool, int, float, str))


def is_sequence(data):
    return isinstance(data, collections.Sequence)


def is_mapping(data):
    return isinstance(data, collections.Mapping)


def is_object(data):
    return isinstance(data, Object)


def encode_builtin(data, codec):
    def _encode_builtin(data, codec):
        if is_primitive(data):
            return data
        
        if is_sequence(data):
            return type(data)(_encode(value, codec.item()) for value in data)
        
        if is_mapping(data):
            return type(data)((key, _encode(value, codec.item(key))) for key, value in data.items())
        
        raise ValueError(type(data).__name__)
    
    return Object(data=(_encode_builtin(data, codec)))


def decode_builtin(data, codec):
    def _decode_builtin(data, codec):
        if is_primitive(data):
            return data
        
        if is_sequence(data):
            return type(data)(_decode(value, codec.item()) for value in data)
        
        if is_mapping(data):
            return type(data)((key, _decode(value, codec.item(key))) for key, value in data.items())
        
        raise ValueError(type(data).__name__)

    return _decode_builtin(dataof(data), codec)


def _encode(data, codec):
    #print("encode", data, codec)
    type_ = type(data)
    type_str_ = None if type_ is codec.type else type_
    type_str_ = type_to_str(type_str_)
    getstate = accessors.getattr(type_, "__getstate__", None)
    if getstate is not None:
        result = Object(type=type_str_, attrs={}, items={})
        getstate(data, View(result, codec))
        return result
    else:
        return encode_builtin(data, codec)
        
    raise ValueError(type(data).__name__)


def _decode(data, codec):
    #print("decode", data, codec)
    type_str_ = typeof(data, codec.type)
    type_ = str_to_type(type_str_)
    setstate = accessors.getattr(type_, "__setstate__", None)
    if setstate is not None:
        result = type_()
        setstate(result, View(data, codec))
        return result
    else:
        return decode_builtin(data, codec)
    
    raise ValueError(type(data).__name__)


class CodecBase(object):
    _default_key = "*"
    
    def __init__(self, type=None, attrs=None, items=None, encode=None, decode=None):
        super().__init__()
        
        self.type = type
        self.attrs = attrs
        self.items = items
        
        self.encode = utilities.identity if encode is None else encode
        self.decode = utilities.identity if decode is None else decode

    def attr(self, key=None):
        def _attr(self, key=None):
            if isinstance(self.attrs, collections.Mapping):
                default = self.attrs.get(self._default_key)
                return self.attrs.get(key, default)
            
            return self.attrs
        
        result = _attr(self, key=key)
        return Codec() if result is None else result
    
    def item(self, key=None):
        def _item(self, key=None):
            if isinstance(self.items, collections.Mapping):
                default = self.items.get(self._default_key)
                return self.items.get(key, default)
            
            return self.items
        
        result = _item(self, key=key)
        return Codec() if result is None else result


class Codec(CodecBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        def encode(func):
            return lambda data: _encode(func(data), self)
        
        def decode(func):
            return lambda data: func(_decode(data, self))
        
        self.encode = encode(self.encode)
        self.decode = decode(self.decode)
        
        
class View(object):
    def __init__(self, value, codec):
        super().__init__()
        
        with direct_access(self):
            self._value = value
            self._codec = codec
        
    def __getattr__(self, key):
        codec = self._codec.attr(key)
        value = accessors.getattr(self._value, key)
        return codec.decode(value)
        
    def __setattr__(self, key, value):
        codec = self._codec.attr(key)
        value = codec.encode(value)
        accessors.setattr(self._value, key, value)
        
    def __delattr__(self, key):
        accessors.delattr(self._value, key)
    
    def __getitem__(self, key):
        codec = self._codec.item(key)
        value = accessors.getitem(self._value, key)
        return codec.decode(value)
        
    def __setitem__(self, key, value):
        codec = self._codec.item(key)
        value = codec.encode(value)
        accessors.setitem(self._value, key, value)
    
    def __delitem__(self, key):
        accessors.delitem(self._value, key)
    
    def __len__(self):
        return len(self._value)
    
    def insert(self, key, value):
        codec = self._codec.item(key)
        value = codec.encode(value)
        self._value.insert(key, value)
    
    def append(self, value):
        self.insert(len(self), value)
    
    def __repr__(self):
        return repr(self._value)
    
    def __str__(self):
        return str(self._value)


def dataof(obj):
    if isinstance(obj, Object):
        return obj._data
    if isinstance(obj, View):
        return dataof(obj._value)
    return obj


def typeof(obj, default=None):
    return dataof(accessors.getitem(dataof(obj), Object._type_key, default))


def attrsof(obj, default=None):
    return dataof(accessors.getitem(dataof(obj), Object._attrs_key, default))


def itemsof(obj, default=None):
    return dataof(accessors.getitem(dataof(obj), Object._items_key, default))


getdata = dataof
getattrs = attrsof
getitems = itemsof


def setdata(obj, value):
    if isinstance(obj, Object):
        obj.__dict__["_data"] = value
    if isinstance(obj, View):
        setdata(obj._value, value)


def setattrs(obj, value):
    accessors.setitem(dataof(obj), Object._attrs_key, value)


def setitems(obj, value):
    accessors.setitem(dataof(obj), Object._items_key, value)


def delattrs(obj):
    accessors.delitem(dataof(obj), Object._attrs_key)


def delitems(obj):
    accessors.delitem(dataof(obj), Object._items_key)


def attrproperty(key, default=utilities.Unspecified):
    def fget(self):
        return accessors.getitem(attrsof(self), key, default)
    def fset(self, value):
        accessors.setitem(attrsof(self), key, value)
    def fdel(self):
        accessors.delitem(attrsof(self), key)
    return property(fget, fset, fdel)


def itemproperty(key, default=utilities.Unspecified):
    def fget(self):
        return accessors.getitem(itemsof(self), key, default)
    def fset(self, value):
        accessors.setitem(itemsof(self), key, value)
    def fdel(self):
        accessors.delitem(itemsof(self), key)
    return property(fget, fset, fdel)


def copystate(lhs, rhs, setparent=False):
    data = dataof(rhs)
    attrs = attrsof(rhs)
    items = itemsof(rhs)
    
    if attrs is None and items is None:
        setdata(lhs, type(data)())
        if is_sequence(data):
            for key in range(len(data)):
                value = accessors.getitem(rhs, key)
                lhs.append(value)
        if is_mapping(data):
            for key in data.keys():
                value = accessors.getitem(rhs, key)
                accessors.setitem(lhs, key, value)
    else:
        setattrs(lhs, type(attrs)())
        #if is_sequence(attrs):
        #    for key in range(len(attrs)):
        #        value = accessors.getattr(rhs, key)
        #        lhs.append(value)
        if is_mapping(attrs):
            for key in attrs.keys():
                value = accessors.getattr(rhs, key)
                accessors.setattr(lhs, key, value)
        
        items = itemsof(rhs)
        setitems(lhs, type(items)())
        if is_sequence(items):
            for key in range(len(items)):
                value = accessors.getitem(rhs, key)
                lhs.append(value)
        if is_mapping(items):
            for key in items.keys():
                value = accessors.getitem(rhs, key)
                accessors.setitem(lhs, key, value)


class Object(object):
    _type_key = defaults.DEFAULT_OBJECTS_TYPE_KEY
    _attrs_key = defaults.DEFAULT_OBJECTS_ATTRS_KEY
    _items_key = defaults.DEFAULT_OBJECTS_ITEMS_KEY
    
    def __init__(self, type=None, attrs=None, items=None, data=None):
        super().__init__()
        
        with direct_access(self):
            self._data = {
                self._attrs_key: {} if attrs is None else attrs,
                self._items_key: {} if items is None else items,
            } if data is None else data
        
        if type is not None:
            accessors.setitem(self._data, self._type_key, type)
        
        if attrs is not None:
            _attrs = self._data.setdefault(self._attrs_key, attrs)
            if _attrs is not attrs:
                _attrs.update(attrs)
        
        if items is not None:
            _items = self._data.setdefault(self._items_key, items)
            if _items is not items:
                _items.update(items)
    
    def __getstate__(self, state):
        copystate(state, self, False)
        
    def __setstate__(self, state):
        copystate(self, state, True)
    
    def __getattr__(self, key):
        try:
            attrs = attrsof(self, dataof(self))
            return accessors.getitem(attrs, key)
        except KeyError:
            raise AttributeError(key)
        
    def __setattr__(self, key, value):
        _property = getattr(self.__class__, key, None)
        if isinstance(_property, property) and _property.fset:
            _property.fset(self, value)
        elif key in self.__dict__:
            accessors.setitem(self.__dict__, key, value)
        else:
            attrs = attrsof(self, dataof(self))
            accessors.setitem(attrs, key, value)
        
    def __delattr__(self, key):
        _property = getattr(self.__class__, key, None)
        if isinstance(_property, property) and _property.fdel:
            _property.fdel(self)
        elif key in self.__dict__:
            accessors.delitem(self.__dict__, key)
        else:
            attrs = attrsof(self, dataof(self))
            accessors.delitem(attrs, key)
    
    def __getitem__(self, key):
        items = itemsof(self, dataof(self))
        return accessors.getitem(items, key)
        
    def __setitem__(self, key, value):
        items = itemsof(self, dataof(self))
        accessors.setitem(items, key, value)
        
    def __delitem__(self, key):
        items = itemsof(self, dataof(self))
        accessors.delitem(items, key)
    
    def __iter__(self):
        items = itemsof(self, dataof(self))
        return accessors.iteritems(items)
    
    def __len__(self):
        items = itemsof(self, dataof(self))
        return accessors.lenitems(items)
    
    def get(self, key, default=None):
        return accessors.getitem(self, key, default)
    
    def setdefault(self, key, value):
        try:
            return accessors.getitem(self, key)
        except KeyError:
            accessors.setitem(self, key, value)
            return value
    
    def keys(self):
        items = itemsof(self, dataof(self))
        
        if isinstance(items, collections.Mapping):
            return iter(items)
        
        if isinstance(items, collections.Sequence):
            return iter(range(len(items)))
        
        return iter([])
    
    def values(self):
        for key in self.keys():
            yield self[key]
    
    def items(self):
        for key in self.keys():
            yield key, self[key]
    
    def insert(self, key, value):
        items = itemsof(self, dataof(self))
        items.insert(key, value)
    
    def append(self, value):
        self.insert(len(self), value)
    
    def __repr__(self):
        return "{}{}".format(type(self).__name__, repr(self._data))
    
    def __str__(self):
        return "{}{}".format(type(self).__name__, str(self._data))

        
def simple_decode(cls):    
    def _decode(obj):
        result = cls()
        
        data = dataof(obj)
        attrs = attrsof(obj)
        items = itemsof(obj)
        
        if attrs is None and items is None:
            if isinstance(data, collections.Sequence):
                for key in range(len(data)):
                    result.append(accessors.getitem(obj, key))
            if isinstance(data, collections.Mapping):
                for key in data.keys():
                    accessors.setitem(result, key, accessors.getitem(obj, key))
        else:
            #if isinstance(attrs, collections.Sequence):
            #    for key in range(len(attrs)):
            #        result.append(accessors.getattr(obj, key))
            if isinstance(attrs, collections.Mapping):
                for key in attrs.keys():
                    accessors.setattr(result, key, accessors.getattr(obj, key))
            
            
            if isinstance(items, collections.Sequence):
                for key in range(len(items)):
                    result.append(accessors.getitem(obj, key))
            if isinstance(items, collections.Mapping):
                for key in items.keys():
                    accessors.setitem(result, key, accessors.getitem(obj, key))
        
        return result
    return _decode


class ObjectJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Object):
            return dataof(obj)
        
        return json.JSONEncoder.default(self, obj)


class ObjectJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        object_hook = kwargs.pop("object_hook", utilities.identity)
        object_pairs_hook = kwargs.pop("object_pairs_hook", dict)
        
        def _object_hook(data):
            return Object(data=data)
        
        kwargs["object_hook"] = lambda data: _object_hook(object_hook(data))
        kwargs["object_pairs_hook"] = lambda data: _object_hook(object_pairs_hook(data))
        
        super().__init__(*args, **kwargs)


def save_raw(data, *args, **kwargs):
    kwargs.setdefault("cls", ObjectJSONEncoder)
    return json.dumps(data, *args, **kwargs)


def load_raw(data, *args, **kwargs):
    kwargs.setdefault("cls", ObjectJSONDecoder)
    return json.loads(data, *args, **kwargs)


def save_file_raw(data, file, *args, **kwargs):
    kwargs.setdefault("cls", ObjectJSONEncoder)
    return json.dump(data, file, *args, **kwargs)


def load_file_raw(file, *args, **kwargs):
    kwargs.setdefault("cls", ObjectJSONDecoder)
    return json.load(file, *args, **kwargs)


def save(value, codec, *args, **kwargs):
    data = codec.encode(value)
    return save_raw(data, *args, **kwargs)


def load(data, codec, *args, **kwargs):
    value = load_raw(data, *args, **kwargs)
    return codec.decode(value)


def save_file(obj, file, codec, *args, **kwargs):
    data = codec.encode(value)
    return save_file_raw(data, file, *args, **kwargs)


def load_file(file, codec, *args, **kwargs):
    value = load_file_raw(file, *args, **kwargs)
    return codec.decode(value)


def save_path(path, data, codec, *args, **kwargs):
    with open(path, 'w') as file:
        return save_file(data, file, codec, *args, **kwargs)


def load_path(path, codec, *args, **kwargs):
    with open(path, 'r') as file:
        return load_file(file, codec, *args, **kwargs)
