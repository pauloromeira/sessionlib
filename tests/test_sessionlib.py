#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sessionlib import Session, sessionaware
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

    assert aware_func() == None
    with s1:
        assert aware_func() == s1

        with Session() as s2:
            assert aware_func() == s2
            assert aware_func(s1) == s1
            assert aware_func() == s2

        assert aware_func() == s1

    assert aware_func() == None


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



