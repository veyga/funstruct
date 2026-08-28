"""Result — Either with domain-oriented naming.

Result[E, A] = Ok(a) | Err(e). Same type as Either, clearer names.
AsyncResult[A] = Future[Exception, A]. Async counterpart of Result.

Decorators:
    @Try       : (args) -> Result[A]       = Either[Exception, A]
    @TryAsync  : (args) -> AsyncResult[A]  = Future[Exception, A]

Examples:
    >>> from funstruct.monad.result import Result, Ok, Err, Try
    >>> Ok(10).map(lambda x: x + 1)
    Ok(11)
    >>> Err("bad").map(lambda x: x + 1)
    Err('bad')
    >>> Ok(10).bind(lambda x: Ok(x * 2))
    Ok(20)

    or_else — recover from Err:

    >>> Err("bad").or_else(lambda e: Ok("default"))
    Ok('default')

    @Try decorator:

    >>> @Try
    ... def safe_div(a, b):
    ...     return a / b
    >>> safe_div(10, 2)
    Ok(5.0)
    >>> safe_div(10, 0)  # doctest: +ELLIPSIS
    Err(ZeroDivisionError(...))
"""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any, Generic, ParamSpec, TypeVar

from dataclasses import dataclass

from funstruct.monad.either import Either, Left, Right
from funstruct.monad.future import Future

_A = TypeVar("_A")


class Result(Either[Exception, _A], Generic[_A]):
    """Result[A] = Ok(value) | Err(exception).

    Single type parameter — E is fixed to Exception.
    Same as Either[Exception, A] but with 1 param for cleaner annotations.
    """

    pass


@dataclass(frozen=True, eq=False)
class Ok(Right):
    """Success case of Result."""

    def map(self, f: Callable) -> Either:
        return Ok(f(self.value))

    def bind(self, f: Callable) -> Either:
        return f(self.value)

    def __repr__(self) -> str:
        return f"Ok({repr(self.value)})"


@dataclass(frozen=True, eq=False)
class Err(Left):
    """Error case of Result."""

    def alt(self, f: Callable) -> Either:
        return Err(f(self.error))

    def or_else(self, f: Callable) -> Either:
        return f(self.error)

    def __repr__(self) -> str:
        return f"Err({repr(self.error)})"


_P = ParamSpec("_P")


class AsyncResult(Future[Exception, _A], Generic[_A]):
    """Future[Exception, A] — async computation that may fail.

    Single type parameter: AsyncResult[User] = Future[Exception, User].
    All Future methods inherited. Constructed via @TryAsync, .pure(), .from_error().
    """

    pass


def Try(
    f: Callable[_P, _A],
) -> Callable[_P, Result[_A]]:
    """Decorator: wraps a sync function so exceptions become Err.

    Successful calls return Ok(value), exceptions return Err(exception).
    Pattern match the result with Ok(v) / Err(e).
    """

    @wraps(f)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> Result[_A]:
        try:
            return Ok(f(*args, **kwargs))
        except Exception as e:
            return Err(e)

    return wrapper


def TryAsync(
    f: Callable[_P, Coroutine[Any, Any, _A]],
) -> Callable[_P, AsyncResult[_A]]:
    """Decorator: wraps an async function so exceptions become Err.

    Returns AsyncResult[A] — a lazy computation. Await at the boundary
    to get Result[A] (Ok or Err). Compose with .bind(), .map(), .alt()
    without awaiting.

    Usage::

        @TryAsync
        async def fetch_user(id: int) -> User:
            resp = await httpx.get(f"/users/{id}")
            if resp.status_code != 200:
                raise NotFoundError(f"user {id}")
            return User(**resp.json())

        # Build pipeline — no await needed:
        pipeline = (
            fetch_user(42)
            .map(lambda u: u.email)
            .alt(lambda e: FallbackError(str(e)))
        )

        # Await once at the boundary:
        result = await pipeline  # Ok("alice@example.com") or Err(...)
    """

    @wraps(f)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> AsyncResult[_A]:
        async def _inner():
            try:
                return Ok(await f(*args, **kwargs))
            except Exception as e:
                return Err(e)

        return AsyncResult(_inner())

    return wrapper


__all__ = ["Result", "Ok", "Err", "Try", "AsyncResult", "TryAsync"]
