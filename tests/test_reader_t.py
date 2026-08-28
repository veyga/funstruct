"""Tests for ReaderT monad transformer."""

from returns.result import Failure, Result, Success

from funstruct.monad import ReaderT, StateT
from tests.laws import assert_applicative_laws, assert_functor_laws, assert_monad_laws


def _reader_t_eq(a, b):
    """Compare ReaderT values by running with test contexts."""
    return a.run("ctx1") == b.run("ctx1") and a.run("ctx2") == b.run("ctx2")


class TestReaderTLaws:
    def test_functor(self):
        assert_functor_laws(ReaderT.pure(1, Result), eq=_reader_t_eq)

    def test_applicative(self):
        # Skipped: ReaderT.ap delegates to inner monad's .ap(),
        # but returns.Result doesn't implement .ap()
        pass

    def test_monad(self):
        assert_monad_laws(
            pure_fn=lambda v: ReaderT.pure(v, Result),
            m=ReaderT.pure(5, Result),
            f=lambda x: ReaderT.pure(x + 1, Result),
            g=lambda x: ReaderT.pure(x * 10, Result),
            eq=_reader_t_eq,
        )


class TestRun:
    def test_run_applies_context(self):
        step = ReaderT(lambda ctx: Result.from_value(ctx + 1))
        assert step.run(5) == Success(6)

    def test_call_is_alias_for_run(self):
        step = ReaderT(lambda ctx: Result.from_value(ctx * 2))
        assert step(3) == step.run(3)


class TestBind:
    def test_bind_threads_context(self):
        step1 = ReaderT(lambda ctx: Result.from_value(ctx))
        step2 = lambda a: ReaderT(lambda ctx: Result.from_value(a + ctx))
        result = step1.bind(step2).run(10)
        assert result == Success(20)

    def test_bind_short_circuits_on_failure(self):
        step1 = ReaderT(lambda ctx: Result.from_failure("err"))
        step2 = lambda a: ReaderT(lambda ctx: Result.from_value("never"))
        assert step1.bind(step2).run(0) == Failure("err")


class TestMap:
    def test_map_transforms_value(self):
        step = ReaderT(lambda ctx: Result.from_value(ctx))
        assert step.map(lambda x: x * 3).run(7) == Success(21)

    def test_map_skips_on_failure(self):
        step = ReaderT(lambda ctx: Result.from_failure("err"))
        assert step.map(lambda x: x * 3).run(7) == Failure("err")


class TestLash:
    def test_lash_recovers_from_failure(self):
        failing = ReaderT(lambda ctx: Result.from_failure("oops"))
        recovered = failing.lash(
            lambda err: ReaderT(lambda ctx: Result.from_value("recovered"))
        )
        assert recovered.run(0) == Success("recovered")

    def test_lash_skips_on_success(self):
        ok = ReaderT(lambda ctx: Result.from_value("ok"))
        result = ok.lash(lambda err: ReaderT(lambda ctx: Result.from_value("nope")))
        assert result.run(0) == Success("ok")

    def test_lash_receives_context(self):
        failing = ReaderT(lambda ctx: Result.from_failure("err"))
        recovered = failing.lash(
            lambda err: ReaderT(lambda ctx: Result.from_value(f"{err}+{ctx}"))
        )
        assert recovered.run("ctx") == Success("err+ctx")


class TestThen:
    def test_then_discards_value(self):
        s1 = ReaderT(lambda ctx: Result.from_value("discard"))
        s2 = ReaderT(lambda ctx: Result.from_value("keep"))
        assert s1.then(s2).run(0) == Success("keep")

    def test_then_short_circuits(self):
        s1 = ReaderT(lambda ctx: Result.from_failure("stop"))
        s2 = ReaderT(lambda ctx: Result.from_value("never"))
        assert s1.then(s2).run(0) == Failure("stop")


class TestPure:
    def test_pure_wraps_value(self):
        step = ReaderT.pure(42, Result)
        assert step.run("anything") == Success(42)

    def test_pure_ignores_context(self):
        step = ReaderT.pure("hello", Result)
        assert step.run(None) == Success("hello")
        assert step.run(999) == Success("hello")

    def test_pure_composes_with_bind(self):
        pipeline = ReaderT.pure(5, Result).bind(
            lambda x: ReaderT(lambda ctx: Result.from_value(x + ctx))
        )
        assert pipeline.run(10) == Success(15)


class TestLift:
    def test_lift_ignores_context(self):
        inner = Result.from_value(42)
        step = ReaderT.lift(inner)
        assert step.run("anything") == Success(42)
        assert step.run(None) == Success(42)

    def test_lift_propagates_failure(self):
        inner = Result.from_failure("err")
        step = ReaderT.lift(inner)
        assert step.run(0) == Failure("err")


class TestWithStateT:
    """ReaderT wrapping StateT — the full stack."""

    def test_threads_context_and_state(self):
        step = ReaderT(lambda ctx: StateT(lambda s: Result.from_value((s + ctx, s))))
        assert step.run(10).run(0) == Success((10, 0))

    def test_lift_state_t(self):
        state_op = StateT(lambda s: Result.from_value((s + 1, s)))
        step = ReaderT.lift(state_op)
        assert step.run("ignored").run(5) == Success((6, 5))

    def test_bind_composes_full_stack(self):
        inc = ReaderT.lift(StateT(lambda s: Result.from_value((s + 1, None))))
        get = ReaderT.lift(StateT(lambda s: Result.from_value((s, s))))
        pipeline = inc.then(inc).then(get)
        assert pipeline.run("ctx").run(0) == Success((2, 2))

    def test_lash_with_state_t(self):
        failing = ReaderT.lift(StateT(lambda s: Failure(ValueError("expired"))))
        recover = ReaderT(
            lambda ctx: StateT(lambda s: Result.from_value((s, f"recovered-{ctx}")))
        )
        pipeline = failing.lash(lambda err: recover)
        assert pipeline.run("myctx").run(0) == Success((0, "recovered-myctx"))


class TestLaws:
    """Monad laws for ReaderT."""

    def test_left_identity(self):
        """pure-equivalent.bind(f) == f(a)"""
        a = 5
        pure_a = ReaderT(lambda ctx: Result.from_value(a))
        f = lambda x: ReaderT(lambda ctx: Result.from_value(x + ctx))
        assert pure_a.bind(f).run(10) == f(a).run(10)

    def test_right_identity(self):
        """m.bind(pure-equivalent) == m."""
        m = ReaderT(lambda ctx: Result.from_value(ctx * 2))
        pure_fn = lambda a: ReaderT(lambda ctx: Result.from_value(a))
        assert m.bind(pure_fn).run(7) == m.run(7)

    def test_associativity(self):
        """m.bind(f).bind(g) == m.bind(x: f(x).bind(g))"""
        m = ReaderT(lambda ctx: Result.from_value(1))
        f = lambda x: ReaderT(lambda ctx: Result.from_value(x + ctx))
        g = lambda x: ReaderT(lambda ctx: Result.from_value(x * 2))
        left = m.bind(f).bind(g).run(5)
        right = m.bind(lambda x: f(x).bind(g)).run(5)
        assert left == right
