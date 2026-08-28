"""Tests for StateT (State monad transformer over Result)."""

from parametrization import Parametrization as P
from returns.result import Failure, Result, Success

from funstruct.monad import StateT
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
        assert_functor_laws(StateT.pure(1, Result), eq=_state_t_eq)

    def test_applicative(self):
        assert_applicative_laws(
            pure_fn=lambda v: StateT.pure(v, Result),
            fa=StateT.pure(1, Result),
            fb=StateT.pure(2, Result),
            eq=_state_t_eq,
        )

    def test_monad(self):
        assert_monad_laws(
            pure_fn=lambda v: StateT.pure(v, Result),
            m=StateT.pure(5, Result),
            f=lambda x: StateT.pure(x + 1, Result),
            g=lambda x: StateT.pure(x * 10, Result),
            eq=_state_t_eq,
        )


class TestRun:
    def test_run_returns_result(self):
        s = StateT(lambda st: Result.from_value((st, 42)))
        assert s.run(0) == Success((0, 42))

    def test_run_propagates_state(self):
        s = StateT(lambda st: Result.from_value((st + 1, "value")))
        assert s.run(10) == Success((11, "value"))

    def test_run_propagates_failure(self):
        s = StateT(lambda _: Result.from_failure(ValueError("boom")))
        result = s.run(0)
        assert isinstance(result, Failure)


class TestPure:
    def test_pure_does_not_modify_state(self):
        assert StateT.pure(99, Result).run("unchanged") == Success(
            ("unchanged", 99)
        )

    def test_pure_wraps_value(self):
        assert StateT.pure("hello", Result).run(0) == Success((0, "hello"))


class TestFail:
    def test_fail_produces_failure(self):
        result = StateT.fail("oops", Result).run(0)
        assert result == Failure("oops")

    def test_fail_short_circuits_chain(self):
        pipeline = StateT.fail("stop", Result).then(
            StateT.pure("never", Result)
        )
        assert pipeline.run(0) == Failure("stop")


class TestMap:
    @P.autodetect_parameters()
    @P.case(name="0", value=1, f=lambda x: x * 2, expected=2)
    @P.case(name="1", value="hi", f=str.upper, expected="HI")
    @P.case(name="2", value=[1, 2], f=len, expected=2)
    def test_map_transforms_value(self, value, f, expected):
        assert StateT.pure(value, Result).map(f).run(0) == Success(
            (0, expected)
        )

    def test_map_does_not_modify_state(self):
        s = StateT(lambda st: Result.from_value((st + 1, 5)))
        assert s.map(lambda x: x * 10).run(0) == Success((1, 50))

    def test_map_skips_on_failure(self):
        s = StateT(lambda st: Result.from_failure("err"))
        result = s.map(lambda x: x * 10).run(0)
        assert result == Failure("err")


class TestBind:
    def test_bind_threads_state(self):
        inc = StateT(lambda s: Result.from_value((s + 1, s)))
        assert inc.bind(lambda _: inc).run(0) == Success((2, 1))

    def test_bind_passes_value(self):
        result = StateT.pure(5, Result).bind(
            lambda x: StateT.pure(x + 10, Result)
        )
        assert result.run(0) == Success((0, 15))

    def test_bind_short_circuits_on_failure(self):
        fail = StateT(lambda _: Result.from_failure("err"))
        pipeline = fail.bind(lambda _: StateT.pure("never", Result))
        assert pipeline.run(0) == Failure("err")

    def test_bind_chains_state_modifications(self):
        push = lambda v: StateT(lambda s: Result.from_value((s + [v], v)))
        pipeline = push(1).bind(lambda _: push(2)).bind(lambda _: push(3))
        assert pipeline.run([]) == Success(([1, 2, 3], 3))


class TestLash:
    def test_lash_recovers_from_failure(self):
        failing = StateT(lambda _: Result.from_failure("oops"))
        recovered = failing.lash(lambda _: StateT.pure("recovered", Result))
        assert recovered.run(0) == Success((0, "recovered"))

    def test_lash_skips_on_success(self):
        s = StateT.pure("ok", Result)
        result = s.lash(lambda e: StateT.pure("should not happen", Result))
        assert result.run(0) == Success((0, "ok"))

    def test_lash_uses_state_before_lashed_computation(self):
        """Lash reverts to the state at the start of the lashed computation."""
        mutate_then_fail = StateT(lambda _: Result.from_failure("err"))
        # lash wraps the whole .then(fail) — recovery gets the original state
        recovered = (
            StateT(lambda s: Result.from_value((s + 1, "a")))
            .then(mutate_then_fail)
            .lash(lambda e: StateT.get(Result))
        )
        assert recovered.run(0) == Success((0, 0))

    def test_lash_preserves_state_from_successful_prefix_with_separate_lash(
        self,
    ):
        """To keep prior state, lash only the failing step."""
        mutate = StateT(lambda s: Result.from_value((s + 1, "a")))
        failing = StateT(lambda s: Result.from_failure("err"))
        # lash only wraps the failing step
        recovered = mutate.then(failing.lash(lambda e: StateT.get(Result)))
        assert recovered.run(0) == Success((1, 1))

    def test_lash_selective_recovery(self):
        """Only recover from specific error types."""

        class Recoverable(Exception):
            pass

        class Fatal(Exception):
            pass

        failing = StateT(lambda _: Result.from_failure(Recoverable()))
        pipeline = failing.lash(
            lambda err: (
                StateT.pure("fixed", Result)
                if isinstance(err, Recoverable)
                else StateT.fail(err, Result)
            )
        )
        assert pipeline.run(0) == Success((0, "fixed"))

        fatal = StateT(lambda _: Result.from_failure(Fatal()))
        pipeline2 = fatal.lash(
            lambda err: (
                StateT.pure("fixed", Result)
                if isinstance(err, Recoverable)
                else StateT.fail(err, Result)
            )
        )
        result = pipeline2.run(0)
        assert isinstance(result, Failure)


class TestThen:
    def test_then_discards_value(self):
        result = StateT.pure("discarded", Result).then(
            StateT.pure("kept", Result)
        )
        assert result.run(0) == Success((0, "kept"))

    def test_then_threads_state(self):
        inc = StateT(lambda s: Result.from_value((s + 1, s)))
        assert inc.then(inc).then(inc).run(0) == Success((3, 2))

    def test_then_short_circuits_on_failure(self):
        inc = StateT(lambda s: Result.from_value((s + 1, s)))
        fail = StateT(lambda s: Result.from_failure("stop"))
        pipeline = inc.then(fail).then(inc)
        assert pipeline.run(0) == Failure("stop")


class TestGet:
    def test_get_produces_state_as_value(self):
        assert StateT.get(Result).run(42) == Success((42, 42))


class TestModify:
    def test_modify_transforms_state(self):
        assert StateT.modify(lambda s: s * 2, Result).run(5) == Success(
            (10, None)
        )


class TestLaws:
    """Monad laws for StateT."""

    def test_left_identity(self):
        """pure(a).bind(f) == f(a)"""
        f = lambda x: StateT(lambda s: Result.from_value((s, x * 2)))
        assert StateT.pure(5, Result).bind(f).run(0) == f(5).run(0)

    def test_right_identity(self):
        """m.bind(pure) == m."""
        m = StateT(lambda s: Result.from_value((s + 1, 42)))
        assert m.bind(lambda a: StateT.pure(a, Result)).run(0) == m.run(0)

    def test_associativity(self):
        """m.bind(f).bind(g) == m.bind(lambda x: f(x).bind(g))"""
        m = StateT.pure(5, Result)
        f = lambda x: StateT(lambda s: Result.from_value((s, x + 1)))
        g = lambda x: StateT(lambda s: Result.from_value((s, x * 2)))

        left = m.bind(f).bind(g).run(0)
        right = m.bind(lambda x: f(x).bind(g)).run(0)
        assert left == right


class TestLift:
    """StateT.lift — lift F[A] into StateT without modifying state."""

    def test_lift_success_preserves_state(self):
        s = StateT.lift(Result.from_value(42))
        assert s.run(99) == Success((99, 42))

    def test_lift_failure_propagates(self):
        s = StateT.lift(Result.from_failure("err"))
        assert s.run(99) == Failure("err")

    def test_lift_composes_with_bind(self):
        pipeline = StateT.lift(Result.from_value(5)).bind(
            lambda x: StateT.pure(x * 2, Result)
        )
        assert pipeline.run(0) == Success((0, 10))

    def test_lift_composes_with_then(self):
        pipeline = StateT.lift(Result.from_value("ignored")).then(
            StateT.modify(lambda s: s + 1, Result)
        )
        assert pipeline.run(0) == Success((1, None))

    def test_lift_failure_short_circuits(self):
        pipeline = StateT.lift(Result.from_failure("stop")).then(
            StateT.pure("never", Result)
        )
        assert pipeline.run(0) == Failure("stop")
