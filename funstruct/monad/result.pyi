from collections.abc import Callable, Coroutine
from typing import Any

from funstruct.monad.either import Either, Left, Right
from funstruct.monad.future import Future

type Result[A] = Either[Exception, A]
"""Result[A] = Ok(value) | Err(exception).

A specialization of Either where the error is always Exception.
Use Ok/Err for construction and pattern matching.
"""

Ok = Right
"""Ok(value) — success case of Result. Same as Right."""

Err = Left
"""Err(exception) — failure case of Result. Same as Left."""

class AsyncResult[A](Future[Exception, A]):
    """Async computation that produces Result[A] when awaited.

    AsyncResult[User] = an async operation that yields Ok(user) or Err(exception).
    Constructed via @TryAsync, .pure(), .from_error(), .from_either().
    """

    ...

def Try[**P, A](f: Callable[P, A]) -> Callable[P, Result[A]]:
    """Decorator: wraps a sync function so exceptions become Err.

    @Try
    def parse(s: str) -> int: return int(s)

    parse("42")   → Ok(42)
    parse("abc")  → Err(ValueError(...))
    """
    ...

def TryAsync[**P, A](
    f: Callable[P, Coroutine[Any, Any, A]],
) -> Callable[P, AsyncResult[A]]:
    """Decorator: wraps an async function so exceptions become Err.

    @TryAsync
    async def fetch(url: str) -> Response: ...

    await fetch(url)  → Ok(response) or Err(exception)
    """
    ...
