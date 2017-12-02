from sessionlib import Session, contextaware


def test_session_stack():
    s1 = Session()
    assert Session.current() == None

    with s1:
        assert Session.current() == s1

        with Session() as s2:
            assert Session.current() == s2

        assert Session.current() == s1

    assert Session.current() == None



def test_contextaware():
    @contextaware
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
