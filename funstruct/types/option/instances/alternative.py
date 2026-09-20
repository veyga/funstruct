from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses.alternative import Alternative
from funstruct.types.option import Nothing, Option, Some

_A = TypeVar("_A")
_B = TypeVar("_B")


class _OptionAlternative(Alternative, for_type=Option):
    def pure(self, value: _A) -> Option[_A]:
        return Some(value)

    def ap(
        self,
        ff: Option[Callable[[_A], _B]],
        fa: Option[_A],
    ) -> Option[_B]:
        match ff:
            case Some(f):
                match fa:
                    case Some(val):
                        return Some(f(val))
                    case _:
                        return Nothing()
            case _:
                return Nothing()

    def empty(self) -> Option:
        return Nothing()

    def or_else(self, fa: Option[_A], fb: Option[_A]) -> Option[_A]:
        match fa:
            case Some():
                return fa
            case Nothing():
                return fb
            case _:
                raise TypeError(f"Expected Option, got {type(fa)}")
