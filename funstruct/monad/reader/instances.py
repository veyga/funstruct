"""Typeclass instances for Reader."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses.monad import Monad
from funstruct.monad.reader import Reader

_Ctx = TypeVar("_Ctx")
_A = TypeVar("_A")
_B = TypeVar("_B")


class _ReaderMonad(Monad, for_type=Reader):

    def pure(self, value: _A) -> Reader[_Ctx, _A]:
        return Reader(lambda _: value)

    def bind(
        self,
        fa: Reader[_Ctx, _A],
        f: Callable[[_A], Reader[_Ctx, _B]],
    ) -> Reader[_Ctx, _B]:
        return Reader(lambda ctx: f(fa._run(ctx)).run(ctx))
