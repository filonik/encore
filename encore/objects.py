import collections
import json

import contextlib as cl

from . import accessors, defaults, functions, generics, managers, utilities


@cl.contextmanager
def direct_access(obj):
    direct_getattr = managers.attrset(type(obj), "__getattr__", functions.raiser(lambda self, key: AttributeError(key)))
    direct_setattr = managers.attrset(type(obj), "__setattr__", object.__setattr__)
    direct_delattr = managers.attrset(type(obj), "__delattr__", object.__delattr__)
    with direct_getattr, direct_setattr, direct_delattr:
        yield


def dataof(obj):
    if isinstance(obj, (Value, Object)):
        return obj._data
    return obj


def typeof(obj, default=None):
    if isinstance(obj, (Value, Object)):
        data = dataof(obj)
        if isinstance(data, collections.Mapping):
            return data.get(Object._type_key, default)
    return default


def attrsof(obj, default=None):
    if isinstance(obj, (Value, Object)):
        data = dataof(obj)
        if isinstance(data, collections.Mapping):
            return dataof(data.get(Object._attrs_key, default))
    return default

    
def itemsof(obj, default=None):
    if isinstance(obj, (Value, Object)):
        data = dataof(obj)
        if isinstance(data, collections.Mapping):
            return dataof(data.get(Object._items_key, default))
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
        
        if not module_name:
            # TODO: Is this correct?
            module_name = "__main__"
        
        module_name = ".".join(module_name)
        m = __import__(module_name, globals(), locals(), class_name)
        c = accessors.getattr(m, class_name)
        return c
    return obj


def as_schema(func):
    if isinstance(func, Schema):
        return func
    return Schema(func=func)


def as_visitor(func):
    if isinstance(func, Visitor):
        return func
    return Visitor(func)


def apply(value, view): 
    value = Value._wrap(value).view(view)
    return view(value)


def visit(value, func):    
    return apply(value, as_visitor(func))


def reify(value, schema):
    if schema._type is not None:
        type_ = string_to_type(schema._type)
        
        result = type_()
        setstate(result, value)
        return result
    else:
        data = dataof(value)
        
        if isinstance(data, (type(None), bool, int, float, str)):
            return data
        
        type_ = typeof(value)
        attrs = attrsof(value)
        items = itemsof(value)
        
        if all(item is None for item in [type_, attrs, items]):
            if data is None:
                pass
            elif isinstance(data, collections.Sequence):
                data = type(data)(apply(value, schema.item()) for value in data)
            elif isinstance(data, collections.Mapping):
                data = type(data)((key, apply(value, schema.item(key))) for key, value in data.items())
                
            return Object(data=data)
        else:
            if attrs is None:
                pass 
            elif isinstance(attrs, collections.Sequence):
                attrs = type(attrs)(apply(value, schema.attr()) for value in attrs)
            elif isinstance(attrs, collections.Mapping):
                attrs = type(attrs)((key, apply(value, schema.attr(key))) for key, value in attrs.items())
            
            if items is None:
                pass
            elif isinstance(items, collections.Sequence):
                items = type(items)(apply(value, schema.item()) for value in items) 
            elif isinstance(items, collections.Mapping):
                items = type(items)((key, apply(value, schema.item(key))) for key, value in items.items())
        
            return Object(type=type_, attrs=attrs, items=items)


class View(object):
    def __init__(self, attrs=None, items=None):
        super().__init__()

        self.attrs = attrs
        self.items = items
    
    def attr(self, key):
        if isinstance(self.attrs, collections.Mapping):
            default = self.attrs.get("*")
            return self.attrs.get(key, default)
        return self.attrs
    
    def item(self, key):
        if isinstance(self.items, collections.Mapping):
            default = self.items.get("*")
            return self.items.get(key, default)
        return self.items
    
    def __call__(self, value):
        return dataof(value)


class Schema(View):
    def __init__(self, type=None, func=None, attrs=None, items=None):
        super().__init__(attrs, items)
        
        self._type = type
        self._func = func
    
    def attr(self, key):
        return as_schema(super().attr(key))
    
    def item(self, key):
        return as_schema(super().item(key))
    
    def update(self, type=None, func=None):
        self._type = self._type if type is None else type
        self._func = self._func if func is None else func
    
    def __call__(self, value):
        self.update(type=typeof(value))
        
        result = reify(value, self)
            
        func = utilities.identity if self._func is None else self._func
        
        return func(result) 
    
    def __repr__(self):
        return "Schema{{{}}}".format(repr(self._type))
    
    def __str__(self):
        return "Schema{{{}}}".format(str(self._type))


class Visitor(View):
    def __init__(self, func=None, attrs=None, items=None):
        super().__init__(attrs, items)
        
        self._func = func
    
    def attr(self, key):
        return as_visitor(super().attr(key))
    
    def item(self, key):
        return as_visitor(super().item(key))
    
    def __call__(self, value):
        data = dataof(value)
        attrs = attrsof(value)
        items = itemsof(value)
        
        #print(value)
        
        if isinstance(attrs, collections.Mapping) or isinstance(items, collections.Mapping):
            if self.attrs and isinstance(attrs, collections.Mapping):
                for key, _ in attrs.items():
                    accessors.getattr(value, key)
                    #accessors.setattr(value, key, accessors.getattr(value, key))
                
            if self.items and isinstance(items, collections.Mapping):
                for key, _ in items.items():
                    accessors.getitem(value, key)
                    #accessors.setitem(value, key, accessors.getitem(value, key))
        else:
            if self.items and isinstance(data, collections.Mapping):
                for key, _ in data.items():
                    accessors.getitem(value, key)
                    #accessors.setitem(value, key, accessors.getitem(value, key))
        
        func = utilities.identity if self._func is None else self._func
        
        return func(dataof(value))


def defaultsetstate(self, other):
    data = dataof(other)
    attrs = attrsof(other)
    items = itemsof(other)
    
    if attrs is None and items is None:
        for key in data:
            #print("setattr", key, accessors.getattr(other, key))
            accessors.setattr(self, key, accessors.getattr(other, key))
        
    if attrs is not None:
        if isinstance(attrs, collections.Sequence):
            for key in range(len(attrs)):
                self.append(accessors.getattr(other, key))
        else:
            for key in attrs:
                #print("setattr", key, accessors.getattr(other, key))
                accessors.setattr(self, key, accessors.getattr(other, key))
    
    if items is not None:
        if isinstance(items, collections.Sequence):
            for key in range(len(items)):
                self.append(accessors.getitem(other, key))
        else:
            for key in items:
                #print("setitem", key, accessors.getitem(other, key))
                accessors.setitem(self, key, accessors.getitem(other, key))


def setstate(self, other):
    _setstate = accessors.getattr(type(self), "__setstate__", defaultsetstate)
    _setstate(self, other)


def attrmeta(self, key=None):
    if isinstance(self, Meta):
        if isinstance(self._attrs, collections.Mapping):
            return self._attrs.get(key)
        return self._attrs
    return None


def itemmeta(self, key=None):
    if isinstance(self, Meta):
        if isinstance(self._items, collections.Mapping):
            return self._items.get(key)
        return self._items
    return None


class Object(object):
    _type_key = defaults.DEFAULT_OBJECTS_TYPE_KEY
    _attrs_key = defaults.DEFAULT_OBJECTS_ATTRS_KEY
    _items_key = defaults.DEFAULT_OBJECTS_ITEMS_KEY
    
    def __init__(self, data=None, attrs=None, items=None, type=None):
        super().__init__()
        
        with direct_access(self):
            self._data = {} if data is None else data
            
            if data is None:
                attrs = {} if attrs is None else attrs
                items = {} if items is None else items
                
                accessors.setitem(self._data, self._type_key, type)
                accessors.setitem(self._data, self._attrs_key, attrs)
                accessors.setitem(self._data, self._items_key, items)
    
    def __getattr__(self, key):
        return _getattr(self, key)
        
    def __setattr__(self, key, value):
        _setattr(self, key, value)
        
    def __delattr__(self, key):
        _delattr(self, key, value)
    
    def __getitem__(self, key):
        return _getitem(self, key)
    
    def __setitem__(self, key, value):
        _setitem(self, key, value)
        
    def __delitem__(self, key):
        _delitem(self, key)
    
    def __iter__(self):
        items = itemsof(self, dataof(self))
        
        if isinstance(items, collections.Sequence):
            return self.values()
        else:
            return self.keys()
    
    def __len__(self):
        items = itemsof(self, dataof(self))
        return len(items)
    
    def items(self):
        for key in self.keys():
            yield key, self[key]
    
    def keys(self):
        items = itemsof(self, dataof(self))
        
        if isinstance(items, collections.Mapping):
            return iter(items)
        
        if isinstance(items, collections.Sequence):
            return range(len(items))
        
        return iter([])
    
    def values(self):
        for key in self.keys():
            yield self[key]
            
    def __repr__(self):
        parts = [typeof(self), attrsof(self), itemsof(self)]
        parts =  ", ".join(map(repr, filter(None, parts))) if any(parts) else repr(dataof(self))
        return "{}({})".format(type(self).__name__, parts)
    
    def __str__(self):
        parts = [typeof(self), attrsof(self), itemsof(self)]
        parts =  ", ".join(map(str, filter(None, parts))) if any(parts) else str(dataof(self))
        return "{}({})".format(type(self).__name__, parts)


class Value(object):
    @staticmethod
    def _wrap(data):
        if isinstance(data, Value):
            return data
        return Value(data)
    
    @staticmethod
    def _unwrap(data):
        if isinstance(data, Value):
            return data._data
        return data
    
    def __init__(self, data=None, view=None):
        super().__init__()
        
        with direct_access(self):
            self._data = data
            self._view = view

    def __getstate__(self):
        return self._data
    
    def __setstate__(self, data):
        self._data = data
    
    def __getattr__(self, key):
        value = self._wrap(_getattr(self, key))
        return apply(value, self._view.attr(key))
        
    def __setattr__(self, key, value):
        value = self._unwrap(value)
        _setattr(self, key, value)
        
    def __delattr__(self, key):
        _delattr(self, key)
    
    def __getitem__(self, key):
        value = self._wrap(_getitem(self, key))
        return apply(value, self._view.item(key))
    
    def __setitem__(self, key, value):
        value = self._unwrap(value)
        _setitem(self, key, value)
        
    def __delitem__(self, key):
        _delitem(self, key)
    
    def view(self, view):
        return Value(self._data, view)
    
    def __repr__(self):
        return "{}({})".format(type(self).__name__, repr(self._data))
        
    def __str__(self):
        return "{}({})".format(type(self).__name__, str(self._data))


class ValueEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Value):
            return obj.__getstate__()
        return json.JSONEncoder.default(self, obj)


class ValueDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        object_hook = kwargs.pop("object_hook", utilities.identity)
        object_pairs_hook = kwargs.pop("object_pairs_hook", utilities.identity)
        
        def _object_hook(data):
            result = Value()
            result.__setstate__(data)
            return result
        
        kwargs["object_hook"] = lambda data: _object_hook(object_hook(data))
        kwargs["object_pairs_hook"] = lambda data: _object_hook(object_pairs_hook(data))
        
        super().__init__(*args, **kwargs)


def save_raw(data):
    return json.dumps(data, cls=ValueEncoder)


def load_raw(data):
    return json.loads(data, cls=ValueDecoder, object_pairs_hook=collections.OrderedDict)


def save_file_raw(file, data):
    return json.dump(data, file, cls=ValueEncoder)


def load_file_raw(file):
    return json.load(file, cls=ValueDecoder, object_pairs_hook=collections.OrderedDict)


def save(data, schema=None):
    return save_raw(data)


def load(data, schema=None):
    value = load_raw(data)
    return apply(value, as_schema(schema))


def save_file(file, data, schema=None):
    return save_file_raw(file, data)


def load_file(file, schema=None):
    value = load_file_raw(file)
    return apply(value, as_schema(schema))


def save_path(path, data, schema=None):
    with open(path, 'w') as file:
        return save_file(file, data, schema=schema)


def load_path(path, schema=None):
    with open(path, 'r') as file:
        return load_file(file, schema=schema)
