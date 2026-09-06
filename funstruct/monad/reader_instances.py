"""Typeclass instances for Reader."""

from __future__ import annotations

from funstruct.typeclasses._registry import register
from funstruct.typeclasses._typeclasses import Monad
from funstruct.monad.reader import Reader


class ReaderMonad(Monad):

    def pure(self, value):
        return Reader(lambda _: value)

    def bind(self, fa, f):
        return Reader(lambda ctx: f(fa._run(ctx)).run(ctx))


register(Monad, Reader, ReaderMonad())

__all__ = ["ReaderMonad"]
