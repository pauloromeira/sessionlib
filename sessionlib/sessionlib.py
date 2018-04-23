# -*- coding: utf-8 -*-

import logging

from types import GeneratorType
from functools import wraps
from contextlib import ExitStack
from .utils import Observable

logger = logging.getLogger(__name__)


class SessionlessError(RuntimeError):
    pass

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
        self._contexts = contextmanagers


    def _push_function(self, func):
        self._function_stack = getattr(self, '_function_stack', [])
        self._function_stack.append(func)

    def _pop_function(self):
        self._function_stack = getattr(self, '_function_stack', [])
        self._function_stack.pop()

    @property
    def current_function(self):
        self._function_stack = getattr(self, '_function_stack', [])
        return self._function_stack[-1] if self._function_stack else None

    @property
    def on_open(self):
        self._on_open = getattr(self, '_on_open', Observable(self))
        return self._on_open

    @property
    def on_enter(self):
        self._on_enter = getattr(self, '_on_enter', Observable(self))
        return self._on_enter

    @property
    def on_leave(self):
        self._on_leave = getattr(self, '_on_leave', Observable(self))
        return self._on_leave

    @property
    def on_close(self):
        self._on_close = getattr(self, '_on_close', Observable(self))
        return self._on_close

    def enter_contexts(self):
        yield from self._contexts

    @property
    def opened(self):
        return getattr(self, '_opened', False)


    def open(self):
        self.__class__._push(self)
        if self.opened:
            self.on_enter()
            logger.info('{} session entered'.format(self))
            return

        self._exit_stack = ExitStack()

        enter_contexts = self.enter_contexts()
        try:
            context = next(enter_contexts)
            while True:
                context_obj = self._exit_stack.enter_context(context)
                context = enter_contexts.send(context_obj)
        except StopIteration:
            pass

        self.on_open()

        self._opened = True
        logger.info('{} session opened'.format(self))

        return self


    def close(self):
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


    def __enter__(self):
        return self.open()

    def __exit__(self, *exc_info):
        self.close()


def sessionaware(function=None, cls=Session):
    def _decorate(func):
        @wraps(func)
        def _handle_generator(session, func, response):
            session._push_function(func)
            try:
                for item in response:
                    session._pop_function()
                    yield item
                    session._push_function(func)
            except GeneratorExit:
                session._push_function(func)
            finally:
                session._pop_function()


        @wraps(func)
        def wrapped(*args, **kwargs):
            current_session = cls.current()

            if args and isinstance(args[0], cls):
                session = args[0]
            elif current_session:
                session = current_session
                args = (session,) + args
            else:
                raise SessionlessError('No session is currently active')

            session._push_function(func)
            try:
                if session is current_session:
                    response = func(*args, **kwargs)
                else:
                    with session:
                        response = func(*args, **kwargs)
            finally:
                session._pop_function()

            if isinstance(response, GeneratorType):
                return _handle_generator(session, func, response)
            else:
                return response

        return wrapped
    
    return _decorate(function) if function else _decorate

