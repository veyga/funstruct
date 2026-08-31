"""Tests for ReaderT monad transformer."""

from funstruct.monad.either import Either, Left, Right
from funstruct.monadtransformer import ReaderT, StateT
from tests.laws import (
    assert_applicative_laws,
    assert_functor_laws,
    assert_monad_laws,
)


def _reader_t_eq(a, b):
    """Compare ReaderT values by running with test contexts."""
    return a.run("ctx1") == b.run("ctx1") and a.run("ctx2") == b.run("ctx2")


class TestReaderTLaws:
    def test_functor(self):
        assert_functor_laws(ReaderT.pure(1, Either), eq=_reader_t_eq)

    def test_applicative(self):
        assert_applicative_laws(
            pure_fn=lambda v: ReaderT.pure(v, Either),
            fa=ReaderT.pure(1, Either),
            fb=ReaderT.pure(2, Either),
            eq=_reader_t_eq,
        )

    def test_monad(self):
        assert_monad_laws(
            pure_fn=lambda v: ReaderT.pure(v, Either),
            m=ReaderT.pure(5, Either),
            f=lambda x: ReaderT.pure(x + 1, Either),
            g=lambda x: ReaderT.pure(x * 10, Either),
            eq=_reader_t_eq,
        )


class TestRun:
    def test_run_applies_context(self):
        step = ReaderT(lambda ctx: Right(ctx + 1))
        assert step.run(5) == Right(6)

    def test_call_is_alias_for_run(self):
        step = ReaderT(lambda ctx: Right(ctx * 2))
        assert step(3) == step.run(3)


class TestBind:
    def test_bind_threads_context(self):
        step1 = ReaderT(lambda ctx: Right(ctx))
        step2 = lambda a: ReaderT(lambda ctx: Right(a + ctx))
        result = step1.bind(step2).run(10)
        assert result == Right(20)

    def test_bind_short_circuits_on_failure(self):
        step1 = ReaderT(lambda ctx: Left("err"))
        step2 = lambda a: ReaderT(lambda ctx: Right("never"))
        assert step1.bind(step2).run(0) == Left("err")


class TestMap:
    def test_map_transforms_value(self):
        step = ReaderT(lambda ctx: Right(ctx))
        assert step.map(lambda x: x * 3).run(7) == Right(21)

    def test_map_skips_on_failure(self):
        step = ReaderT(lambda ctx: Left("err"))
        assert step.map(lambda x: x * 3).run(7) == Left("err")


class TestOrElse:
    def test_or_else_recovers_from_failure(self):
        failing = ReaderT(lambda ctx: Left("oops"))
        recovered = failing.or_else(lambda err: ReaderT(lambda ctx: Right("recovered")))
        assert recovered.run(0) == Right("recovered")

    def test_or_else_skips_on_success(self):
        ok = ReaderT(lambda ctx: Right("ok"))
        result = ok.or_else(lambda err: ReaderT(lambda ctx: Right("nope")))
        assert result.run(0) == Right("ok")

    def test_or_else_receives_context(self):
        failing = ReaderT(lambda ctx: Left("err"))
        recovered = failing.or_else(
            lambda err: ReaderT(lambda ctx: Right(f"{err}+{ctx}"))
        )
        assert recovered.run("ctx") == Right("err+ctx")


class TestThen:
    def test_then_discards_value(self):
        s1 = ReaderT(lambda ctx: Right("discard"))
        s2 = ReaderT(lambda ctx: Right("keep"))
        assert s1.then(s2).run(0) == Right("keep")

    def test_then_short_circuits(self):
        s1 = ReaderT(lambda ctx: Left("stop"))
        s2 = ReaderT(lambda ctx: Right("never"))
        assert s1.then(s2).run(0) == Left("stop")


class TestPure:
    def test_pure_wraps_value(self):
        step = ReaderT.pure(42, Either)
        assert step.run("anything") == Right(42)

    def test_pure_ignores_context(self):
        step = ReaderT.pure("hello", Either)
        assert step.run(None) == Right("hello")
        assert step.run(999) == Right("hello")

    def test_pure_composes_with_bind(self):
        pipeline = ReaderT.pure(5, Either).bind(
            lambda x: ReaderT(lambda ctx: Right(x + ctx))
        )
        assert pipeline.run(10) == Right(15)


class TestLift:
    def test_lift_ignores_context(self):
        inner = Right(42)
        step = ReaderT.lift_f(inner)
        assert step.run("anything") == Right(42)
        assert step.run(None) == Right(42)

    def test_lift_propagates_failure(self):
        inner = Left("err")
        step = ReaderT.lift_f(inner)
        assert step.run(0) == Left("err")


class TestWithStateT:
    """ReaderT wrapping StateT — the full stack."""

    def test_threads_context_and_state(self):
        step = ReaderT(lambda ctx: StateT(lambda s: Right((s + ctx, s))))
        assert step.run(10).run(0) == Right((10, 0))

    def test_lift_state_t(self):
        state_op = StateT(lambda s: Right((s + 1, s)))
        step = ReaderT.lift_f(state_op)
        assert step.run("ignored").run(5) == Right((6, 5))

    def test_bind_composes_full_stack(self):
        inc = ReaderT.lift_f(StateT(lambda s: Right((s + 1, None))))
        get = ReaderT.lift_f(StateT(lambda s: Right((s, s))))
        pipeline = inc.then(inc).then(get)
        assert pipeline.run("ctx").run(0) == Right((2, 2))

    def test_or_else_with_state_t(self):
        failing = ReaderT.lift_f(StateT(lambda s: Left(ValueError("expired"))))
        recover = ReaderT(lambda ctx: StateT(lambda s: Right((s, f"recovered-{ctx}"))))
        pipeline = failing.or_else(lambda err: recover)
        assert pipeline.run("myctx").run(0) == Right((0, "recovered-myctx"))


class TestAndThen:
    def test_output_becomes_next_context(self):
        # a reads ctx and returns ctx + 10; b reads that as its ctx
        a = ReaderT(lambda ctx: Right(ctx + 10))
        b = ReaderT(lambda ctx: Right(ctx * 2))
        assert a.and_then(b).run(5) == Right(30)

    def test_short_circuits_on_failure(self):
        a = ReaderT(lambda ctx: Left("err"))
        b = ReaderT(lambda ctx: Right("never"))
        assert a.and_then(b).run(0) == Left("err")

    def test_chains_three_steps(self):
        add_one = ReaderT(lambda ctx: Right(ctx + 1))
        double = ReaderT(lambda ctx: Right(ctx * 2))
        to_str = ReaderT(lambda ctx: Right(str(ctx)))
        assert add_one.and_then(double).and_then(to_str).run(4) == Right("10")


class TestLaws:
    """Monad laws for ReaderT."""

    def test_left_identity(self):
        """pure-equivalent.bind(f) == f(a)"""
        a = 5
        pure_a = ReaderT(lambda ctx: Right(a))
        f = lambda x: ReaderT(lambda ctx: Right(x + ctx))
        assert pure_a.bind(f).run(10) == f(a).run(10)

    def test_right_identity(self):
        """m.bind(pure-equivalent) == m."""
        m = ReaderT(lambda ctx: Right(ctx * 2))
        pure_fn = lambda a: ReaderT(lambda ctx: Right(a))
        assert m.bind(pure_fn).run(7) == m.run(7)

    def test_associativity(self):
        """m.bind(f).bind(g) == m.bind(x: f(x).bind(g))"""
        m = ReaderT(lambda ctx: Right(1))
        f = lambda x: ReaderT(lambda ctx: Right(x + ctx))
        g = lambda x: ReaderT(lambda ctx: Right(x * 2))
        left = m.bind(f).bind(g).run(5)
        right = m.bind(lambda x: f(x).bind(g)).run(5)
        assert left == right


class TestDoNotation:
    def test_shared_context_with_failure(self):
        get_name = ReaderT(lambda cfg: Right(cfg["name"]))
        get_email = ReaderT(
            lambda cfg: Right(cfg["email"]) if "email" in cfg else Left("missing email")
        )
        validate_name = lambda n: ReaderT(
            lambda cfg: Right(n) if len(n) > 0 else Left("empty name")
        )

        @ReaderT.do
        def build_profile():
            name = yield get_name
            name = yield validate_name(name)
            email = yield get_email
            return {"name": name, "email": email}

        cfg_ok = {"name": "Alice", "email": "alice@example.com"}
        assert build_profile.run(cfg_ok) == Right(
            {"name": "Alice", "email": "alice@example.com"}
        )

        cfg_no_email = {"name": "Bob"}
        assert build_profile.run(cfg_no_email) == Left("missing email")

        cfg_empty_name = {"name": "", "email": "x@y.z"}
        assert build_profile.run(cfg_empty_name) == Left("empty name")

    def test_do_threads_context(self):
        @ReaderT.do
        def pipeline():
            x = yield ReaderT(lambda ctx: Right(ctx))
            y = yield ReaderT(lambda ctx: Right(x + ctx))
            return y

        assert pipeline.run(5) == Right(10)

    def test_do_short_circuits(self):
        @ReaderT.do
        def pipeline():
            x = yield ReaderT(lambda ctx: Right(1))
            y = yield ReaderT(lambda ctx: Left("boom"))
            return x + y

        assert pipeline.run(0) == Left("boom")


class TestWithOption:
    """ReaderT wrapping Option — tests transformer generality."""

    def test_pure_with_option(self):
        from funstruct.monad.option import Option, Some

        step = ReaderT.pure(42, Option)
        assert step.run("anything") == Some(42)

    def test_bind_with_option(self):
        from funstruct.monad.option import Some

        step1 = ReaderT(lambda ctx: Some(ctx))
        step2 = lambda a: ReaderT(lambda ctx: Some(a + ctx))
        assert step1.bind(step2).run(5) == Some(10)

    def test_bind_short_circuits_nothing(self):
        from funstruct.monad.option import Nothing, Some

        step1 = ReaderT(lambda ctx: Nothing())
        step2 = lambda a: ReaderT(lambda ctx: Some("never"))
        assert step1.bind(step2).run(0) == Nothing()

    def test_do_with_option(self):
        from funstruct.monad.option import Some

        @ReaderT.do
        def pipeline():
            x = yield ReaderT(lambda ctx: Some(ctx))
            y = yield ReaderT(lambda ctx: Some(x + 1))
            return y

        assert pipeline.run(10) == Some(11)

    def test_do_short_circuits_nothing(self):
        from funstruct.monad.option import Nothing, Some

        @ReaderT.do
        def pipeline():
            x = yield ReaderT(lambda ctx: Some(1))
            y = yield ReaderT(lambda ctx: Nothing())
            return x + y

        assert pipeline.run(0) == Nothing()
