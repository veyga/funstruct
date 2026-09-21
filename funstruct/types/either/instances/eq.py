"""Eq instance for Either."""

from __future__ import annotations

from funstruct.typeclasses.eq import Eq
from funstruct.types.either import Either, Left, Right


class _EitherEq(Eq, for_type=Either):
    def eq(self, a, b) -> bool:
        match a, b:
            case Right(va), Right(vb):
                return va == vb
            case Left(ea), Left(eb):
                return ea == eb
            case _:
                return False
