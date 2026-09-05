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

import inspect
from abc import abstractmethod
from collections.abc import Awaitable, Callable, Coroutine
from dataclasses import dataclass
from functools import wraps
from typing import Any, Generic, ParamSpec, TypeVar, overload

from funstruct.monad.either import Either, Left, Right
from funstruct.typeclasses._monad import Monad

_A = TypeVar("_A")
_B = TypeVar("_B")


class Result(Either[Exception, _A], Generic[_A]):
    """Result[A] = Ok(value) | Err(exception).

    Single type parameter — E is fixed to Exception.
    Same as Either[Exception, A] but with 1 param for cleaner annotations.
    """

    @classmethod
    def pure(cls, value: _A) -> Result[_A]:
        return Ok(value)

    @classmethod
    def from_exception(cls, error: Exception) -> Result:
        return Err(error)

    @abstractmethod
    def bind(self, f: Callable[[_A], Result[_B]]) -> Result[_B]: ...
    @abstractmethod
    def alt(self, f: Callable[[Exception], Exception]) -> Result[_A]: ...
    @abstractmethod
    def or_else(self, f: Callable[[Exception], Result[_A]]) -> Result[_A]: ...


@dataclass(frozen=True, eq=False)
class Ok(Right):
    """Success case of Result."""

    @classmethod
    def pure(cls, value: _A) -> Ok:
        return Ok(value)

    def bind(self, f: Callable[[_A], Result[_B]]) -> Result[_B]:
        return f(self.value)

    def alt(self, f: Callable[[Exception], Exception]) -> Result[_A]:
        return self

    def or_else(self, f: Callable[[Exception], Result[_A]]) -> Result[_A]:
        return self

    def __repr__(self) -> str:
        return f"Ok({repr(self.value)})"


@dataclass(frozen=True, eq=False)
class Err(Left):
    """Error case of Result."""

    def bind(self, f: Callable[[_A], Result[_B]]) -> Result[_B]:
        return self

    def alt(self, f: Callable[[Exception], Exception]) -> Result[_A]:
        return Err(f(self.error))

    def or_else(self, f: Callable[[Exception], Result[_A]]) -> Result[_A]:
        return f(self.error)

    def __repr__(self) -> str:
        return f"Err({repr(self.error)})"


_P = ParamSpec("_P")


class AsyncResult(Monad, Generic[_A]):
    """Lazy async computation that produces Result[A] (Ok or Err) when awaited.

    AsyncResult[User] = async computation → Ok(user) or Err(exception).
    Compose with .bind(), .map(), .alt(), .or_else() — no await needed.
    Execute once at the boundary with await.
    """

    __slots__ = ("_coro",)

    def __init__(self, coro: Awaitable[Result[_A]]) -> None:
        self._coro = coro

    def __del__(self):
        if hasattr(self._coro, "close"):
            getattr(self._coro, "close")()

    def __await__(self):
        return self._awaitable().__await__()

    async def _awaitable(self) -> Result[_A]:
        return await self._coro

    def bind(self, f: Callable[[_A], Any]) -> AsyncResult:
        """Chain: f receives value. Short-circuits on Err.

        Handles all return types from f:
        - AsyncResult[B] → awaited, produces Result
        - Either[E, B] / Result[B] → used directly
        - Awaitable[B] → awaited, plain value wrapped in Ok
        - Plain B → wrapped in Ok
        """

        async def _inner():
            result = await self._coro
            match result:
                case Right(value):
                    inner = f(value)
                    if inspect.isawaitable(inner):
                        inner = await inner
                    if isinstance(inner, Either):
                        return inner
                    return Ok(inner)
                case _:
                    return result

        return AsyncResult(_inner())

    def alt(self, f: Callable[[Exception], Exception]) -> AsyncResult[_A]:
        """Transform the error without recovering."""

        async def _inner():
            result = await self._coro
            match result:
                case Left(error):
                    return Err(f(error))
                case _:
                    return result

        return AsyncResult(_inner())

    def or_else(self, f: Callable[[Exception], Any]) -> AsyncResult:
        """Recover from error: f receives error. Short-circuits on success.

        Handles all return types from f:
        - AsyncResult[A] → awaited, produces Result
        - Either[E, A] / Result[A] → used directly
        - Awaitable[A] → awaited, plain value wrapped in Ok
        - Plain A → wrapped in Ok
        """

        async def _inner():
            result = await self._coro
            match result:
                case Left(error):
                    inner = f(error)
                    if inspect.isawaitable(inner):
                        inner = await inner
                    if isinstance(inner, Either):
                        return inner
                    return Ok(inner)
                case _:
                    return result

        return AsyncResult(_inner())

    @classmethod
    def pure(cls, value: _A) -> AsyncResult[_A]:
        """Lift a plain value into Ok."""

        async def _inner():
            return Ok(value)

        return cls(_inner())

    @classmethod
    def from_exception(cls, error: Exception) -> AsyncResult:
        """Lift an exception into Err."""

        async def _inner():
            return Err(error)

        return cls(_inner())

    @classmethod
    def from_either(cls, either: Either) -> AsyncResult:
        """Lift a sync Either/Result into AsyncResult."""

        async def _inner():
            return either

        return cls(_inner())

    @classmethod
    def do(cls, gen_fn: Callable) -> Callable[..., AsyncResult]:
        """Do-notation for AsyncResult. Short-circuits on Err. Returns a callable.

        Each yield can be an AsyncResult (awaited) or a sync Either
        (used directly). Right values are sent back, Left short-circuits.

        >>> @AsyncResult.do
        ... def pipeline():
        ...     x = yield AsyncResult.pure(1)
        ...     y = yield AsyncResult.pure(x + 10)
        ...     return x + y
        """

        def _thunk(*args, **kwargs):
            async def _run():
                gen = gen_fn(*args, **kwargs)
                try:
                    monadic_val = next(gen)
                    while True:
                        if isinstance(monadic_val, Either):
                            result = monadic_val
                        else:
                            result = await monadic_val
                        match result:
                            case Right(value):
                                monadic_val = gen.send(value)
                            case _:
                                return result
                except StopIteration as e:
                    return Ok(e.value)

            return cls(_run())

        return _thunk

    def __repr__(self) -> str:
        return f"AsyncResult({self._coro})"


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


@overload
def TryAsync(
    f: Callable[_P, Coroutine[Any, Any, _A]],
) -> Callable[_P, AsyncResult[_A]]: ...
@overload
def TryAsync(
    f: Callable[_P, _A],
) -> Callable[_P, AsyncResult[_A]]: ...
def TryAsync(
    f: Callable[_P, _A],
) -> Callable[_P, AsyncResult[_A]]:
    """Decorator: wraps a function so exceptions become Err.

    Accepts both sync and async functions. Returns AsyncResult[A] — a
    lazy computation. Await at the boundary to get Result[A] (Ok or Err).
    Compose with .bind(), .map(), .alt() without awaiting.

    Usage::

        @TryAsync
        async def fetch_user(id: int) -> User:
            resp = await httpx.get(f"/users/{id}")
            if resp.status_code != 200:
                raise NotFoundError(f"user {id}")
            return User(**resp.json())

        @TryAsync
        def parse_id(raw: str) -> int:
            return int(raw)

        # Build pipeline — no await needed:
        pipeline = (
            parse_id("42")
            .bind(fetch_user)
            .map(lambda u: u.email)
        )

        # Await once at the boundary:
        result = await pipeline  # Ok("alice@example.com") or Err(...)
    """

    @wraps(f)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> AsyncResult[_A]:
        async def _inner():
            try:
                result = f(*args, **kwargs)
                if inspect.isawaitable(result):
                    result = await result
                return Ok(result)
            except Exception as e:
                return Err(e)

        return AsyncResult(_inner())

    return wrapper


__all__ = [
    "Result",
    "Ok",
    "Err",
    "Try",
    "AsyncResult",
    "TryAsync",
]
