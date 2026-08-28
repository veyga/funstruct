"""Future — lazy async computation that may fail.

Future[E, A] wraps an awaitable that produces Either[E, A].
Compose pipelines without await, execute once at the boundary.

Examples:
    >>> import asyncio
    >>> from funstruct.monad.future import Future, TryAsync
    >>> from funstruct.monad.either import Right, Left

    Build a pipeline — no await until the end:

    >>> async def fetch_user(id):
    ...     if id == 1:
    ...         return {"name": "alice"}
    ...     raise ValueError(f"not found: {id}")

    >>> pipeline = (
    ...     Future.from_coroutine(fetch_user(1))
    ...     .map(lambda u: u["name"].upper())
    ... )
    >>> asyncio.run(pipeline._awaitable())
    Right('ALICE')

    >>> failed = Future.from_coroutine(fetch_user(99))
    >>> asyncio.run(failed._awaitable())  # doctest: +ELLIPSIS
    Left(ValueError('not found: 99'))

    @TryAsync decorator:

    >>> @TryAsync
    ... async def safe_fetch(id):
    ...     if id == 1:
    ...         return {"name": "alice"}
    ...     raise ValueError(f"not found: {id}")
    >>> asyncio.run(safe_fetch(1)._awaitable())
    Right({'name': 'alice'})
    >>> asyncio.run(safe_fetch(99)._awaitable())  # doctest: +ELLIPSIS
    Left(ValueError('not found: 99'))
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Generator
from functools import wraps
from typing import Generic, TypeVar

from funstruct.monad.either import Either, Left, Right

E = TypeVar("E")
A = TypeVar("A")
B = TypeVar("B")


class Future(Generic[E, A]):
    """Lazy async computation that produces Either[E, A] when awaited.

    Build pipelines with .bind(), .map(), .or_else() — no await needed.
    Execute once at the boundary with await.
    """

    __slots__ = ("_coro",)

    def __init__(self, coro: Awaitable[Either[E, A]]) -> None:
        self._coro = coro

    def __del__(self):
        if hasattr(self._coro, "close"):
            self._coro.close()

    def __await__(self) -> Generator[None, None, Either[E, A]]:
        return self._awaitable().__await__()

    async def _awaitable(self) -> Either[E, A]:
        return await self._coro

    def map(self, f: Callable[[A], B]) -> Future[E, B]:
        """Transform the success value without executing."""

        async def _inner():
            result = await self._coro
            return result.map(f)

        return Future(_inner())

    def bind(self, f: Callable[[A], Future[E, B]]) -> Future[E, B]:
        """Chain: f receives the value, returns a new Future."""

        async def _inner():
            result = await self._coro
            match result:
                case Right(value):
                    return await f(value)
                case _:
                    return result

        return Future(_inner())

    def bind_either(self, f: Callable[[A], Either[E, B]]) -> Future[E, B]:
        """Chain with a sync function that returns Either."""

        async def _inner():
            result = await self._coro
            match result:
                case Right(value):
                    return f(value)
                case _:
                    return result

        return Future(_inner())

    def bind_awaitable(self, f: Callable[[A], Awaitable[B]]) -> Future[E, B]:
        """Chain with an async function that returns a plain value."""

        async def _inner():
            result = await self._coro
            match result:
                case Right(value):
                    return Right(await f(value))
                case _:
                    return result

        return Future(_inner())

    def alt(self, f: Callable[[E], E]) -> Future[E, A]:
        """Transform the error without recovering. Keeps it as Left."""

        async def _alt():
            result = await self._coro
            match result:
                case Left(error):
                    return Left(f(error))
                case _:
                    return result

        return Future(_alt())

    def or_else(self, f: Callable[[E], Future[E, A]]) -> Future[E, A]:
        """Recover from error: f receives the error, returns a new Future."""

        async def _inner():
            result = await self._coro
            match result:
                case Left(error):
                    return await f(error)
                case _:
                    return result

        return Future(_inner())

    def or_else_either(self, f: Callable[[E], Either[E, A]]) -> Future[E, A]:
        """Recover from error with a sync function returning Either."""

        async def _inner():
            result = await self._coro
            match result:
                case Left(error):
                    return f(error)
                case _:
                    return result

        return Future(_inner())

    def then(self, next_future: Future[E, B]) -> Future[E, B]:
        """Sequence: run self, discard value, run next."""
        return self.bind(lambda _: next_future)

    def ap(self, other: Future[E, B]) -> Future[E, tuple[A, B]]:
        """Applicative: run both, tuple the values."""
        return self.bind(lambda a: other.map(lambda b: (a, b)))

    @classmethod
    def pure(cls, value: A) -> Future[E, A]:
        """Lift a plain value into a successful Future."""

        async def _inner():
            return Right(value)

        return cls(_inner())

    @classmethod
    def from_error(cls, error: E) -> Future[E, A]:
        """Lift an error into a failed Future."""

        async def _inner():
            return Left(error)

        return cls(_inner())

    @classmethod
    def from_either(cls, either: Either[E, A]) -> Future[E, A]:
        """Lift a sync Either into a Future."""

        async def _inner():
            return either

        return cls(_inner())

    @classmethod
    def from_coroutine(cls, coro: Awaitable[A]) -> Future[Exception, A]:
        """Wrap a coroutine, catching exceptions into Left."""

        async def _inner():
            try:
                return Right(await coro)
            except Exception as e:
                return Left(e)

        return Future(_inner())

    def __repr__(self) -> str:
        return f"Future({self._coro})"


def TryAsync(f: Callable) -> Callable[..., Future[Exception, A]]:
    """Decorator: wraps an async function so exceptions become Left.

    The decorated function returns a Future that, when awaited,
    produces Either[Exception, A].
    """

    @wraps(f)
    def wrapper(*args, **kwargs) -> Future[Exception, A]:
        async def _inner():
            try:
                return Right(await f(*args, **kwargs))
            except Exception as e:
                return Left(e)

        return Future(_inner())

    return wrapper


__all__ = ["Future", "TryAsync"]
