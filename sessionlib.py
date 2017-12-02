import logging

from contextlib import AbstractContextManager

logger = logging.getLogger(__name__)

__all__ = ['AbstractSession', 'contextaware']


class AbstractSession(AbstractContextManager):
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

    @property
    def started(self):
        getattr(self, '_started', False)

    @started.setter
    def started(self, value):
        self._started = value

    def __enter__(self):
        self.__class__._push(self)
        if self.started:
            self.on_session_entered()
            logger.info(f'{self} session entered')
            return

        self.started = True
        self.on_session_started()
        logger.info(f'{self} session started')

        return self


    def __exit__(self, *exc_info):
        self.__class__._pop()
        if self in self.__class__._sessions:
            self.on_session_left()
            logger.info(f'{self} session left')
            return

        self.on_session_closed()
        logger.info(f'{self} session closed')


    def on_session_started(self):
        pass

    def on_session_entered(self):
        pass

    def on_session_left(self):
        pass

    def on_session_closed(self):
        pass


def contextaware(func, session_class=AbstractSession):
    def func_wrapper(*args, **kwargs):
        current_session = session_class.current()

        if args and isinstance(args[0], session_class):
            session = args[0]
            if session is current_session:
                return func(*args, **kwargs)
            else:
                with session:
                    return func(*args, **kwargs)
        else:
            return func(current_session, *args, **kwargs)

    return func_wrapper
