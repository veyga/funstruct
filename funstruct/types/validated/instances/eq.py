"""Eq instance for Validated."""

from __future__ import annotations

from funstruct.typeclasses.eq import Eq
from funstruct.types.validated import Invalid, Valid, Validated


class _ValidatedEq(Eq, for_type=Validated):
    def eq(self, a, b) -> bool:
        match a, b:
            case Valid(va), Valid(vb):
                return va == vb
            case Invalid(ea), Invalid(eb):
                return ea == eb
            case _:
                return False
