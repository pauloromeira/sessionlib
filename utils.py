class Observable(object):
    def __init__(self, obj=None):
        self.callbacks = []
        self.obj = obj

    def add(self, callback):
        self.callbacks.append(callback)

    def del(self, callback):
        self.callbacks.remove(callback)

    def __call__(self, args=None):
        for fn in self.callbacks:
            fn(self.obj, args)
