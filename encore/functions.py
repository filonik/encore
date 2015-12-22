
def constant(value):
    def _constant(*args, **kwargs):
        return value
    return _constant


def raiser(value):
    def _raiser(*args, **kwargs):
        raise value(*args, **kwargs)
    return _raiser


def counter(initial=0, step=1):
    def _counter(*args, **kwargs):
        result = _counter._i
        _counter._i += step
        return result
    _counter._i = initial
    return _counter


# TODO: Monad
unit = constant


def binder(function):
    def decorator(*args_, **kwargs_):
        def decorated(*args, **kwargs):
            _args = [value(*args, **kwargs) for value in args_]
            _kwargs = {key: value(*args, **kwargs) for key, value in kwargs_.items()}
            return function(*_args, **_kwargs)
        return decorated
    return decorator


def lifter(function):
    return binder(lambda *args, **kwargs: unit(function(*args, **kwargs)))


printer = lifter(print)
