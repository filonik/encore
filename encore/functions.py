
def constant(value):
    def _constant():
        return value
    return _constant


def binder(function, *args, **kwargs):
    def _binder():
        return function(*args, **kwargs)
    return _bound


def raiser(cls):
    def _raiser():
        raise cls()
    return _raiser


def counter(initial=0, step=1):
    def _counter():
        result = _counter._i
        _counter._i += step
        return result
    _counter._i = initial
    return _counter
