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


def print_info(obj):
    print(type(obj).__name__, obj)


# No Type Annotation:
# Return default Python JSON representation
print_info(objects.load('{"a": false, "b": 1, "c": "2"}'))

# Type Annotation in Python:
# Create Foo object, default __setstate__ -> set items as attributes 
print_info(objects.load('{"a": false, "b": 1, "c": "2"}', schema=objects.Schema(Foo)))

# Create Foo object, default __setstate__ -> set items as attributes with custom conversion
print_info(objects.load('{"a": false, "b": 1, "c": "2"}', schema=objects.Schema(Foo, items=int)))

# Create Bar object, use provided __setstate__
print_info(objects.load('{"a": false, "b": 1, "c": "2"}', schema=objects.Schema(Bar)))

# Type Annotation in JSON:
print_info(objects.load('{"__type__": "A", "__attrs__": {"a": false, "b": 1, "c": "2"}}'))
```

Special attribute names ("__type__", "__attrs__", "__items__") are fully customizable.
