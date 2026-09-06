"""Tests for Future — lazy async computation."""

import asyncio

import pytest

from funstruct.monad.either import Left, Right
from funstruct.monad.future import Future
from funstruct.monad.result import AsyncResult, Err, Ok, TryAsync


def run(future):
    """Helper: await a Future and return the Result."""
    return asyncio.run(future._awaitable())


class TestAwaitable:
    """Future and AsyncResult are directly awaitable — no .run() needed."""

    def test_future_is_awaitable(self):
        async def go():
            return await Future.pure(42)

        assert asyncio.run(go()) == 42

    def test_async_result_is_awaitable(self):
        async def go():
            return await AsyncResult.pure(42)

        assert asyncio.run(go()) == Ok(42)

    def test_async_result_is_not_callable(self):
        ar = AsyncResult.pure(42)
        with pytest.raises(TypeError):
            ar()

    def test_async_result_has_no_run(self):
        ar = AsyncResult.pure(42)
        assert not hasattr(ar, "run")


class TestPure:
    def test_pure_succeeds(self):
        assert run(AsyncResult.pure(42)) == Ok(42)

    def test_from_exception_fails(self):
        err = ValueError("oops")
        result = run(AsyncResult.from_exception(err))
        assert result == Err(err)

    def test_from_either_right(self):
        assert run(AsyncResult.from_either(Right(1))) == Right(1)

    def test_from_either_left(self):
        assert run(AsyncResult.from_either(Left("err"))) == Left("err")

    def test_from_result_ok(self):
        assert run(AsyncResult.from_result(Ok(1))) == Ok(1)

    def test_from_result_err(self):
        err = ValueError("bad")
        assert run(AsyncResult.from_result(Err(err))) == Err(err)


class TestTryAsyncWrapping:
    def test_success(self):
        @TryAsync
        async def coro():
            return 42

        assert run(coro()) == Ok(42)

    def test_catches_exception(self):
        @TryAsync
        async def coro():
            raise ValueError("boom")

        result = run(coro())
        assert result.is_err
        match result:
            case Err(e):
                assert type(e) is ValueError


class TestMap:
    def test_maps_success(self):
        result = run(AsyncResult.pure(5).map(lambda x: x * 2))
        assert result == Ok(10)

    def test_skips_on_error(self):
        err = RuntimeError("err")
        result = run(AsyncResult.from_exception(err).map(lambda x: x * 2))
        assert result == Err(err)

    def test_chains_maps(self):
        result = run(AsyncResult.pure(1).map(lambda x: x + 1).map(lambda x: x * 10))
        assert result == Ok(20)


class TestBind:
    def test_chains_futures(self):
        result = run(AsyncResult.pure(1).bind(lambda x: AsyncResult.pure(x + 10)))
        assert result == Ok(11)

    def test_short_circuits_on_error(self):
        err = RuntimeError("stop")
        result = run(
            AsyncResult.from_exception(err).bind(lambda x: AsyncResult.pure(x + 1))
        )
        assert result == Err(err)

    def test_bind_can_fail(self):
        err = RuntimeError("failed")
        result = run(
            AsyncResult.pure(1).bind(lambda x: AsyncResult.from_exception(err))
        )
        assert result == Err(err)


class TestBindWithEither:
    def test_success(self):
        result = run(AsyncResult.pure(5).bind(lambda x: Right(x * 2)))
        assert result == Right(10)

    def test_failure(self):
        result = run(AsyncResult.pure(5).bind(lambda x: Left("nope")))
        assert result == Left("nope")

    def test_skips_on_initial_error(self):
        err = RuntimeError("err")
        result = run(AsyncResult.from_exception(err).bind(lambda x: Right(99)))
        assert result == Err(err)


class TestBindWithResult:
    def test_success(self):
        result = run(AsyncResult.pure(5).bind(lambda x: Ok(x * 2)))
        assert result == Ok(10)

    def test_failure(self):
        result = run(AsyncResult.pure(5).bind(lambda x: Err(ValueError("nope"))))
        match result:
            case Err(e):
                assert str(e) == "nope"


class TestBindWithAwaitable:
    def test_success(self):
        async def double(x):
            return x * 2

        result = run(AsyncResult.pure(5).bind(double))
        assert result == Ok(10)

    def test_skips_on_error(self):
        async def double(x):
            return x * 2

        err = RuntimeError("err")
        result = run(AsyncResult.from_exception(err).bind(double))
        assert result == Err(err)


class TestHandleErrorWith:
    def test_recovers_from_error(self):
        err = ValueError("oops")
        result = run(
            AsyncResult.from_exception(err).handle_error_with(
                lambda e: AsyncResult.pure(f"recovered: {e}")
            )
        )
        assert result == Ok("recovered: oops")

    def test_skips_on_success(self):
        result = run(
            AsyncResult.pure(42).handle_error_with(lambda e: AsyncResult.pure(0))
        )
        assert result == Ok(42)

    def test_handle_error_with_either(self):
        err = ValueError("oops")
        result = run(
            AsyncResult.from_exception(err).handle_error_with(lambda e: Right("fixed"))
        )
        assert result == Right("fixed")

    def test_handle_error_with_result(self):
        err = ValueError("oops")
        result = run(
            AsyncResult.from_exception(err).handle_error_with(lambda e: Ok("fixed"))
        )
        assert result == Ok("fixed")


class TestThen:
    def test_sequences(self):
        result = run(AsyncResult.pure("discard").then(AsyncResult.pure("keep")))
        assert result == Ok("keep")

    def test_short_circuits(self):
        err = RuntimeError("stop")
        result = run(AsyncResult.from_exception(err).then(AsyncResult.pure("never")))
        assert result == Err(err)


class TestAp:
    def test_applies_function(self):
        result = run(AsyncResult.pure(lambda x: x + 1).ap(AsyncResult.pure(2)))
        assert result == Ok(3)

    def test_short_circuits_err(self):
        err = RuntimeError("err")
        result = run(AsyncResult.from_exception(err).ap(AsyncResult.pure(2)))
        assert result == Err(err)


class TestTryAsync:
    def test_success(self):
        @TryAsync
        async def fetch(id):
            return {"id": id, "name": "alice"}

        assert run(fetch(1)) == Ok({"id": 1, "name": "alice"})

    def test_catches_exception(self):
        @TryAsync
        async def fetch(id):
            raise ValueError(f"not found: {id}")

        result = run(fetch(99))
        assert result.is_err
        match result:
            case Err(e):
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
        assert run(pipeline) == Ok("sent to alice@example.com")

    def test_pipeline_short_circuits(self):
        @TryAsync
        async def fetch_user(id):
            raise ValueError(f"user {id} not found")

        @TryAsync
        async def send_email(email):
            return f"sent to {email}"

        pipeline = fetch_user(99).map(lambda u: u["email"]).bind(send_email)
        result = run(pipeline)
        assert result.is_err

    def test_pipeline_with_recovery(self):
        pipeline = (
            AsyncResult.from_exception(TimeoutError("timeout"))
            .handle_error_with(lambda e: AsyncResult.pure("cached"))
            .map(lambda v: v.upper())
        )
        assert run(pipeline) == Ok("CACHED")


class TestAsyncResultDo:
    def test_success(self):
        @AsyncResult.do
        def pipeline():
            x = yield AsyncResult.pure(1)
            y = yield AsyncResult.pure(x + 10)
            return x + y

        assert run(pipeline()) == Ok(12)

    def test_short_circuits_on_err(self):
        @AsyncResult.do
        def pipeline():
            x = yield AsyncResult.pure(1)
            y = yield AsyncResult.from_exception(ValueError("boom"))
            return x + y

        result = run(pipeline())
        assert result.is_err

    def test_multiple_binds(self):
        @AsyncResult.do
        def pipeline():
            a = yield AsyncResult.pure(10)
            b = yield AsyncResult.pure(20)
            c = yield AsyncResult.pure(30)
            return a + b + c

        assert run(pipeline()) == Ok(60)

    def test_with_args(self):
        def pipeline(base):
            x = yield AsyncResult.pure(base)
            y = yield AsyncResult.pure(x * 2)
            return x + y

        assert run(AsyncResult.do(pipeline)(5)) == Ok(15)

    def test_accepts_lifted_result(self):
        @AsyncResult.do
        def pipeline():
            x = yield AsyncResult.pure(1)
            y = yield AsyncResult.from_result(Ok(10))
            return x + y

        assert run(pipeline()) == Ok(11)

    def test_short_circuits_on_lifted_err(self):
        @AsyncResult.do
        def pipeline():
            x = yield AsyncResult.pure(1)
            y = yield AsyncResult.from_result(Err(ValueError("sync error")))
            return x + y

        result = run(pipeline())
        assert result.is_err


class TestFutureDo:
    def _run_future(self, future):
        return asyncio.run(future._awaitable())

    def test_success(self):
        @Future.do
        def pipeline():
            x = yield Future.pure(1)
            y = yield Future.pure(x + 10)
            return x + y

        assert self._run_future(pipeline()) == 12

    def test_multiple_binds(self):
        @Future.do
        def pipeline():
            a = yield Future.pure(10)
            b = yield Future.pure(20)
            c = yield Future.pure(30)
            return a + b + c

        assert self._run_future(pipeline()) == 60

    def test_with_args(self):
        def pipeline(base):
            x = yield Future.pure(base)
            y = yield Future.pure(x * 2)
            return y

        result = self._run_future(Future.do(pipeline)(21))
        assert result == 42


class TestTryAsyncWithSyncFunctions:
    """TryAsync accepts sync functions, wrapping them in AsyncResult."""

    def test_sync_success(self):
        @TryAsync
        def parse_int(s):
            return int(s)

        assert run(parse_int("42")) == Ok(42)

    def test_sync_catches_exception(self):
        @TryAsync
        def parse_int(s):
            return int(s)

        result = run(parse_int("not a number"))
        assert isinstance(result, Err)
        match result:
            case Err(e):
                assert isinstance(e, ValueError)

    def test_sync_preserves_function_name(self):
        @TryAsync
        def my_sync_func():
            return 1

        assert my_sync_func.__name__ == "my_sync_func"

    def test_sync_with_args(self):
        @TryAsync
        def add(a, b):
            return a + b

        assert run(add(3, 4)) == Ok(7)


class TestTryAsyncWithFuture:
    """TryAsync accepts functions returning Future (awaitable, not coroutine)."""

    def test_future_returning_function(self):
        @TryAsync
        def get_value():
            return Future.pure(42)

        assert run(get_value()) == Ok(42)

    def test_future_with_args(self):
        @TryAsync
        def double(x):
            return Future.pure(x * 2)

        assert run(double(21)) == Ok(42)

    def test_future_exception_in_wrapper(self):
        @TryAsync
        def bad():
            raise RuntimeError("sync boom")

        result = run(bad())
        assert isinstance(result, Err)
        match result:
            case Err(e):
                assert isinstance(e, RuntimeError)


class TestTryAsyncComposition:
    """Compose sync, async, and Future-returning functions in one pipeline."""

    def test_sync_into_async_pipeline(self):
        @TryAsync
        def parse(raw):
            return int(raw)

        @TryAsync
        async def fetch(id):
            return {"id": id, "name": "alice"}

        pipeline = parse("1").bind(fetch)
        assert run(pipeline) == Ok({"id": 1, "name": "alice"})

    def test_async_into_sync_pipeline(self):
        @TryAsync
        async def fetch_name():
            return "alice"

        @TryAsync
        def upper(s):
            return s.upper()

        pipeline = fetch_name().bind(upper)
        assert run(pipeline) == Ok("ALICE")

    def test_sync_into_future_pipeline(self):
        @TryAsync
        def parse(raw):
            return int(raw)

        def async_double(x):
            return AsyncResult.pure(x * 2)

        pipeline = parse("5").bind(async_double)
        assert run(pipeline) == Ok(10)

    def test_three_step_mixed_pipeline(self):
        @TryAsync
        def parse(raw):
            return int(raw)

        @TryAsync
        async def fetch_user(id):
            if id == 1:
                return "alice@example.com"
            raise ValueError(f"not found: {id}")

        @TryAsync
        def format_email(email):
            return f"<{email}>"

        pipeline = parse("1").bind(fetch_user).bind(format_email)
        assert run(pipeline) == Ok("<alice@example.com>")

    def test_mixed_pipeline_short_circuits_on_sync_error(self):
        @TryAsync
        def parse(raw):
            return int(raw)

        @TryAsync
        async def fetch_user(id):
            return {"id": id}

        pipeline = parse("bad").bind(fetch_user)
        result = run(pipeline)
        assert isinstance(result, Err)

    def test_mixed_pipeline_short_circuits_on_async_error(self):
        @TryAsync
        def parse(raw):
            return int(raw)

        @TryAsync
        async def fetch_user(id):
            raise ValueError(f"not found: {id}")

        pipeline = parse("99").bind(fetch_user)
        result = run(pipeline)
        assert isinstance(result, Err)

    def test_map_after_sync(self):
        @TryAsync
        def parse(raw):
            return int(raw)

        result = run(parse("10").map(lambda x: x * 2))
        assert result == Ok(20)

    def test_left_map_after_sync_error(self):
        @TryAsync
        def parse(raw):
            return int(raw)

        result = run(parse("bad").left_map(lambda e: TypeError("parse failed")))
        assert isinstance(result, Err)
        match result:
            case Err(e):
                assert isinstance(e, TypeError)
