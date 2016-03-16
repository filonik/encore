import collections

import functools as ft
import itertools as it

drop = lambda iterable, n: it.islice(iterable, n, None)
take = lambda iterable, n: it.islice(iterable, None, n)

nth = lambda iterable, n, default=None: next(drop(iterable, n), default)


def populate(arr, iterable):
    for key, value in zip(range(len(arr)), iterable):
        arr[key] = value


def count(iterable, predicate):
    return sum(1 for item in iterable if predicate(item))


def indices(iterable, predicate):
    return [i for i, item in enumerate(iterable) if predicate(item)]


def split(iterable, n):
    i1, i2 = it.tee(iterable)
    return take(i1, n), drop(i2, n)


def distinct(iterable):
    return collections.OrderedDict.fromkeys(iterable).keys()


def flattened_full(iterable):
    if not isinstance(iterable, collections.Iterable) or isinstance(iterable, str):
        yield iterable
    else:
        for items in iterable:
            for item in flattened_full(items):
                yield item


def flattened_deep(iterable, depth=1):
    if depth < 0:
        yield iterable
    else:
        for items in iterable:
            for item in flattened_deep(items, depth-1):
                yield item


def flattened(iterable, depth=None):
    if depth is None:
        return flattened_full(iterable)
    else:
        return flattened_deep(iterable, depth)


def cycled(iterable, n):
    for _ in range(n):
        for item in iterable:
            yield item


def repeated(iterable, n):
    for item in iterable:
        for _ in range(n):
            yield item


def windowed(iterable, n=1):
    head, tail = split(iterable, n)
    window = collections.deque(head, maxlen=n)
    yield window
    for e in tail:
        window.append(e)
        yield window
