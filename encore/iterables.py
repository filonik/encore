import collections

import functools as ft
import itertools as it

drop = lambda iterable, n: it.islice(iterable, n, None)
take = lambda iterable, n: it.islice(iterable, None, n)

nth = lambda iterable, n, default=None: next(drop(iterable, n), default)


def populate(arr, iterable):
    for key, value in zip(range(len(arr)), iterable):
        arr[key] = value


def split(iterable, n):
    i1, i2 = it.tee(iterable)
    return take(i1, n), drop(i2, n)


def distinct(iterable):
    return collections.OrderedDict.fromkeys(iterable).keys()


def flattened(iterable):
    for items in iterable:
        if isinstance(items, collections.Iterable) and not isinstance(items, str):
            for item in flattened(items):
                yield item
        else:
            yield items

            
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
