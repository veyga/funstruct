"""Tests for the pure State monad."""

from parametrization import Parametrization as P

from funstruct.monad import State


class TestRun:
    def test_run_returns_tuple(self):
        s = State(lambda st: (st, 42))
        assert s.run(0) == (0, 42)

    def test_run_propagates_state(self):
        s = State(lambda st: (st + 1, "value"))
        assert s.run(10) == (11, "value")


class TestPure:
    def test_pure_does_not_modify_state(self):
        assert State.pure(99).run("unchanged") == ("unchanged", 99)

    def test_pure_wraps_value(self):
        assert State.pure("hello").run(0) == (0, "hello")


class TestMap:
    @P.autodetect_parameters()
    @P.case(name="0", value=1, f=lambda x: x * 2, expected=2)
    @P.case(name="1", value="hi", f=str.upper, expected="HI")
    @P.case(name="2", value=[1, 2], f=len, expected=2)
    def test_map_transforms_value(self, value, f, expected):
        assert State.pure(value).map(f).run(0) == (0, expected)

    def test_map_does_not_modify_state(self):
        s = State(lambda st: (st + 1, 5))
        assert s.map(lambda x: x * 10).run(0) == (1, 50)


class TestBind:
    def test_bind_threads_state(self):
        inc = State(lambda s: (s + 1, s))
        assert inc.bind(lambda _: inc).run(0) == (2, 1)

    def test_bind_passes_value(self):
        result = State.pure(5).bind(lambda x: State.pure(x + 10))
        assert result.run(0) == (0, 15)

    def test_bind_chains_state_modifications(self):
        push = lambda v: State(lambda s: (s + [v], v))
        pipeline = push(1).bind(lambda _: push(2)).bind(lambda _: push(3))
        assert pipeline.run([]) == ([1, 2, 3], 3)


class TestThen:
    def test_then_discards_value(self):
        result = State.pure("discarded").then(State.pure("kept"))
        assert result.run(0) == (0, "kept")

    def test_then_threads_state(self):
        inc = State(lambda s: (s + 1, s))
        assert inc.then(inc).then(inc).run(0) == (3, 2)


class TestGet:
    def test_get_produces_state_as_value(self):
        assert State.get().run(42) == (42, 42)

    def test_get_does_not_modify_state(self):
        assert State.get().run("foo") == ("foo", "foo")


class TestModify:
    def test_modify_transforms_state(self):
        assert State.modify(lambda s: s * 2).run(5) == (10, None)

    def test_modify_produces_none(self):
        _, value = State.modify(lambda s: s).run(99)
        assert value is None


class TestLaws:
    """Monad laws: left identity, right identity, associativity."""

    def test_left_identity(self):
        """pure(a).bind(f) == f(a)"""
        f = lambda x: State(lambda s: (s, x * 2))
        assert State.pure(5).bind(f).run(0) == f(5).run(0)

    def test_right_identity(self):
        """m.bind(pure) == m."""
        m = State(lambda s: (s + 1, 42))
        assert m.bind(State.pure).run(0) == m.run(0)

    def test_associativity(self):
        """m.bind(f).bind(g) == m.bind(lambda x: f(x).bind(g))"""
        m = State.pure(5)
        f = lambda x: State(lambda s: (s, x + 1))
        g = lambda x: State(lambda s: (s, x * 2))

        left = m.bind(f).bind(g).run(0)
        right = m.bind(lambda x: f(x).bind(g)).run(0)
        assert left == right
