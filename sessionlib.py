import logging

from contextlib import AbstractContextManager, ExitStack

logger = logging.getLogger(__name__)

__all__ = ['Session', 'contextaware']


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
        self._cms = contextmanagers
        self._exit_stack = ExitStack()
        self.started = False


    def __enter__(self):
        Session._push(self)
        if self.started:
            logger.info(f'{self} session entered')
            return

        for cm in self._cms:
            self._exit_stack.enter_context(cm)

        self.started = True
        logger.info(f'{self} session started')

        return self


    def __exit__(self, *exc_info):
        Session._pop()
        if self in Session._sessions:
            logger.info(f'{self} session left')
            return

        self._exit_stack.close()
        logger.info(f'{self} session closed')

