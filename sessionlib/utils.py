# -*- coding: utf-8 -*-

from inspect import signature


class Observable(object):
    def __init__(self, obj=None):
        self.callbacks = []
        self.obj = obj

    def subscribe(self, callback):
        self.callbacks.append(callback)

    def unsubscribe(self, callback):
        self.callbacks.remove(callback)

    def __call__(self, args=None):
        for fn in self.callbacks:
            a = [self.obj, args][:len(signature(fn).parameters)]
            fn(*a)
