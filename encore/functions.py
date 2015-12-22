
def constant(value):
    def _constant():
        return value
    return _constant

    
def caller(function, *args, **kwargs):
    def _caller():
        return function(*args, **kwargs)
    return _caller


def raiser(value):
    def _raiser():
        raise value
    return _raiser


def counter(initial=0, step=1):
    def _counter():
        result = _counter._i
        _counter._i += step
        return result
    _counter._i = initial
    return _counter


# TODO: Monad
unit = constant

def bind(function, value):
    return function(value())

