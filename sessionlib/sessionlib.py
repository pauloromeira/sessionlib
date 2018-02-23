# -*- coding: utf-8 -*-

import logging

from contextlib import ExitStack
from .utils import Observable

logger = logging.getLogger(__name__)


class Session(object):
    _sessions = []

    @classmethod
    def current(cls):
        return cls._sessions[-1] if cls._sessions else None

    @classmethod
    def _push(cls, session):
        cls._sessions.append(session)

    @classmethod
    def _pop(cls):
        cls._sessions.pop()

    def __init__(self, *contextmanagers):
        self._on_start = Observable(self)
        self._on_enter = Observable(self)
        self._on_leave = Observable(self)
        self._on_close = Observable(self)

        self._exit_stack = ExitStack()
        self._started = False
        self._contexts = contextmanagers

    @property
    def on_start(self):
        return self._on_start

    @property
    def on_enter(self):
        return self._on_enter

    @property
    def on_leave(self):
        return self._on_leave

    @property
    def on_close(self):
        return self._on_close

    def enter_contexts(self):
        yield from self._contexts

    @property
    def started(self):
        return self._started

    def __enter__(self):
        self.__class__._push(self)
        if self._started:
            self.on_enter()
            logger.info('{} session entered'.format(self))
            return

        self.on_start()

        enter_contexts = self.enter_contexts()
        for context in enter_contexts:
            enter_contexts.send(self._exit_stack.enter_context(context))

        self._started = True
        logger.info('{} session started'.format(self))

        return self

    def __exit__(self, *exc_info):
        self.__class__._pop()
        if self in self.__class__._sessions:
            self.on_leave()
            logger.info('{} session left'.format(self))
            return

        try:
            self.on_close()
        finally:
            self._exit_stack.close()

        logger.info('{} session closed'.format(self))


def sessionaware(func):
    def func_wrapper(*args, **kwargs):
        current_session = Session.current()

        if args and isinstance(args[0], Session):
            session = args[0]
            if session is current_session:
                return func(*args, **kwargs)
            else:
                with session:
                    return func(*args, **kwargs)
        else:
            return func(current_session, *args, **kwargs)

    return func_wrapper
