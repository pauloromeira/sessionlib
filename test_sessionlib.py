from sessionlib import AbstractSession, contextaware


def test_session_stack():
    s1 = AbstractSession()
    assert AbstractSession.current() == None

    with s1:
        assert AbstractSession.current() == s1

        with AbstractSession() as s2:
            assert AbstractSession.current() == s2

        assert AbstractSession.current() == s1

    assert AbstractSession.current() == None



def test_contextaware():
    @contextaware
    def aware_func(session):
        return session

    s1 = AbstractSession()

    assert aware_func() == None
    with s1:
        assert aware_func() == s1

        with AbstractSession() as s2:
            assert aware_func() == s2
            assert aware_func(s1) == s1
            assert aware_func() == s2

        assert aware_func() == s1

    assert aware_func() == None
