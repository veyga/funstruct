from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses.monad import Monad
from funstruct.types.option import Nothing, Option, Some

_A = TypeVar("_A")
_B = TypeVar("_B")


class _OptionMonad(Monad, for_type=Option):
    def pure(self, value: _A) -> Option[_A]:
        return Some(value)

    def bind(self, fa: Option[_A], f: Callable[[_A], Option[_B]]) -> Option[_B]:
        match fa:
            case Some(value):
                return f(value)
            case Nothing():
                return fa
            case _:
                raise TypeError(f"Expected Option, got {type(fa)}")
