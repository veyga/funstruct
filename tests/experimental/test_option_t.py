"""Tests for OptionT monad transformer."""

import pytest

from funstruct.monad.either import Either, Left, Right
from funstruct.monad.option import Nothing, Some
from funstruct.experimental.monadtransformer.option_t import OptionT


class TestMap:
    def test_maps_some(self):
        assert OptionT(Right(Some(5))).map(lambda x: x * 2).run() == Right(Some(10))

    def test_skips_nothing(self):
        called = False

        def f(x):
            nonlocal called
            called = True
            return x * 2

        result = OptionT(Right(Nothing())).map(f).run()

        assert result == Right(Nothing())
        assert not called

    def test_skips_left(self):
        called = False

        def f(x):
            nonlocal called
            called = True
            return x * 2

        result = OptionT(Left("err")).map(f).run()

        assert result == Left("err")
        assert not called

    def test_map_identity(self):
        values = [
            OptionT(Right(Some(5))),
            OptionT(Right(Nothing())),
            OptionT(Left("err")),
        ]

        for m in values:
            assert m.map(lambda x: x).run() == m.run()

    def test_map_composition(self):
        values = [
            OptionT(Right(Some(5))),
            OptionT(Right(Nothing())),
            OptionT(Left("err")),
        ]

        for m in values:
            left = m.map(lambda x: x + 1).map(lambda x: x * 2).run()
            right = m.map(lambda x: (x + 1) * 2).run()
            assert left == right


class TestBind:
    def test_chains_some(self):
        result = (
            OptionT(Right(Some(1))).bind(lambda x: OptionT(Right(Some(x + 10)))).run()
        )
        assert result == Right(Some(11))

    def test_bind_produces_nothing(self):
        result = OptionT(Right(Some(1))).bind(lambda x: OptionT(Right(Nothing()))).run()
        assert result == Right(Nothing())

    def test_bind_produces_left(self):
        result = OptionT(Right(Some(1))).bind(lambda x: OptionT(Left("boom"))).run()
        assert result == Left("boom")

    def test_short_circuits_nothing(self):
        called = False

        def f(x):
            nonlocal called
            called = True
            return OptionT(Right(Some(x + 10)))

        result = OptionT(Right(Nothing())).bind(f).run()

        assert result == Right(Nothing())
        assert not called

    def test_short_circuits_left(self):
        called = False

        def f(x):
            nonlocal called
            called = True
            return OptionT(Right(Some(x + 10)))

        result = OptionT(Left("err")).bind(f).run()

        assert result == Left("err")
        assert not called

    def test_multi_step(self):
        result = (
            OptionT(Right(Some(1)))
            .bind(lambda x: OptionT(Right(Some(x + 1))))
            .bind(lambda x: OptionT(Right(Some(x + 1))))
            .run()
        )
        assert result == Right(Some(3))


class TestHandleErrorWith:
    def test_recovers_from_nothing(self):
        result = (
            OptionT(Right(Nothing()))
            .handle_error_with(lambda: OptionT(Right(Some(99))))
            .run()
        )
        assert result == Right(Some(99))

    def test_skips_on_some(self):
        called = False

        def fallback():
            nonlocal called
            called = True
            return OptionT(Right(Some(99)))

        result = OptionT(Right(Some(1))).handle_error_with(fallback).run()

        assert result == Right(Some(1))
        assert not called

    def test_does_not_recover_left(self):
        """or_else only handles Nothing, not outer monad failure."""
        called = False

        def fallback():
            nonlocal called
            called = True
            return OptionT(Right(Some(99)))

        result = OptionT(Left("err")).handle_error_with(fallback).run()

        assert result == Left("err")
        assert not called

    def test_propagates_fallback_failure(self):
        result = (
            OptionT(Right(Nothing()))
            .handle_error_with(lambda: OptionT(Left("fallback failed")))
            .run()
        )
        assert result == Left("fallback failed")


class TestThen:
    def test_sequences(self):
        result = (
            OptionT(Right(Some("discard"))).then(OptionT(Right(Some("keep")))).run()
        )
        assert result == Right(Some("keep"))

    def test_short_circuits_nothing(self):
        result = OptionT(Right(Nothing())).then(OptionT(Right(Some("never")))).run()
        assert result == Right(Nothing())

    def test_short_circuits_left(self):
        result = OptionT(Left("err")).then(OptionT(Right(Some("never")))).run()
        assert result == Left("err")


class TestPure:
    def test_pure(self):
        assert OptionT.pure(42, Either).run() == Right(Some(42))

    def test_none(self):
        assert OptionT.none(Either).run() == Right(Nothing())

    def test_pure_preserves_python_none_as_a_value(self):
        assert OptionT.pure(None, Either).run() == Right(Some(None))


class TestLift:
    def test_lift_right(self):
        assert OptionT.lift_f(Right(42)).run() == Right(Some(42))

    def test_lift_left(self):
        assert OptionT.lift_f(Left("err")).run() == Left("err")

    def test_lift_is_equivalent_to_mapping_some(self):
        value = Right(42)

        assert OptionT.lift_f(value).run() == value.map(Some)


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

    def test_then_and_and_then_are_equivalent(self):
        a = OptionT(Right(Some(1)))
        b = OptionT(Right(Some(2)))

        assert a.then(b).run() == a.and_then(b).run()


class TestWithOption:
    """OptionT over Option preserves the nested Option structure."""

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

        assert pipeline().run() == Right(Some(12))

    def test_short_circuits_nothing(self):
        @OptionT.do
        def pipeline():
            x = yield OptionT(Right(Some(1)))
            y = yield OptionT(Right(Nothing()))
            return x + y

        assert pipeline().run() == Right(Nothing())

    def test_short_circuits_left(self):
        @OptionT.do
        def pipeline():
            x = yield OptionT(Right(Some(1)))
            y = yield OptionT(Left("boom"))
            return x + y

        assert pipeline().run() == Left("boom")


class TestLaws:
    """Monad laws for OptionT over Either."""

    @pytest.mark.parametrize("a", [5, 0, -1])
    def test_left_identity(self, a):
        """pure(a).bind(f) == f(a)."""
        f = lambda x: OptionT(Right(Some(x + 1)))

        left = OptionT.pure(a, Either).bind(f).run()
        right = f(a).run()

        assert left == right

    @pytest.mark.parametrize(
        "m",
        [
            OptionT(Right(Some(5))),
            OptionT(Right(Nothing())),
            OptionT(Left("err")),
        ],
    )
    def test_right_identity(self, m):
        """m.bind(pure) == m."""
        left = m.bind(lambda x: OptionT.pure(x, Either)).run()
        right = m.run()

        assert left == right

    @pytest.mark.parametrize(
        "m",
        [
            OptionT(Right(Some(5))),
            OptionT(Right(Nothing())),
            OptionT(Left("err")),
        ],
    )
    def test_associativity(self, m):
        """m.bind(f).bind(g) == m.bind(x -> f(x).bind(g))."""
        f = lambda x: OptionT(Right(Some(x + 1)))
        g = lambda x: OptionT(Right(Some(x * 2)))

        left = m.bind(f).bind(g).run()
        right = m.bind(lambda x: f(x).bind(g)).run()

        assert left == right

    @pytest.mark.parametrize(
        "m",
        [
            OptionT(Right(Some(5))),
            OptionT(Right(Nothing())),
            OptionT(Left("err")),
        ],
    )
    def test_associativity_with_short_circuit(self, m):
        """Associativity holds when f produces Nothing."""
        f = lambda x: OptionT(Right(Nothing()))
        g = lambda x: OptionT(Right(Some(x * 2)))

        left = m.bind(f).bind(g).run()
        right = m.bind(lambda x: f(x).bind(g)).run()

        assert left == right
