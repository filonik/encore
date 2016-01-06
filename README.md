# encore
Some addons to the Python standard library shared among other projects. Functionality such as:

## Decorators

The `flyweight` decorator allows for simple implementation of the flyweight design pattern.

```python
from encore import decorators

@decorators.flyweight
class Foo(object):
    def __init__(self, name):
        super().__init__()
        self._name = name
    def __str__(self):
        return self._name

a = Foo("A")
print(a, id(a), id(Foo("A")), a is Foo("A"))
```

The `indexedproperty` decorator allows defining properties that behave like mappings.

```python
from encore import decorators


class Foo(object):
    @decorators.indexedproperty
    def x(self, key):
        return key + 1
    
    @x.setter
    def x(self, key, value):
        print("setter", key)
    
    @x.deleter
    def x(self, key):
        print("deleter", key)
    
    @x.iterator
    def x(self):
        return iter([1,2,3])


f = Foo()
print(list(f.x.items()))
```

## Objects

Simple JSON-based object (de-)serialization with optional schema annotation to provide type information.

```python
from encore import objects


class Foo(object):
    __module__ = "example"
    
    def __repr__(self):
        return repr(self.__dict__)
    
    def __str__(self):
        return str(self.__dict__)


class Bar(object):
    __module__ = "example"
    
    def __setstate__(self, data):
        self.a = data.get("a")
        self.b = data.get("b")
    
    def __repr__(self):
        return repr(self.__dict__)
    
    def __str__(self):
        return str(self.__dict__)


def print_info(obj):
    print(type(obj).__name__, obj)


# No Type Annotation, result:
# Default Python JSON representation
print_info(objects.load('{"a": false, "b": 1, "c": "2"}'))


# Type Annotation in Python, result:
# Foo object, default __setstate__ implementation (set items as attributes)
print_info(objects.load('{"a": false, "b": 1, "c": "2"}', schema=objects.Schema(Foo)))

# Foo object, default __setstate__ implementation (set items as attributes) with custom item conversion
print_info(objects.load('{"a": false, "b": 1, "c": "2"}', schema=objects.Schema(Foo, items=int)))

# Bar object, custom __setstate__ implementation
print_info(objects.load('{"a": false, "b": 1, "c": "2"}', schema=objects.Schema(Bar)))

# Bar object, custom __setstate__ implementation with custom item conversion
print_info(objects.load('{"a": false, "b": 1, "c": "2"}', schema=objects.Schema(Bar, items=int)))

# Bar object with Foo object items (Schema Composition)
print_info(objects.load('{"a": {"a": "One", "b": 1}, "b": {"a": "Two", "b": 2}}', schema=objects.Schema(Bar, items=objects.Schema(Foo))))



# Type Annotation in JSON, result:
# Foo object, default __setstate__ implementation (set items as attributes)
print_info(objects.load('{"__type__": "Foo", "__attrs__": {"a": false, "b": 1, "c": "2"}}'))

# Bar object, custom __setstate__ implementation
print_info(objects.load('{"__type__": "Bar", "__attrs__": {"a": false, "b": 1, "c": "2"}}'))
```

Special attribute names ("\_\_type\_\_", "\_\_attrs\_\_", "\_\_items\_\_") are fully customizable.

```python
import encore.defaults

# Before importing objects module
encore.defaults.DEFAULT_OBJECTS_TYPE_KEY = "py/type"
encore.defaults.DEFAULT_OBJECTS_ATTRS_KEY = "py/attrs"
encore.defaults.DEFAULT_OBJECTS_ITEMS_KEY = "py/items"
```
