"""Typeclass instances for Writer variants."""

from __future__ import annotations

from funstruct.typeclasses._registry import register
from funstruct.typeclasses._typeclasses import Monad
from funstruct.monad.writer import (
    CListWriter,
    IntWriter,
    ListWriter,
    StrWriter,
    Writer,
)


class WriterMonad(Monad):
    def __init__(self, writer_cls):
        self._cls = writer_cls

    def pure(self, value):
        return self._cls.pure(value)

    def bind(self, fa, f):
        result = f(fa.value)
        return self._cls(
            result.value,
            self._cls._monoid.combine(fa.output, result.output),
        )


register(Monad, Writer, WriterMonad(Writer))
register(Monad, ListWriter, WriterMonad(ListWriter))
register(Monad, CListWriter, WriterMonad(CListWriter))
register(Monad, StrWriter, WriterMonad(StrWriter))
register(Monad, IntWriter, WriterMonad(IntWriter))

__all__ = ["WriterMonad"]
