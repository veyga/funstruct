"""Result — Either specialized for error handling.

Result = Either, Ok = Right, Err = Left.
AsyncResult[A] = Future[Exception, A] as a single-param generic.
Try wraps sync functions, TryAsync wraps async functions.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Coroutine
from functools import wraps
from typing import Any, Generic, ParamSpec, TypeVar

from _funstruct._either import Either, Left, Right
from _funstruct._future import Future

_A = TypeVar("_A")
_P = ParamSpec("_P")


class Result(Either[Exception, _A], Generic[_A]):
    """Result[A] = Ok(value) | Err(exception).

    Single type parameter — E is fixed to Exception.
    Same as Either[Exception, A] but with 1 param for cleaner annotations.
    """

    pass


Ok = Right
Err = Left
_P = ParamSpec("_P")


class AsyncResult(Future[Exception, _A], Generic[_A]):
    """Future[Exception, A] — async computation that may fail.

    Single type parameter: AsyncResult[User] = Future[Exception, User].
    All Future methods inherited. Constructed via @TryAsync, .pure(), .from_error().
    """

    pass


def Try(
    f: Callable[_P, _A],
) -> Callable[_P, "Result[_A]"]:
    """Decorator: wraps a sync function so exceptions become Err.

    >>> @Try
    ... def divide(a, b):
    ...     return a / b
    >>> divide(10, 2)
    Right(5.0)
    >>> divide(10, 0)  # doctest: +ELLIPSIS
    Left(ZeroDivisionError(...))
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
) -> Callable[_P, "AsyncResult[_A]"]:
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
