"""Eq instance for Option."""

from __future__ import annotations

from funstruct.typeclasses.eq import Eq
from funstruct.types.option import Nothing, Option, Some


class _OptionEq(Eq, for_type=Option):
    def eq(self, a, b) -> bool:
        match a, b:
            case Some(va), Some(vb):
                return va == vb
            case Nothing(), Nothing():
                return True
            case _:
                return False

    def hash(self, a) -> int:
        match a:
            case Some(v):
                return hash(("Some", v))
            case Nothing():
                return hash(("Nothing",))
            case _:
                return hash(id(a))
