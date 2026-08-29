"""Tests for Future — lazy async computation."""

import asyncio

from funstruct.monad.either import Left, Right
from funstruct.monad.result import AsyncResult, TryAsync


def run(future):
    """Helper: await a Future and return the Either."""
    return asyncio.run(future._awaitable())


class TestPure:
    def test_pure_succeeds(self):
        assert run(AsyncResult.pure(42)) == Right(42)

    def test_from_error_fails(self):
        assert run(AsyncResult.from_error("oops")) == Left("oops")

    def test_from_either_right(self):
        assert run(AsyncResult.from_either(Right(1))) == Right(1)

    def test_from_either_left(self):
        assert run(AsyncResult.from_either(Left("err"))) == Left("err")


class TestTryAsyncWrapping:
    def test_success(self):
        @TryAsync
        async def coro():
            return 42

        assert run(coro()) == Right(42)

    def test_catches_exception(self):
        @TryAsync
        async def coro():
            raise ValueError("boom")

        result = run(coro())
        assert result.is_left
        match result:
            case Left(e):
                assert type(e) is ValueError


class TestMap:
    def test_maps_success(self):
        result = run(AsyncResult.pure(5).map(lambda x: x * 2))
        assert result == Right(10)

    def test_skips_on_error(self):
        result = run(AsyncResult.from_error("err").map(lambda x: x * 2))
        assert result == Left("err")

    def test_chains_maps(self):
        result = run(AsyncResult.pure(1).map(lambda x: x + 1).map(lambda x: x * 10))
        assert result == Right(20)


class TestBind:
    def test_chains_futures(self):
        result = run(AsyncResult.pure(1).bind(lambda x: AsyncResult.pure(x + 10)))
        assert result == Right(11)

    def test_short_circuits_on_error(self):
        result = run(
            AsyncResult.from_error("stop").bind(lambda x: AsyncResult.pure(x + 1))
        )
        assert result == Left("stop")

    def test_bind_can_fail(self):
        result = run(
            AsyncResult.pure(1).bind(lambda x: AsyncResult.from_error("failed"))
        )
        assert result == Left("failed")


class TestBindEither:
    def test_success(self):
        result = run(AsyncResult.pure(5).bind_either(lambda x: Right(x * 2)))
        assert result == Right(10)

    def test_failure(self):
        result = run(AsyncResult.pure(5).bind_either(lambda x: Left("nope")))
        assert result == Left("nope")

    def test_skips_on_initial_error(self):
        result = run(AsyncResult.from_error("err").bind_either(lambda x: Right(99)))
        assert result == Left("err")


class TestBindAwaitable:
    def test_success(self):
        async def double(x):
            return x * 2

        result = run(AsyncResult.pure(5).bind_awaitable(double))
        assert result == Right(10)

    def test_skips_on_error(self):
        async def double(x):
            return x * 2

        result = run(AsyncResult.from_error("err").bind_awaitable(double))
        assert result == Left("err")


class TestOrElse:
    def test_recovers_from_error(self):
        result = run(
            AsyncResult.from_error("oops").or_else(
                lambda e: AsyncResult.pure(f"recovered: {e}")
            )
        )
        assert result == Right("recovered: oops")

    def test_skips_on_success(self):
        result = run(AsyncResult.pure(42).or_else(lambda e: AsyncResult.pure(0)))
        assert result == Right(42)

    def test_or_else_either(self):
        result = run(
            AsyncResult.from_error("oops").or_else_either(lambda e: Right("fixed"))
        )
        assert result == Right("fixed")


class TestThen:
    def test_sequences(self):
        result = run(AsyncResult.pure("discard").then(AsyncResult.pure("keep")))
        assert result == Right("keep")

    def test_short_circuits(self):
        result = run(AsyncResult.from_error("stop").then(AsyncResult.pure("never")))
        assert result == Left("stop")


class TestAp:
    def test_tuples_values(self):
        result = run(AsyncResult.pure(1).ap(AsyncResult.pure(2)))
        assert result == Right((1, 2))

    def test_short_circuits_left(self):
        result = run(AsyncResult.from_error("err").ap(AsyncResult.pure(2)))
        assert result == Left("err")


class TestTryAsync:
    def test_success(self):
        @TryAsync
        async def fetch(id):
            return {"id": id, "name": "alice"}

        assert run(fetch(1)) == Right({"id": 1, "name": "alice"})

    def test_catches_exception(self):
        @TryAsync
        async def fetch(id):
            raise ValueError(f"not found: {id}")

        result = run(fetch(99))
        assert result.is_left
        match result:
            case Left(e):
                assert "not found: 99" in str(e)

    def test_preserves_function_name(self):
        @TryAsync
        async def my_func():
            return 1

        assert my_func.__name__ == "my_func"


class TestPipeline:
    """Integration test: multi-step async pipeline."""

    def test_full_pipeline(self):
        @TryAsync
        async def fetch_user(id):
            if id == 1:
                return {"name": "alice", "email": "alice@example.com"}
            raise ValueError(f"user {id} not found")

        @TryAsync
        async def send_email(email):
            return f"sent to {email}"

        pipeline = fetch_user(1).map(lambda u: u["email"]).bind(send_email)
        assert run(pipeline) == Right("sent to alice@example.com")

    def test_pipeline_short_circuits(self):
        @TryAsync
        async def fetch_user(id):
            raise ValueError(f"user {id} not found")

        @TryAsync
        async def send_email(email):
            return f"sent to {email}"

        pipeline = fetch_user(99).map(lambda u: u["email"]).bind(send_email)
        result = run(pipeline)
        assert result.is_left

    def test_pipeline_with_recovery(self):
        pipeline = (
            AsyncResult.from_error("timeout")
            .or_else(lambda e: AsyncResult.pure("cached"))
            .map(lambda v: v.upper())
        )
        assert run(pipeline) == Right("CACHED")
