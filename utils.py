class Observable(object):
    def __init__(self, obj=None):
        self.callbacks = []
        self.obj = obj

    def subscribe(self, callback):
        self.callbacks.append(subscribe)

    def __call__(self, args=None):
        for fn in self.callbacks:
            fn(self.obj, args)
