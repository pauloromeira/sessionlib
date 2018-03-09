#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from sessionlib import Session, sessionaware, SessionlessError
from contextlib import contextmanager


def test_session_stack():
    s1 = Session()
    assert Session.current() == None

    with s1:
        assert Session.current() == s1

        with Session() as s2:
            assert Session.current() == s2

        assert Session.current() == s1

    assert Session.current() == None


def test_sessionaware():
    @sessionaware
    def aware_func(session):
        return session

    s1 = Session()

    with pytest.raises(SessionlessError):
        aware_func()

    with s1:
        assert aware_func() == s1

        with Session() as s2:
            assert aware_func() == s2
            assert aware_func(s1) == s1
            assert aware_func() == s2

        assert aware_func() == s1

    with pytest.raises(SessionlessError):
        aware_func()


def test_events(capsys):
    s1 = Session()
    s1.on_open.subscribe(lambda: print('open'))
    s1.on_enter.subscribe(lambda: print('enter'))
    s1.on_leave.subscribe(lambda: print('leave'))
    s1.on_close.subscribe(lambda: print('close'))

    with s1:
        with s1:
            pass

    out, _ = capsys.readouterr()
    assert out == 'open\nenter\nleave\nclose\n'


def test_contextmanagers():
    @contextmanager
    def cmanager(name):
        yield name

    class SampleSession(Session):
        def enter_contexts(self):
            cm = yield cmanager('1')
            assert cm == '1'

    class SampleSession2(Session):
        def enter_contexts(self):
            yield cmanager('ho')
            cm = yield cmanager('hi')
            assert cm == 'hi'

    with SampleSession():
        pass

    with SampleSession2():
        pass



def test_function_stack():
    class SampleSession(Session):
        def method(self, function_name=None):
            if function_name:
                assert self.current_function.__name__ == function_name
            else:
                assert self.current_function == None

    @sessionaware
    def aware_func(session):
        assert session.current_function.__name__ == 'aware_func'
        session.method('aware_func')

    with SampleSession() as s:
        assert s.current_function == None
        aware_func()
        s.method()
        assert s.current_function == None


def test_gen_function_stack():
    class SampleSession(Session):
        def method(self, function_name=None):
            if function_name:
                assert self.current_function.__name__ == function_name
            else:
                assert self.current_function == None

    @sessionaware
    def gen_func(session):
        assert session.current_function.__name__ == 'gen_func'
        session.method('gen_func')

        aware_func2()
        assert session.current_function.__name__ == 'gen_func'
        session.method('gen_func')

        for i in range(1):
            assert session.current_function.__name__ == 'gen_func'
            session.method('gen_func')
            aware_func2()
            assert session.current_function.__name__ == 'gen_func'
            session.method('gen_func')

            yield i
            assert session.current_function.__name__ == 'gen_func'
            session.method('gen_func')
            aware_func2()
            assert session.current_function.__name__ == 'gen_func'
            session.method('gen_func')

        assert session.current_function.__name__ == 'gen_func'
        session.method('gen_func')
        aware_func2()
        assert session.current_function.__name__ == 'gen_func'
        session.method('gen_func')


    @sessionaware
    def aware_func(session):
        assert session.current_function.__name__ == 'aware_func'
        session.method('aware_func')

        g = gen_func()
        assert session.current_function.__name__ == 'aware_func'
        session.method('aware_func')

        next(g)
        assert session.current_function.__name__ == 'aware_func'
        session.method('aware_func')

        for _ in gen_func():
            assert session.current_function.__name__ == 'aware_func'
            session.method('aware_func')
            for _ in gen_func():
                assert session.current_function.__name__ == 'aware_func'
                session.method('aware_func')
            assert session.current_function.__name__ == 'aware_func'
            session.method('aware_func')

        assert session.current_function.__name__ == 'aware_func'
        session.method('aware_func')


    @sessionaware
    def aware_func2(session):
        assert session.current_function.__name__ == 'aware_func2'
        session.method('aware_func2')


    with SampleSession() as s:
        assert s.current_function == None
        s.method()

        g = gen_func()
        assert s.current_function == None
        s.method()

        next(g)
        assert s.current_function == None
        s.method()

        aware_func()
        assert s.current_function == None
        s.method()

        for _ in gen_func():
            assert s.current_function == None
            s.method()

            aware_func()
            assert s.current_function == None
            s.method()

            for _ in gen_func():
                assert s.current_function == None
                s.method()

                aware_func()
                assert s.current_function == None
                s.method()

            assert s.current_function == None
            s.method()

        assert s.current_function == None
        s.method()



def test_gen_function_next():
    @sessionaware
    def gen_func(session):
        assert session.current_function.__name__ == 'gen_func'
        for i in range(3):
            assert session.current_function.__name__ == 'gen_func'
            yield i
            assert session.current_function.__name__ == 'gen_func'
        assert session.current_function.__name__ == 'gen_func'

    @sessionaware
    def aware_func(session):
        assert session.current_function.__name__ == 'aware_func'
        g = gen_func()
        next(g)
        assert session.current_function.__name__ == 'aware_func'

    with Session() as s:
        aware_func()
        assert s.current_function == None
