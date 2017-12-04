# -*- coding: utf-8 -*-

import logging

from contextlib import AbstractContextManager, ExitStack
from .utils import Observable

logger = logging.getLogger(__name__)


class Session(AbstractContextManager):
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
        self.on_start = Observable(self)
        self.on_enter = Observable(self)
        self.on_leave = Observable(self)
        self.on_close = Observable(self)

        self._exit_stack = ExitStack()
        self._started = False
        self._cms = contextmanagers

    def build_context(self):
        yield from self._cms

    @property
    def started(self):
        return self._started

    def __enter__(self):
        self.__class__._push(self)
        if self._started:
            self.on_enter()
            logger.info(f'{self} session entered')
            return

        self.on_start()

        for context in self.build_context():
            self._exit_stack.enter_context(context)

        self._started = True
        logger.info(f'{self} session started')

        return self

    def __exit__(self, *exc_info):
        self.__class__._pop()
        if self in self.__class__._sessions:
            self.on_leave()
            logger.info(f'{self} session left')
            return

        try:
            self.on_close()
        finally:
            self._exit_stack.close()

        logger.info(f'{self} session closed')


def contextaware(func):
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
