

def not_(predicate):
    def _not_(*args, **kwargs):
        return not predicate(*args, **kwargs)
    return _not_


def pos_(predicate):
    return predicate


def neg_(predicate):
    return not_(predicate)


def all_(*predicates):
    def _all_(*args, **kwargs):
        return all(predicate(*args, **kwargs) for predicate in predicates)
    return _all_


def any_(*predicates):
    def _any_(*args, **kwargs):
        return any(predicate(*args, **kwargs) for predicate in predicates)
    return _any_


def eq_(y):
    def _eq_(x):
        return x == y
    return _eq_


def neq_(y):
    def _neq_(x):
        return x != y
    return _neq_


def and_(y):
    def _and_(x):
        return x & y
    return _and_


def or_(y):
    def _or_(x):
        return x | y
    return _or_


def has_flag(flag):
    def _has_flag(obj):
        return (obj & flag) == flag
    return _has_flag


def oftype(type):
    def _oftype(obj):
        return isinstance(obj, type)
    return _oftype


def between(a, b):
    def _between(obj):
        return a <= obj and obj < b
    return _between
