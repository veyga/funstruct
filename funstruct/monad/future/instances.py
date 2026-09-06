"""Typeclass instances for Future."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from funstruct.monad.future import Future
from funstruct.typeclasses.monad import Monad

_A = TypeVar("_A")
_B = TypeVar("_B")


class _FutureMonad(Monad, for_type=Future):

    def pure(self, value: _A) -> Future[_A]:
        return Future.pure(value)

    def bind(self, fa: Future[_A], f: Callable[[_A], Future[_B]]) -> Future[_B]:
        return fa.bind(f)
