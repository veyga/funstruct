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
from abc import abstractmethod
from collections.abc import Awaitable, Callable, Coroutine
from dataclasses import dataclass
from functools import wraps
from typing import Any, Generic, ParamSpec, TypeVar, overload

from funstruct.monad.either import Either
from funstruct.monad.future import Future
from funstruct.typeclasses._monad import Monad
from funstruct.util.created_at import CapturesCreationSiteMixin
from funstruct.util.reawaitable import ReAwaitable

_A = TypeVar("_A")
_B = TypeVar("_B")


class Result(Monad, Generic[_A]):
    """Result[A] = Ok(value) | Err(exception).

    A monad for computations that can fail with an Exception.
    Standalone type — not an alias for Either. Uses domain-specific
    naming: Ok/Err instead of Right/Left, is_ok/is_err.
    """

    @classmethod
    def pure(cls, value: _A) -> Result[_A]:
        return Ok(value)

    @classmethod
    def from_exception(cls, error: Exception) -> Result:
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

    @abstractmethod
    def fold(self, on_err: Callable[[Exception], _B], on_ok: Callable[[_A], _B]) -> _B:
        """Eliminate the Result — apply on_err or on_ok."""
        ...

    @abstractmethod
    def bind(self, f: Callable[[_A], Result[_B]]) -> Result[_B]: ...

    @abstractmethod
    def left_map(self, f: Callable[[Exception], Exception]) -> Result[_A]:
        """Transform the error value. No-op on Ok."""
        ...

    @abstractmethod
    def handle_error_with(self, f: Callable[[Exception], Result[_A]]) -> Result[_A]:
        """Recover from error. No-op on Ok."""
        ...

    @abstractmethod
    def bimap(self, on_err: Callable, on_ok: Callable) -> Result:
        """Transform both sides."""
        ...

    @abstractmethod
    def get_or_else(self, default: _A) -> _A:
        """Extract the value, or return default if Err."""
        ...

    @abstractmethod
    def swap(self) -> Result:
        """Swap Ok and Err."""
        ...

    @property
    @abstractmethod
    def is_ok(self) -> bool: ...

    @property
    def is_err(self) -> bool:
        return not self.is_ok


@dataclass(frozen=True, eq=False)
class Ok(Result[_A]):
    """Success case of Result."""

    value: _A

    @classmethod
    def pure(cls, value: _A) -> Ok:
        return Ok(value)

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


_P = ParamSpec("_P")


class AsyncResult(Monad, Generic[_A]):
    """Async computation that produces Result[A] — essentially Future[Result[A]].

    AsyncResult is syntactic sugar for composing async operations that can
    fail. Instead of manually awaiting and pattern-matching at each step,
    chain with .bind(), .map(), .left_map() — one await at the boundary.

    Equivalent to Scala's ``EitherT[Future, Exception, A]`` but with a
    simpler API designed for Python's async/await.

    Create with:
        AsyncResult.pure(42)                     # Ok(42) wrapped in async
        AsyncResult.from_exception(ValueError()) # Err wrapped in async
        AsyncResult.from_result(Ok(42))          # lift sync Result
        @TryAsync decorator                      # catch exceptions

    Compose (lazy — nothing executes until awaited):
        result.map(f)                            # transform success value
        result.bind(f)                           # chain async operations
        result.left_map(f)                       # transform error value
        result.handle_error_with(f)              # recover from error

    Execute (one await at the boundary):
        value = await result                     # Result[A]
        value = await result.fold(on_err, on_ok) # _B
    """

    def __init__(self, coro: Awaitable[Result[_A]]) -> None:
        self._coro = ReAwaitable(coro) if not isinstance(coro, ReAwaitable) else coro

    def __await__(self):
        return self._awaitable().__await__()

    async def _awaitable(self) -> Result[_A]:
        return await self._coro

    @staticmethod
    async def _resolve(value: Any) -> Result:
        """Resolve a mixed return type into a Result."""
        if inspect.isawaitable(value):
            value = await value
        if isinstance(value, (Either, Result)):
            return value
        return Ok(value)

    def bind(self, f: Callable[[_A], Any]) -> AsyncResult:
        """Chain: f receives value. Short-circuits on Err."""

        async def _inner():
            result = await self._coro
            match result:
                case Ok(value):
                    return await AsyncResult._resolve(f(value))
                case _:
                    return result

        return AsyncResult(_inner())

    def left_map(self, f: Callable[[Exception], Exception]) -> AsyncResult[_A]:
        """Transform the error without recovering."""

        async def _inner():
            result = await self._coro
            match result:
                case Err(error):
                    return Err(f(error))
                case _:
                    return result

        return AsyncResult(_inner())

    def handle_error_with(self, f: Callable[[Exception], Any]) -> AsyncResult:
        """Recover from error: f receives error. Short-circuits on success."""

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
    def from_result(cls, result: Result) -> AsyncResult:
        """Lift a sync Result into AsyncResult."""

        async def _inner():
            return result

        return cls(_inner())

    @classmethod
    def from_either(cls, either: Either) -> AsyncResult:
        """Lift a sync Either into AsyncResult."""

        async def _inner():
            return either

        return cls(_inner())

    def fold(
        self, on_err: Callable[[Exception], _B], on_ok: Callable[[_A], _B]
    ) -> Future[_B]:
        """Eliminate — apply on_err or on_ok. Returns a Future to await.

        Usage: ``value = await async_result.fold(handle_err, handle_ok)``
        """

        async def _inner():
            result = await self._coro
            return result.fold(on_err=on_err, on_ok=on_ok)

        return Future(_inner())

    @classmethod
    def do(cls, gen_fn: Callable) -> Callable[..., AsyncResult]:
        """Do-notation for AsyncResult. Short-circuits on Err. Returns a callable.

        Every yielded value must be an AsyncResult. Use
        ``AsyncResult.from_result()`` to lift sync Result values.

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
    Compose with .bind(), .map(), .left_map() without awaiting.

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
