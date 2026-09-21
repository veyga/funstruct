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

    def hash(self, a) -> int:
        if a._hash_cache is None:
            h = 0
            for k, v in a._root.items_iter():
                h ^= hash((k, v))
            object.__setattr__(a, "_hash_cache", h)
        return a._hash_cache
