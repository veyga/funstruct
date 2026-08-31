"""Tests for OptionT monad transformer."""

from funstruct.monad.either import Either, Left, Right
from funstruct.monad.option import Nothing, Some
from funstruct.monadtransformer.option_t import OptionT


def _option_t_eq(a, b):
    """Compare OptionT values by running them."""
    return a.run() == b.run()


class TestMap:
    def test_maps_some(self):
        assert OptionT(Right(Some(5))).map(lambda x: x * 2).run() == Right(Some(10))

    def test_skips_nothing(self):
        assert OptionT(Right(Nothing())).map(lambda x: x * 2).run() == Right(Nothing())

    def test_skips_left(self):
        assert OptionT(Left("err")).map(lambda x: x * 2).run() == Left("err")


class TestBind:
    def test_chains_some(self):
        result = (
            OptionT(Right(Some(1))).bind(lambda x: OptionT(Right(Some(x + 10)))).run()
        )
        assert result == Right(Some(11))

    def test_short_circuits_nothing(self):
        result = (
            OptionT(Right(Nothing())).bind(lambda x: OptionT(Right(Some(x + 10)))).run()
        )
        assert result == Right(Nothing())

    def test_short_circuits_left(self):
        result = OptionT(Left("err")).bind(lambda x: OptionT(Right(Some(x + 10)))).run()
        assert result == Left("err")

    def test_bind_produces_nothing(self):
        result = OptionT(Right(Some(1))).bind(lambda x: OptionT(Right(Nothing()))).run()
        assert result == Right(Nothing())

    def test_multi_step(self):
        result = (
            OptionT(Right(Some(1)))
            .bind(lambda x: OptionT(Right(Some(x + 1))))
            .bind(lambda x: OptionT(Right(Some(x + 1))))
            .run()
        )
        assert result == Right(Some(3))


class TestOrElse:
    def test_recovers_from_nothing(self):
        result = (
            OptionT(Right(Nothing())).or_else(lambda: OptionT(Right(Some(99)))).run()
        )
        assert result == Right(Some(99))

    def test_skips_on_some(self):
        result = OptionT(Right(Some(1))).or_else(lambda: OptionT(Right(Some(99)))).run()
        assert result == Right(Some(1))

    def test_does_not_recover_left(self):
        """or_else only handles Nothing, not outer monad failure."""
        result = OptionT(Left("err")).or_else(lambda: OptionT(Right(Some(99)))).run()
        assert result == Left("err")


class TestThen:
    def test_sequences(self):
        result = (
            OptionT(Right(Some("discard"))).then(OptionT(Right(Some("keep")))).run()
        )
        assert result == Right(Some("keep"))

    def test_short_circuits_nothing(self):
        result = OptionT(Right(Nothing())).then(OptionT(Right(Some("never")))).run()
        assert result == Right(Nothing())


class TestPure:
    def test_pure(self):
        assert OptionT.pure(42, Either).run() == Right(Some(42))

    def test_none(self):
        assert OptionT.none(Either).run() == Right(Nothing())


class TestLift:
    def test_lift_right(self):
        assert OptionT.lift_f(Right(42)).run() == Right(Some(42))

    def test_lift_left(self):
        assert OptionT.lift_f(Left("err")).run() == Left("err")


class TestAndThen:
    def test_chains_discarding_value(self):
        a = OptionT(Right(Some(1)))
        b = OptionT(Right(Some(2)))
        assert a.and_then(b).run() == Right(Some(2))

    def test_short_circuits_on_nothing(self):
        a = OptionT(Right(Nothing()))
        b = OptionT(Right(Some("never")))
        assert a.and_then(b).run() == Right(Nothing())

    def test_short_circuits_on_left(self):
        a = OptionT(Left("err"))
        b = OptionT(Right(Some("never")))
        assert a.and_then(b).run() == Left("err")


class TestWithOption:
    """OptionT wrapping Option — nested optionality collapsed."""

    def test_some_some(self):
        result = OptionT(Some(Some(1))).map(lambda x: x + 10).run()
        assert result == Some(Some(11))

    def test_some_nothing(self):
        result = OptionT(Some(Nothing())).map(lambda x: x + 10).run()
        assert result == Some(Nothing())

    def test_nothing_outer(self):
        result = OptionT(Nothing()).map(lambda x: x + 10).run()
        assert result == Nothing()

    def test_bind_with_option(self):
        result = (
            OptionT(Some(Some(1))).bind(lambda x: OptionT(Some(Some(x + 10)))).run()
        )
        assert result == Some(Some(11))

    def test_bind_inner_nothing(self):
        result = (
            OptionT(Some(Nothing())).bind(lambda x: OptionT(Some(Some(x + 10)))).run()
        )
        assert result == Some(Nothing())


class TestDoNotation:
    def test_success(self):
        @OptionT.do
        def pipeline():
            x = yield OptionT(Right(Some(1)))
            y = yield OptionT(Right(Some(x + 10)))
            return x + y

        assert pipeline.run() == Right(Some(12))

    def test_short_circuits_nothing(self):
        @OptionT.do
        def pipeline():
            x = yield OptionT(Right(Some(1)))
            y = yield OptionT(Right(Nothing()))
            return x + y

        assert pipeline.run() == Right(Nothing())

    def test_short_circuits_left(self):
        @OptionT.do
        def pipeline():
            x = yield OptionT(Right(Some(1)))
            y = yield OptionT(Left("boom"))
            return x + y

        assert pipeline.run() == Left("boom")


class TestLaws:
    """Monad laws for OptionT over Either."""

    def test_left_identity(self):
        """pure(a).bind(f) == f(a)"""
        f = lambda x: OptionT(Right(Some(x + 1)))
        left = OptionT.pure(5, Either).bind(f).run()
        right = f(5).run()
        assert left == right

    def test_right_identity(self):
        """m.bind(pure) == m"""
        m = OptionT(Right(Some(5)))
        left = m.bind(lambda x: OptionT.pure(x, Either)).run()
        right = m.run()
        assert left == right

    def test_associativity(self):
        """m.bind(f).bind(g) == m.bind(x -> f(x).bind(g))"""
        m = OptionT(Right(Some(5)))
        f = lambda x: OptionT(Right(Some(x + 1)))
        g = lambda x: OptionT(Right(Some(x * 2)))
        left = m.bind(f).bind(g).run()
        right = m.bind(lambda x: f(x).bind(g)).run()
        assert left == right

    def test_associativity_with_nothing(self):
        """Laws hold even when values are Nothing."""
        m = OptionT(Right(Nothing()))
        f = lambda x: OptionT(Right(Some(x + 1)))
        g = lambda x: OptionT(Right(Some(x * 2)))
        left = m.bind(f).bind(g).run()
        right = m.bind(lambda x: f(x).bind(g)).run()
        assert left == right


class TestBrokenShortCircuit:
    """Demonstrates what goes wrong without proper Nothing short-circuiting.

    If bind doesn't check for Nothing and always passes to f,
    you get wrong results — Nothing leaks through as a value.
    """

    def test_without_short_circuit_produces_wrong_result(self):
        """A naive bind that doesn't check Nothing wraps Nothing as a value."""

        class BrokenOptionT:
            def __init__(self, run):
                self._run = run

            def run(self):
                return self._run

            def bind(self, f):
                # BUG: doesn't check for Nothing, passes raw Option to f
                return BrokenOptionT(self._run.bind(lambda opt: f(opt).run()))

        # Without short-circuit, Nothing() leaks through as a value
        result = (
            BrokenOptionT(Right(Nothing()))
            .bind(lambda x: BrokenOptionT(Right(Some(x))))
            .run()
        )
        # BUG: produces Right(Some(Nothing())) instead of Right(Nothing())
        assert result == Right(Some(Nothing()))

        # Correct OptionT short-circuits:
        correct = (
            OptionT(Right(Nothing())).bind(lambda x: OptionT(Right(Some(x)))).run()
        )
        assert correct == Right(Nothing())
