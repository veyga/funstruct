"""Tests for StateT (State monad transformer over Either)."""

from parametrization import Parametrization as P

from funstruct.monad.either import Either, Left, Right
from funstruct.monadtransformer import StateT
from tests.laws import (
    assert_applicative_laws,
    assert_functor_laws,
    assert_monad_laws,
)


def _state_t_eq(a, b):
    """Compare StateT values by running them with a test state."""
    return a.run(0) == b.run(0) and a.run(99) == b.run(99)


class TestStateTLaws:
    def test_functor(self):
        assert_functor_laws(StateT.pure(1, Either), eq=_state_t_eq)

    def test_applicative(self):
        assert_applicative_laws(
            pure_fn=lambda v: StateT.pure(v, Either),
            fa=StateT.pure(1, Either),
            fb=StateT.pure(2, Either),
            eq=_state_t_eq,
        )

    def test_monad(self):
        assert_monad_laws(
            pure_fn=lambda v: StateT.pure(v, Either),
            m=StateT.pure(5, Either),
            f=lambda x: StateT.pure(x + 1, Either),
            g=lambda x: StateT.pure(x * 10, Either),
            eq=_state_t_eq,
        )


class TestRun:
    def test_run_returns_result(self):
        s = StateT(lambda st: Right((st, 42)))
        assert s.run(0) == Right((0, 42))

    def test_run_propagates_state(self):
        s = StateT(lambda st: Right((st + 1, "value")))
        assert s.run(10) == Right((11, "value"))

    def test_run_propagates_failure(self):
        s = StateT(lambda _: Left(ValueError("boom")))
        result = s.run(0)
        assert result.is_left


class TestPure:
    def test_pure_does_not_modify_state(self):
        assert StateT.pure(99, Either).run("unchanged") == Right(("unchanged", 99))

    def test_pure_wraps_value(self):
        assert StateT.pure("hello", Either).run(0) == Right((0, "hello"))


class TestFail:
    def test_fail_produces_failure(self):
        result = StateT.fail("oops", Either).run(0)
        assert result == Left("oops")

    def test_fail_short_circuits_chain(self):
        pipeline = StateT.fail("stop", Either).then(StateT.pure("never", Either))
        assert pipeline.run(0) == Left("stop")


class TestMap:
    @P.autodetect_parameters()
    @P.case(name="0", value=1, f=lambda x: x * 2, expected=2)
    @P.case(name="1", value="hi", f=str.upper, expected="HI")
    @P.case(name="2", value=[1, 2], f=len, expected=2)
    def test_map_transforms_value(self, value, f, expected):
        assert StateT.pure(value, Either).map(f).run(0) == Right((0, expected))

    def test_map_does_not_modify_state(self):
        s = StateT(lambda st: Right((st + 1, 5)))
        assert s.map(lambda x: x * 10).run(0) == Right((1, 50))

    def test_map_skips_on_failure(self):
        s = StateT(lambda st: Left("err"))
        result = s.map(lambda x: x * 10).run(0)
        assert result == Left("err")


class TestBind:
    def test_bind_threads_state(self):
        inc = StateT(lambda s: Right((s + 1, s)))
        assert inc.bind(lambda _: inc).run(0) == Right((2, 1))

    def test_bind_passes_value(self):
        result = StateT.pure(5, Either).bind(lambda x: StateT.pure(x + 10, Either))
        assert result.run(0) == Right((0, 15))

    def test_bind_short_circuits_on_failure(self):
        fail = StateT(lambda _: Left("err"))
        pipeline = fail.bind(lambda _: StateT.pure("never", Either))
        assert pipeline.run(0) == Left("err")

    def test_bind_chains_state_modifications(self):
        push = lambda v: StateT(lambda s: Right((s + [v], v)))
        pipeline = push(1).bind(lambda _: push(2)).bind(lambda _: push(3))
        assert pipeline.run([]) == Right(([1, 2, 3], 3))

    def test_bind_chains_state_with_clist(self):
        from funstruct.collections.cons import CList, Cons, Nil

        push = lambda v: StateT(lambda s: Right((Cons(v, s), v)))
        pipeline = push(1).bind(lambda _: push(2)).bind(lambda _: push(3))
        assert pipeline.run(Nil()) == Right((CList.from_iterable([3, 2, 1]), 3))


class TestOrElse:
    def test_or_else_recovers_from_failure(self):
        failing = StateT(lambda _: Left("oops"))
        recovered = failing.or_else(lambda _: StateT.pure("recovered", Either))
        assert recovered.run(0) == Right((0, "recovered"))

    def test_or_else_skips_on_success(self):
        s = StateT.pure("ok", Either)
        result = s.or_else(lambda e: StateT.pure("should not happen", Either))
        assert result.run(0) == Right((0, "ok"))

    def test_or_else_uses_state_before_or_elseed_computation(self):
        """or_else reverts to the state at the start of the or_elseed computation."""
        mutate_then_fail = StateT(lambda _: Left("err"))
        # or_else wraps the whole .then(fail) — recovery gets the original state
        recovered = (
            StateT(lambda s: Right((s + 1, "a")))
            .then(mutate_then_fail)
            .or_else(lambda e: StateT.get(Either))
        )
        assert recovered.run(0) == Right((0, 0))

    def test_or_else_preserves_state_from_successful_prefix_with_separate_or_else(
        self,
    ):
        """To keep prior state, or_else only the failing step."""
        mutate = StateT(lambda s: Right((s + 1, "a")))
        failing = StateT(lambda s: Left("err"))
        # or_else only wraps the failing step
        recovered = mutate.then(failing.or_else(lambda e: StateT.get(Either)))
        assert recovered.run(0) == Right((1, 1))

    def test_or_else_selective_recovery(self):
        """Only recover from specific error types."""

        class Recoverable(Exception):
            pass

        class Fatal(Exception):
            pass

        failing = StateT(lambda _: Left(Recoverable()))
        pipeline = failing.or_else(
            lambda err: (
                StateT.pure("fixed", Either)
                if isinstance(err, Recoverable)
                else StateT.fail(err, Either)
            )
        )
        assert pipeline.run(0) == Right((0, "fixed"))

        fatal = StateT(lambda _: Left(Fatal()))
        pipeline2 = fatal.or_else(
            lambda err: (
                StateT.pure("fixed", Either)
                if isinstance(err, Recoverable)
                else StateT.fail(err, Either)
            )
        )
        result = pipeline2.run(0)
        assert result.is_left


class TestThen:
    def test_then_discards_value(self):
        result = StateT.pure("discarded", Either).then(StateT.pure("kept", Either))
        assert result.run(0) == Right((0, "kept"))

    def test_then_threads_state(self):
        inc = StateT(lambda s: Right((s + 1, s)))
        assert inc.then(inc).then(inc).run(0) == Right((3, 2))

    def test_then_short_circuits_on_failure(self):
        inc = StateT(lambda s: Right((s + 1, s)))
        fail = StateT(lambda s: Left("stop"))
        pipeline = inc.then(fail).then(inc)
        assert pipeline.run(0) == Left("stop")


class TestGet:
    def test_get_produces_state_as_value(self):
        assert StateT.get(Either).run(42) == Right((42, 42))


class TestModify:
    def test_modify_transforms_state(self):
        assert StateT.modify(lambda s: s * 2, Either).run(5) == Right((10, None))


class TestLaws:
    """Monad laws for StateT."""

    def test_left_identity(self):
        """pure(a).bind(f) == f(a)"""
        f = lambda x: StateT(lambda s: Right((s, x * 2)))
        assert StateT.pure(5, Either).bind(f).run(0) == f(5).run(0)

    def test_right_identity(self):
        """m.bind(pure) == m."""
        m = StateT(lambda s: Right((s, s * 2)))
        pure_fn = lambda a: StateT.pure(a, Either)
        assert m.bind(pure_fn).run(7) == m.run(7)

    def test_associativity(self):
        """m.bind(f).bind(g) == m.bind(x: f(x).bind(g))"""
        m = StateT.pure(1, Either)
        f = lambda x: StateT(lambda s: Right((s, x + 1)))
        g = lambda x: StateT(lambda s: Right((s, x * 2)))
        left = m.bind(f).bind(g).run(0)
        right = m.bind(lambda x: f(x).bind(g)).run(0)
        assert left == right


class TestDoNotation:
    def test_basic_do(self):
        @StateT.do
        def pipeline():
            x = yield StateT.pure(1, Either)
            y = yield StateT.pure(x + 10, Either)
            return x + y

        assert pipeline.run(0) == Right((0, 12))

    def test_do_threads_state(self):
        @StateT.do
        def pipeline():
            x = yield StateT(lambda s: Right((s + 1, s)))
            y = yield StateT(lambda s: Right((s + 1, s)))
            return (x, y)

        assert pipeline.run(0) == Right((2, (0, 1)))

    def test_do_short_circuits(self):
        @StateT.do
        def pipeline():
            x = yield StateT.pure(1, Either)
            y = yield StateT(lambda _: Left("boom"))
            return x + y

        assert pipeline.run(0) == Left("boom")

    def test_do_modifies_state(self):
        @StateT.do
        def pipeline():
            yield StateT.modify(lambda s: s + 10, Either)
            yield StateT.modify(lambda s: s * 2, Either)
            s = yield StateT.get(Either)
            return s

        assert pipeline.run(1) == Right((22, 22))


class TestLift:
    def test_lift_success(self):
        result = StateT.lift(Right(42)).run(0)
        assert result == Right((0, 42))

    def test_lift_failure(self):
        result = StateT.lift(Left("err")).run(0)
        assert result == Left("err")

    def test_lift_preserves_state(self):
        result = StateT.lift(Right("val")).run(99)
        assert result == Right((99, "val"))
