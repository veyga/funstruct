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
from collections.abc import Awaitable, Callable, Coroutine
from dataclasses import dataclass
from functools import wraps
from typing import Any, Generic, ParamSpec, TypeVar, overload

from funstruct.monad.either import Either
from funstruct.monad.future import Future
from funstruct.typeclasses._dot_notation import DotNotation
from funstruct.util.created_at import CapturesCreationSiteMixin
from funstruct.util._reawaitable import ReAwaitable

_A = TypeVar("_A")
_B = TypeVar("_B")


class Result(DotNotation, Generic[_A]):
    """Result[A] = Ok(value) | Err(exception)."""

    @classmethod
    def pure(cls, value: _A) -> Result[_A]:
        return Ok(value)

    @classmethod
    def raise_error(cls, error: Exception) -> Result:
        return Err(error)

    @classmethod
    def do(cls, gen_fn: Callable) -> Callable[..., Result]:
        """Do-notation. Short-circuits on Err. Returns a callable."""

        def _thunk(*args, **kwargs):
            gen = gen_fn(*args, **kwargs)
            try:
                monadic_val = next(gen)
                while True:
                    match monadic_val:
                        case Err():
                            return monadic_val
                        case Ok(value):
                            monadic_val = gen.send(value)
            except StopIteration as e:
                return Ok(e.value)

        return _thunk

    @property
    def is_ok(self) -> bool:
        return False

    @property
    def is_err(self) -> bool:
        return not self.is_ok


@dataclass(frozen=True, eq=False)
class Ok(Result[_A]):
    """Success case of Result."""

    value: _A

    @property
    def is_ok(self) -> bool:
        return True

    def bind(self, f: Callable[[_A], Result[_B]]) -> Result[_B]:
        return f(self.value)

    def fold(self, on_err: Callable[[Exception], _B], on_ok: Callable[[_A], _B]) -> _B:
        return on_ok(self.value)

    def left_map(self, f: Callable[[Exception], Exception]) -> Result[_A]:
        return self

    def handle_error_with(self, f: Callable[[Exception], Result[_A]]) -> Result[_A]:
        return self

    def bimap(self, on_err: Callable, on_ok: Callable) -> Result:
        return Ok(on_ok(self.value))

    def get_or_else(self, default: _A) -> _A:
        return self.value

    def swap(self) -> Result:
        return Err(self.value)

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

    def bind(self, f: Callable[[_A], Result[_B]]) -> Result[_B]:
        return self

    def fold(self, on_err: Callable[[Exception], _B], on_ok: Callable[[_A], _B]) -> _B:
        return on_err(self.error)

    def left_map(self, f: Callable[[Exception], Exception]) -> Result[_A]:
        return Err(f(self.error))

    def handle_error_with(self, f: Callable[[Exception], Result[_A]]) -> Result[_A]:
        return f(self.error)

    def bimap(self, on_err: Callable, on_ok: Callable) -> Result:
        return Err(on_err(self.error))

    def get_or_else(self, default: _A) -> _A:
        return default

    def swap(self) -> Result:
        return Ok(self.error)

    def __eq__(self, other: object) -> bool:
        match other:
            case Err(err):
                return self.error == err
            case _:
                return False

    def __repr__(self) -> str:
        return f"Err({repr(self.error)})"


Result._type_constructor = Result
Ok._type_constructor = Result
Err._type_constructor = Result

_P = ParamSpec("_P")


class AsyncResult(DotNotation, Generic[_A]):
    """Async computation that produces Result[A] — essentially Future[Result[A]]."""

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
            return value
        return Ok(value)

    def bind(self, f: Callable[[_A], Any]) -> AsyncResult:
        async def _inner():
            result = await self._coro
            match result:
                case Ok(value):
                    return await AsyncResult._resolve(f(value))
                case _:
                    return result
        return AsyncResult(_inner())

    def left_map(self, f: Callable[[Exception], Exception]) -> AsyncResult[_A]:
        async def _inner():
            result = await self._coro
            match result:
                case Err(error):
                    return Err(f(error))
                case _:
                    return result
        return AsyncResult(_inner())

    def bimap(self, on_err: Callable[[Exception], Exception], on_ok: Callable) -> AsyncResult:
        async def _inner():
            result = await self._coro
            match result:
                case Ok(value):
                    return Ok(on_ok(value))
                case Err(error):
                    return Err(on_err(error))
                case _:
                    return result
        return AsyncResult(_inner())

    def handle_error_with(self, f: Callable[[Exception], Any]) -> AsyncResult:
        async def _inner():
            result = await self._coro
            match result:
                case Err(error):
                    return await AsyncResult._resolve(f(error))
                case _:
                    return result
        return AsyncResult(_inner())

    @classmethod
    def pure(cls, value: _A) -> AsyncResult[_A]:
        async def _inner():
            return Ok(value)
        return cls(_inner())

    @classmethod
    def raise_error(cls, error: Exception) -> AsyncResult:
        async def _inner():
            return Err(error)
        return cls(_inner())

    @classmethod
    def from_result(cls, result: Result) -> AsyncResult:
        async def _inner():
            return result
        return cls(_inner())

    @classmethod
    def from_either(cls, either: Either) -> AsyncResult:
        async def _inner():
            return either
        return cls(_inner())

    def fold(self, on_err: Callable[[Exception], _B], on_ok: Callable[[_A], _B]) -> Future[_B]:
        async def _inner():
            result = await self._coro
            return result.fold(on_err=on_err, on_ok=on_ok)
        return Future(_inner())

    @classmethod
    def do(cls, gen_fn: Callable) -> Callable[..., AsyncResult]:
        """Do-notation for AsyncResult."""
        def _thunk(*args, **kwargs):
            async def _run():
                gen = gen_fn(*args, **kwargs)
                try:
                    monadic_val = next(gen)
                    while True:
                        result = await monadic_val
                        match result:
                            case Ok(value):
                                monadic_val = gen.send(value)
                            case _:
                                return result
                except StopIteration as e:
                    return Ok(e.value)
            return cls(_run())
        return _thunk

    def __repr__(self) -> str:
        return f"AsyncResult({self._coro})"


AsyncResult._type_constructor = AsyncResult


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
def TryAsync(
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


import funstruct.monad.result_instances  # noqa: E402, F401

__all__ = [
    "Result",
    "Ok",
    "Err",
    "Try",
    "AsyncResult",
    "TryAsync",
]
