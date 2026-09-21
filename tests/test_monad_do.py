"""Tests for Monad.do — the generic do-notation implementation.

Monad.do is defined once on the Monad typeclass and works for all monadic
types via bind/pure. DataType.do delegates to it via summon. Per-type
do implementations are not needed.
"""

import asyncio

from funstruct.typeclasses import Monad, MonadError, summon
from funstruct.types.cons import CList, Cons, Nil
from funstruct.types.either import Either, Left, Right
from funstruct.types.future import Future
from funstruct.types.option import Nothing, Option, Some
from funstruct.types.reader import Reader
from funstruct.types.result import AsyncResult, Err, Ok, Result
from funstruct.types.state import State
from funstruct.types.writer import ListWriter


def run_async(ar):
    return asyncio.run(ar._awaitable())


# ── DataType.do (class-level delegation) ────────────────────────────


class TestDataTypeDo:
    """DataType.do delegates to summon(Monad, cls).do."""

    def test_result_do(self):
        @Result.do
        def pipeline():
            x = yield Ok(10)
            y = yield Ok(x + 1)
            return x + y

        assert pipeline() == Ok(21)

    def test_option_do(self):
        @Option.do
        def pipeline():
            x = yield Some(5)
            y = yield Some(x * 2)
            return x + y

        assert pipeline() == Some(15)

    def test_either_do(self):
        @Either.do
        def pipeline():
            x = yield Right(1)
            y = yield Right(2)
            return x + y

        assert pipeline() == Right(3)

    def test_async_result_do(self):
        @AsyncResult.do
        def pipeline():
            x = yield AsyncResult.pure(10)
            y = yield AsyncResult.pure(x + 1)
            return x + y

        assert run_async(pipeline()) == Ok(21)

    def test_future_do(self):
        @Future.do
        def pipeline():
            x = yield Future.pure(1)
            y = yield Future.pure(x + 10)
            return x + y

        assert asyncio.run(pipeline()._awaitable()) == 12


# ── Monad.do via summon ─────────────────────────────────────────────


class TestMonadDoViaSummon:
    """summon(Monad, Type).do works for all monadic types."""

    def test_result(self):
        M = summon(Monad, Result)

        @M.do
        def pipeline():
            x = yield Ok(10)
            y = yield Ok(x + 1)
            return x + y

        assert pipeline() == Ok(21)

    def test_option(self):
        M = summon(Monad, Option)

        @M.do
        def pipeline():
            x = yield Some(5)
            y = yield Some(x * 2)
            return x + y

        assert pipeline() == Some(15)

    def test_either(self):
        M = summon(Monad, Either)

        @M.do
        def pipeline():
            x = yield Right(1)
            y = yield Right(x + 10)
            return x + y

        assert pipeline() == Right(12)

    def test_state(self):
        M = summon(Monad, State)

        @M.do
        def pipeline():
            x = yield State(lambda s: (s + 1, s))
            y = yield State(lambda s: (s + 1, s))
            return x + y

        assert pipeline().run(0) == (2, 1)

    def test_reader(self):
        M = summon(Monad, Reader)

        @M.do
        def pipeline():
            x = yield Reader(lambda ctx: ctx["x"])
            y = yield Reader(lambda ctx: ctx["y"])
            return x + y

        assert pipeline().run({"x": 1, "y": 10}) == 11

    def test_writer(self):
        M = summon(Monad, ListWriter)

        @M.do
        def pipeline():
            x = yield ListWriter(10, ["step1"])
            y = yield ListWriter(x + 1, ["step2"])
            return y

        result = pipeline()
        assert result.value == 11
        assert result.output == ["step1", "step2"]


# ── Short-circuiting ────────────────────────────────────────────────


class TestDoShortCircuit:
    """do-notation short-circuits on error cases."""

    def test_result_short_circuits_on_err(self):
        @Result.do
        def pipeline():
            x = yield Ok(10)
            y = yield Err(ValueError("boom"))
            return x + y

        result = pipeline()
        assert result.is_err

    def test_option_short_circuits_on_nothing(self):
        @Option.do
        def pipeline():
            x = yield Some(10)
            y = yield Nothing()
            return x + y

        assert pipeline() == Nothing()

    def test_either_short_circuits_on_left(self):
        @Either.do
        def pipeline():
            x = yield Right(10)
            y = yield Left("fail")
            return x + y

        assert pipeline() == Left("fail")

    def test_async_result_short_circuits(self):
        @AsyncResult.do
        def pipeline():
            x = yield AsyncResult.pure(10)
            y = yield AsyncResult.raise_error(ValueError("boom"))
            return x + y

        assert run_async(pipeline()).is_err


# ── Arguments ───────────────────────────────────────────────────────


class TestDoWithArgs:
    """do-notation passes arguments through to the generator function."""

    def test_result_with_args(self):
        @Result.do
        def add(a, b):
            x = yield Ok(a)
            y = yield Ok(b)
            return x + y

        assert add(3, 7) == Ok(10)

    def test_async_result_with_args(self):
        @AsyncResult.do
        def multiply(base, factor):
            x = yield AsyncResult.pure(base)
            y = yield AsyncResult.pure(factor)
            return x * y

        assert run_async(multiply(5, 3)) == Ok(15)

    def test_summon_with_args(self):
        M = summon(MonadError, Result)

        @M.do
        def divide(a, b):
            if b == 0:
                yield M.raise_error(ValueError("division by zero"))
            return a / b

        assert divide(10, 2) == Ok(5.0)
        assert divide(10, 0).is_err


class TestCListDo:
    """do-notation works for the list monad (CList) via generator replay."""

    def test_cartesian_product(self):
        @CList.do
        def pipeline():
            x = yield CList.from_iterable([1, 2])
            y = yield CList.from_iterable(["a", "b"])
            return (x, y)

        assert pipeline() == CList.from_iterable([(1, "a"), (1, "b"), (2, "a"), (2, "b")])

    def test_dependent_values(self):
        @CList.do
        def pipeline():
            x = yield CList.from_iterable([1, 2, 3])
            y = yield CList.from_iterable([x, x * 10])
            return (x, y)

        assert pipeline() == CList.from_iterable([(1, 1), (1, 10), (2, 2), (2, 20), (3, 3), (3, 30)])

    def test_single_step(self):
        @CList.do
        def pipeline():
            x = yield CList.from_iterable([10, 20, 30])
            return x + 1

        assert pipeline() == CList.from_iterable([11, 21, 31])

    def test_three_steps(self):
        @CList.do
        def pipeline():
            x = yield CList.from_iterable([1, 2])
            y = yield CList.from_iterable([10, 20])
            z = yield CList.from_iterable([100, 200])
            return x + y + z

        assert pipeline() == CList.from_iterable([
            111, 211, 121, 221, 112, 212, 122, 222,
        ])

    def test_with_args(self):
        @CList.do
        def pipeline(base):
            x = yield CList.from_iterable([base, base * 2])
            return x + 1

        assert pipeline(5) == CList.from_iterable([6, 11])
