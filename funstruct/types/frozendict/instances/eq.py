"""Eq instance for frozendict."""

from __future__ import annotations

from funstruct.typeclasses.eq import Eq
from funstruct.types.frozendict import frozendict


class _FrozendictEq(Eq, for_type=frozendict):
    def eq(self, a, b) -> bool:
        match b:
            case frozendict():
                if len(a) != len(b):
                    return False
                return all(b.get(k) == v for k, v in a.items())
            case dict():
                if len(a) != len(b):
                    return False
                return all(b.get(k) == v for k, v in a.items())
            case _:
                return False
