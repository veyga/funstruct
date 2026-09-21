"""Eq instance for Result."""

from __future__ import annotations

from funstruct.typeclasses.eq import Eq
from funstruct.types.result import Err, Ok, Result


class _ResultEq(Eq, for_type=Result):
    def eq(self, a, b) -> bool:
        match a, b:
            case Ok(va), Ok(vb):
                return va == vb
            case Err(ea), Err(eb):
                return ea == eb
            case _:
                return False
