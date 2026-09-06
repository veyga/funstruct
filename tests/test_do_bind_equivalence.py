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
            y = yield AsyncResult.from_exception(ValueError("boom"))
            return x + y

        bind_version = AsyncResult.pure(1).bind(
            lambda x: AsyncResult.from_exception(ValueError("boom")).map(
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
