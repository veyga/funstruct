"""Typeclass instances for Writer variants."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from funstruct.monad.writer import (
    CListWriter,
    IntWriter,
    ListWriter,
    StrWriter,
    Writer,
)
from funstruct.typeclasses.monad import Monad
from funstruct.typeclasses.utils.registry import register

_A = TypeVar("_A")
_B = TypeVar("_B")
_W = TypeVar("_W")


class _WriterMonad(Monad):
    def __init__(self, writer_cls: type[Writer]) -> None:
        self._cls = writer_cls

    def pure(self, value: _A) -> Writer[_W, _A]:
        return self._cls.pure(value)

    def bind(
        self,
        fa: Writer[_W, _A],
        f: Callable[[_A], Writer[_W, _B]],
    ) -> Writer[_W, _B]:
        result = f(fa.value)
        return self._cls(
            result.value,
            self._cls._monoid.combine(fa.output, result.output),
        )


register(Monad, Writer, _WriterMonad(Writer))
register(Monad, ListWriter, _WriterMonad(ListWriter))
register(Monad, CListWriter, _WriterMonad(CListWriter))
register(Monad, StrWriter, _WriterMonad(StrWriter))
register(Monad, IntWriter, _WriterMonad(IntWriter))
