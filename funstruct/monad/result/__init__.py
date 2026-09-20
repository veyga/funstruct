"""Result — a monad for computations that can fail with an Exception.

Result[A] = Ok(value) | Err(exception).
AsyncResult[A] = async computation producing Result[A].

Decorators:
    @Try       : (args) -> Result[A]
    @TryAsync  : (args) -> AsyncResult[A]

Examples:
    >>> from funstruct.monad.result import Result, Ok, Err, Try
    >>> Ok(10).map(lambda x: x + 1)
    Ok(11)
    >>> Err("bad").map(lambda x: x + 1)
    Err('bad')
    >>> Ok(10).bind(lambda x: Ok(x * 2))
    Ok(20)

    handle_error_with — recover from Err:

    >>> Err("bad").handle_error_with(lambda e: Ok("default"))
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
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable, Coroutine
from dataclasses import dataclass
from functools import wraps
from typing import Any, Generic, ParamSpec, TypeVar, overload

from funstruct.monad.either import Either
from funstruct.monad.future import Future
from funstruct.typeclasses.mixins.data_type import DataType
from funstruct.util._reawaitable import ReAwaitable
from funstruct.util.created_at import CapturesCreationSiteMixin

_A = TypeVar("_A")
_B = TypeVar("_B")


class Result(DataType, ABC, Generic[_A]):
    """Result[A] = Ok(value) | Err(exception)."""

    @property
    @abstractmethod
    def is_ok(self) -> bool: ...

    @property
    def is_err(self) -> bool:
        return not self.is_ok

    def get_or_else(self, default: _A) -> _A:
        match self:
            case Ok(v):
                return v
            case _:
                return default

    def fold(self, on_err: Callable[[Exception], _B], on_ok: Callable[[_A], _B]) -> _B:
        match self:
            case Ok(v):
                return on_ok(v)
            case Err(e):
                return on_err(e)
            case _:
                raise TypeError(f"Expected Result, got {type(self)}")

    def swap(self) -> Result:
        match self:
            case Ok(v):
                return Err(v)  # type: ignore[arg-type]
            case Err(e):
                return Ok(e)
            case _:
                raise TypeError(f"Expected Result, got {type(self)}")


@dataclass(frozen=True, eq=False)
class Ok(Result[_A]):
    """Success case of Result."""

    value: _A

    @property
    def is_ok(self) -> bool:
        return True

    def __eq__(self, other: object) -> bool:
        match other:
            case Ok(val):
                return self.value == val
            case _:
                return False

    def __repr__(self) -> str:
        return f"Ok({repr(self.value)})"


@dataclass(frozen=True, eq=False)
class Err(CapturesCreationSiteMixin, Result[_A]):
    """Error case of Result. Captures creation site automatically."""

    error: Exception

    @property
    def is_ok(self) -> bool:
        return False

    def __eq__(self, other: object) -> bool:
        match other:
            case Err(err):
                return self.error == err
            case _:
                return False

    def __repr__(self) -> str:
        return f"Err({repr(self.error)})"


_P = ParamSpec("_P")


class AsyncResult(DataType, Generic[_A]):
    """Async computation that produces Result[A] — essentially Future[Result[A]].

    Create with:
        AsyncResult.pure(42)                     # Ok(42) wrapped in async
        AsyncResult.raise_error(ValueError())    # Err wrapped in async
        @TryAsync decorator                      # catch exceptions

    Compose (lazy — nothing executes until awaited):
        result.map(f)                            # transform success value
        result.bind(f)                           # chain async operations
        result.left_map(f)                       # transform error value
        result.handle_error_with(f)              # recover from error

    Execute (one await at the boundary):
        value = await result                     # Result[A]

    Important: @do uses generators (yield), NOT async/await.
    You cannot decorate an async def with @do.
    """

    def __init__(self, coro: Awaitable[Result[_A]]) -> None:
        self._coro = ReAwaitable(coro) if not isinstance(coro, ReAwaitable) else coro

    def __await__(self):
        return self._awaitable().__await__()

    async def _awaitable(self) -> Result[_A]:
        return await self._coro

    @staticmethod
    async def _resolve(value: Any) -> Result:
        if inspect.isawaitable(value):
            value = await value
        if isinstance(value, (Either, Result)):
            return value  # type: ignore[return-value]
        return Ok(value)

    def fold(
        self, on_err: Callable[[Exception], _B], on_ok: Callable[[_A], _B]
    ) -> Future[_B]:
        async def _inner():
            result = await self._coro
            return result.fold(on_err=on_err, on_ok=on_ok)

        return Future(_inner())

    def __repr__(self) -> str:
        return f"AsyncResult({self._coro})"


def Try(
    f: Callable[_P, _A],
) -> Callable[_P, Result[_A]]:
    """Decorator: wraps a sync function so exceptions become Err."""

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
def TryAsync(  # type: ignore[misc]  # overload TypeVar limitation
    f: Callable[_P, _A],
) -> Callable[_P, AsyncResult[_A]]:
    """Decorator: wraps a function so exceptions become Err."""

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


import funstruct.monad.result.instances  # noqa: E402, F401

__all__ = [
    "Result",
    "Ok",
    "Err",
    "Try",
    "AsyncResult",
    "TryAsync",
]
