# -*- coding: utf-8 -*-


class Observable(object):
    def __init__(self, obj=None):
        self.callbacks = []
        self.obj = obj

    def subscribe(self, callback):
        self.callbacks.append(callback)

    def unsubscribe(self, callback):
        self.callbacks.remove(callback)

    def __call__(self, params=None):
        for fn in self.callbacks:
            if fn.__code__.co_argcount == 0:
                fn()
            elif params:
                fn(self.obj, params)
            else:
                fn(self.obj)
