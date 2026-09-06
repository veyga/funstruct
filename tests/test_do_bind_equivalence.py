"""Tests that do-notation and bind chains produce identical results.

For every monad, the do syntax is syntactic sugar for bind. These tests
verify both paths give the same result for success AND failure cases.
"""

import asyncio

from funstruct.monad.either import Either, Right, Left
from funstruct.monad.option import Option, Some, Nothing
from funstruct.monad.result import Result, Ok, Err, AsyncResult
from funstruct.monad.state import State
from funstruct.monad.reader import Reader


class TestEitherEquivalence:
    def test_success(self):
        @Either.do
        def do_version():
            x = yield Right(1)
            y = yield Right(x + 10)
            return x + y

        bind_version = Right(1).bind(lambda x: Right(x + 10).map(lambda y: x + y))

        assert do_version() == bind_version

    def test_short_circuit(self):
        @Either.do
        def do_version():
            x = yield Right(1)
            y = yield Left("boom")
            return x + y

        bind_version = Right(1).bind(lambda x: Left("boom").map(lambda y: x + y))

        assert do_version() == bind_version == Left("boom")


class TestOptionEquivalence:
    def test_success(self):
        @Option.do
        def do_version():
            x = yield Some(1)
            y = yield Some(x + 10)
            return x + y

        bind_version = Some(1).bind(lambda x: Some(x + 10).map(lambda y: x + y))

        assert do_version() == bind_version

    def test_short_circuit(self):
        @Option.do
        def do_version():
            x = yield Some(1)
            y = yield Nothing()
            return x + y

        bind_version = Some(1).bind(lambda x: Nothing().map(lambda y: x + y))

        assert do_version() == bind_version == Nothing()


class TestResultEquivalence:
    def test_success(self):
        @Result.do
        def do_version():
            x = yield Ok(1)
            y = yield Ok(x + 10)
            return x + y

        bind_version = Ok(1).bind(lambda x: Ok(x + 10).map(lambda y: x + y))

        assert do_version() == bind_version

    def test_short_circuit(self):
        err = Err(ValueError("boom"))

        @Result.do
        def do_version():
            x = yield Ok(1)
            y = yield err
            return x + y

        bind_version = Ok(1).bind(lambda x: err.map(lambda y: x + y))

        assert do_version() == bind_version


class TestAsyncResultEquivalence:
    def _run(self, ar):
        return asyncio.run(ar._awaitable())

    def test_success(self):
        @AsyncResult.do
        def do_version():
            x = yield AsyncResult.pure(1)
            y = yield AsyncResult.pure(x + 10)
            return x + y

        bind_version = AsyncResult.pure(1).bind(
            lambda x: AsyncResult.pure(x + 10).map(lambda y: x + y)
        )

        assert self._run(do_version()) == self._run(bind_version)

    def test_short_circuit(self):
        @AsyncResult.do
        def do_version():
            x = yield AsyncResult.pure(1)
            y = yield AsyncResult.raise_error(ValueError("boom"))
            return x + y

        bind_version = AsyncResult.pure(1).bind(
            lambda x: AsyncResult.raise_error(ValueError("boom")).map(
                lambda y: x + y
            )
        )

        do_result = self._run(do_version())
        bind_result = self._run(bind_version)
        assert do_result.is_err
        assert bind_result.is_err


class TestStateEquivalence:
    def test_success(self):
        inc = State(lambda s: (s + 1, s))

        @State.do
        def do_version():
            a = yield inc
            b = yield inc
            return (a, b)

        bind_version = inc.bind(lambda a: inc.map(lambda b: (a, b)))

        assert do_version().run(0) == bind_version.run(0) == (2, (0, 1))


class TestReaderEquivalence:
    def test_success(self):
        get_x = Reader(lambda ctx: ctx["x"])
        get_y = Reader(lambda ctx: ctx["y"])

        @Reader.do
        def do_version():
            x = yield get_x
            y = yield get_y
            return x + y

        bind_version = get_x.bind(lambda x: get_y.map(lambda y: x + y))

        ctx = {"x": 10, "y": 20}
        assert do_version().run(ctx) == bind_version.run(ctx) == 30


class TestDoNotationLimitations:
    """@do uses generators (yield), NOT coroutines (async/await).

    Key rules:
        1. @Result.do / @Option.do takes a regular generator function (def + yield)
        2. You CANNOT decorate an async def with @do — it won't work
        3. You CANNOT yield AsyncResult from @Result.do — it won't unwrap
        4. For async pipelines, use @AsyncResult.do (which awaits internally)
        5. To mix sync Result into @AsyncResult.do, use AsyncResult.from_result()
    """

    def test_do_takes_generator_not_coroutine(self):
        """@Result.do works with generators. async def is not a generator."""

        @Result.do
        def sync_pipeline():
            x = yield Ok(10)
            y = yield Ok(20)
            return x + y

        assert sync_pipeline() == Ok(30)

    def test_async_result_is_not_ok_or_err(self):
        """AsyncResult is not Ok or Err — it can't be pattern-matched in sync do.

        @Result.do matches on Ok(value) / Err(). An AsyncResult is neither,
        so yielding one in @Result.do would spin forever. Don't do it.
        """
        ar = AsyncResult.pure(20)
        assert not isinstance(ar, Ok)
        assert not isinstance(ar, Err)

    def test_async_do_awaits_properly(self):
        """@AsyncResult.do handles async values correctly."""
        @AsyncResult.do
        def async_pipeline():
            x = yield AsyncResult.pure(10)
            y = yield AsyncResult.pure(20)
            return x + y

        result = asyncio.run(async_pipeline()._awaitable())
        assert result == Ok(30)

    def test_mixing_sync_result_into_async_do(self):
        """Use AsyncResult.from_result() to lift sync Result into async do."""
        @AsyncResult.do
        def pipeline():
            x = yield AsyncResult.from_result(Ok(10))
            y = yield AsyncResult.pure(20)
            return x + y

        result = asyncio.run(pipeline()._awaitable())
        assert result == Ok(30)
