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
