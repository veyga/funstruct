"""Future — lazy async computation.

Future[A] wraps Awaitable[A]. A generic async monad — no error semantics built in.
For error handling, use AsyncResult[A] from funstruct.monad.result.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Generator
from typing import Generic, TypeVar

from funstruct.typeclasses.mixins.data_type import DataType
from funstruct.util._reawaitable import ReAwaitable

A = TypeVar("A")
B = TypeVar("B")


class Future(DataType, Generic[A]):
    """Lazy async computation that produces A when awaited."""

    def __init__(self, coro: Awaitable[A]) -> None:
        self._coro = ReAwaitable(coro) if not isinstance(coro, ReAwaitable) else coro

    def __del__(self):
        pass

    def __await__(self) -> Generator[None, None, A]:
        return self._awaitable().__await__()

    async def _awaitable(self) -> A:
        return await self._coro

    def bind(self, f: Callable[[A], Future[B]]) -> Future[B]:
        async def _inner():
            result = await self._coro
            return await f(result)

        return Future(_inner())

    @classmethod
    def do(cls, gen_fn: Callable) -> Callable[..., Future]:
        """Do-notation for Future.

        >>> @Future.do
        ... def pipeline():
        ...     x = yield Future.pure(1)
        ...     y = yield Future.pure(x + 10)
        ...     return x + y
        """

        def _thunk(*args, **kwargs):
            async def _run():
                gen = gen_fn(*args, **kwargs)
                try:
                    monadic_val = next(gen)
                    while True:
                        value = await monadic_val
                        monadic_val = gen.send(value)
                except StopIteration as e:
                    return e.value

            return cls(_run())

        return _thunk

    @classmethod
    def pure(cls, value: A) -> Future[A]:
        async def _inner():
            return value

        return cls(_inner())

    def __repr__(self) -> str:
        return f"Future({self._coro})"


import funstruct.monad.future.instances  # noqa: E402, F401

__all__ = [
    "Future",
]
