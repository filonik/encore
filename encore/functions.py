import operator


def constant(value):
    def _constant(*args, **kwargs):
        return value
    return _constant


def variable(key, default=None):
    def _variable(*args, **kwargs):
        return kwargs.get(key, default)
    return _variable


def counter(initial=0, step=1):
    def _counter(*args, **kwargs):
        result = _counter._i
        _counter._i += step
        return result
    _counter._i = initial
    return _counter


def raiser(value):
    def _raiser(*args, **kwargs):
        raise value(*args, **kwargs)
    return _raiser


def binder(function):
    def decorator(*args_, **kwargs_):
        def decorated(*args, **kwargs):
            _args = [value(*args, **kwargs) for value in args_]
            _kwargs = {key: value(*args, **kwargs) for key, value in kwargs_.items()}
            return function(*_args, **_kwargs)
        return decorated
    return decorator


# TODO: Monads
unit = constant

printer = binder(print)

add = binder(operator.add)
sub = binder(operator.sub)
mul = binder(operator.mul)
div = binder(operator.truediv)