from . import functions, utilities


def infinite(func):
    while True:
        yield func()


constant = utilities.compose(infinite, functions.constant)
autoincrement = utilities.compose(infinite, functions.counter)