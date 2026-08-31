"""Tests for EitherT monad transformer."""

import pytest

from funstruct.monad.either import Left, Right
from funstruct.monad.option import Nothing, Option, Some
from funstruct.monadtransformer.either_t import EitherT
from tests.laws import assert_functor_laws, assert_monad_laws


def _either_t_eq(a, b):
    """Compare EitherT values by unwrapping."""
    return a.run() == b.run()


class TestEitherTLaws:
    def test_functor(self):
        assert_functor_laws(EitherT(Some(Right(42))), eq=_either_t_eq)

    def test_monad(self):
        assert_monad_laws(
            pure_fn=lambda v: EitherT(Some(Right(v))),
            m=EitherT(Some(Right(10))),
            f=lambda x: EitherT(Some(Right(x + 1))),
            g=lambda x: EitherT(Some(Right(x * 2))),
            eq=_either_t_eq,
        )

    def test_monad_laws_with_left(self):
        assert_monad_laws(
            pure_fn=lambda v: EitherT(Some(Right(v))),
            m=EitherT(Some(Left("err"))),
            f=lambda x: EitherT(Some(Right(x + 1))),
            g=lambda x: EitherT(Some(Right(x * 2))),
            eq=_either_t_eq,
        )

    def test_monad_laws_with_nothing(self):
        assert_monad_laws(
            pure_fn=lambda v: EitherT(Some(Right(v))),
            m=EitherT(Nothing()),
            f=lambda x: EitherT(Some(Right(x + 1))),
            g=lambda x: EitherT(Some(Right(x * 2))),
            eq=_either_t_eq,
        )


class TestMap:
    def test_maps_right(self):
        result = EitherT(Some(Right(5))).map(lambda x: x * 2)
        assert result.run() == Some(Right(10))

    def test_skips_left(self):
        result = EitherT(Some(Left("err"))).map(lambda x: x * 2)
        assert result.run() == Some(Left("err"))

    def test_skips_nothing(self):
        result = EitherT(Nothing()).map(lambda x: x * 2)
        assert result.run() == Nothing()


class TestBind:
    def test_chains_right(self):
        inc = lambda x: EitherT(Some(Right(x + 1)))
        result = EitherT(Some(Right(1))).bind(inc).bind(inc)
        assert result.run() == Some(Right(3))

    def test_short_circuits_left(self):
        inc = lambda x: EitherT(Some(Right(x + 1)))
        result = EitherT(Some(Left("stop"))).bind(inc)
        assert result.run() == Some(Left("stop"))

    def test_short_circuits_nothing(self):
        inc = lambda x: EitherT(Some(Right(x + 1)))
        result = EitherT(Nothing()).bind(inc)
        assert result.run() == Nothing()

    def test_bind_can_fail(self):
        fail = lambda x: EitherT(Some(Left(f"failed at {x}")))
        result = EitherT(Some(Right(5))).bind(fail)
        assert result.run() == Some(Left("failed at 5"))


class TestOrElse:
    def test_recovers_from_left(self):
        result = EitherT(Some(Left("err"))).or_else(
            lambda e: EitherT(Some(Right(f"recovered: {e}")))
        )
        assert result.run() == Some(Right("recovered: err"))

    def test_skips_right(self):
        result = EitherT(Some(Right(42))).or_else(lambda e: EitherT(Some(Right(0))))
        assert result.run() == Some(Right(42))

    def test_nothing_propagates(self):
        result = EitherT(Nothing()).or_else(lambda e: EitherT(Some(Right("recovered"))))
        assert result.run() == Nothing()


class TestPure:
    def test_pure_wraps_in_right(self):
        result = EitherT.pure(42, Option)
        assert result.run() == Some(Right(42))


class TestFromError:
    def test_from_error_wraps_in_left(self):
        result = EitherT.from_error("oops", Option)
        assert result.run() == Some(Left("oops"))


class TestLift:
    def test_lift_wraps_value_in_right(self):
        result = EitherT.lift_f(Some(42))
        assert result.run() == Some(Right(42))

    def test_lift_preserves_nothing(self):
        result = EitherT.lift_f(Nothing())
        assert result.run() == Nothing()


class TestFromEither:
    def test_from_either_right(self):
        result = EitherT.from_either(Right(1), Option)
        assert result.run() == Some(Right(1))

    def test_from_either_left(self):
        result = EitherT.from_either(Left("err"), Option)
        assert result.run() == Some(Left("err"))


class TestAndThen:
    def test_chains_discarding_value(self):
        a = EitherT(Some(Right(1)))
        b = EitherT(Some(Right(2)))
        assert a.and_then(b).run() == Some(Right(2))

    def test_short_circuits_on_inner_left(self):
        a = EitherT(Some(Left("stop")))
        b = EitherT(Some(Right("never")))
        assert a.and_then(b).run() == Some(Left("stop"))

    def test_short_circuits_on_outer_nothing(self):
        a = EitherT(Nothing())
        b = EitherT(Some(Right("never")))
        assert a.and_then(b).run() == Nothing()


class TestThen:
    def test_sequences(self):
        a = EitherT(Some(Right("discard")))
        b = EitherT(Some(Right("keep")))
        assert a.then(b).run() == Some(Right("keep"))

    def test_short_circuits(self):
        a = EitherT(Some(Left("stop")))
        b = EitherT(Some(Right("never")))
        assert a.then(b).run() == Some(Left("stop"))


class TestWithEitherAsF:
    """EitherT over Either — nested error types."""

    def test_map(self):
        result = EitherT(Right(Right(5))).map(lambda x: x * 2)
        assert result.run() == Right(Right(10))

    def test_bind(self):
        inc = lambda x: EitherT(Right(Right(x + 1)))
        result = EitherT(Right(Right(1))).bind(inc)
        assert result.run() == Right(Right(2))

    def test_outer_left_propagates(self):
        result = EitherT(Left("outer")).map(lambda x: x + 1)
        assert result.run() == Left("outer")

    def test_inner_left_propagates(self):
        inc = lambda x: EitherT(Right(Right(x + 1)))
        result = EitherT(Right(Left("inner"))).bind(inc)
        assert result.run() == Right(Left("inner"))


class TestDoNotation:
    def test_success(self):
        @EitherT.do
        def pipeline():
            x = yield EitherT(Some(Right(1)))
            y = yield EitherT(Some(Right(x + 10)))
            return x + y

        assert pipeline.run() == Some(Right(12))

    def test_short_circuits_on_left(self):
        @EitherT.do
        def pipeline():
            x = yield EitherT(Some(Right(1)))
            y = yield EitherT(Some(Left("boom")))
            return x + y

        assert pipeline.run() == Some(Left("boom"))

    def test_short_circuits_on_nothing(self):
        @EitherT.do
        def pipeline():
            x = yield EitherT(Some(Right(1)))
            y = yield EitherT(Nothing())
            return x + y

        assert pipeline.run() == Nothing()


class TestBrokenEitherT:
    """Demonstrates what breaks if EitherT doesn't short-circuit properly."""

    def test_non_short_circuiting_violates_monad_laws(self):
        """A broken EitherT that ignores Left and always applies f."""

        class BrokenEitherT:
            def __init__(self, value):
                self._value = value

            def run(self):
                return self._value

            def map(self, f):
                return BrokenEitherT(self._value.map(lambda e: e.map(f)))

            def bind(self, f):
                # BUG: doesn't check for Left — always applies f
                def _step(either):
                    match either:
                        case Right(value):
                            return f(value).run()
                        case Left(err):
                            # BUG: applies f to error instead of propagating
                            return f(err).run()

                return BrokenEitherT(self._value.bind(_step))

        inc = lambda x: BrokenEitherT(Some(Right(x + 1)))

        # This should propagate Left("err") unchanged,
        # but broken version tries to add 1 to "err"
        with pytest.raises(TypeError):
            BrokenEitherT(Some(Left("err"))).bind(inc).run()
