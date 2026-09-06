"""Typeclass instances for Future."""

from __future__ import annotations

from funstruct.typeclasses._registry import register
from funstruct.typeclasses._typeclasses import Monad
from funstruct.monad.future import Future


class FutureMonad(Monad):

    def pure(self, value):
        return Future.pure(value)

    def bind(self, fa, f):
        return fa.bind(f)


register(Monad, Future, FutureMonad())

__all__ = ["FutureMonad"]
