

class Observable(object):
    def __init__(self):
        super(Observable, self).__init__()

        self._subscribers = []

    def subscribe(self, value):
        self._subscribers.append(value)

    def unsubscribe(self, value):
        self._subscribers.remove(value)

    def __call__(self, *args, **kwargs):
        for subscriber in self._subscribers:
            subscriber(*args, **kwargs)
