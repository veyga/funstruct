from __future__ import annotations

from funstruct.typeclasses.semigroup import Semigroup
from funstruct.types.frozendict import frozendict


class _FrozendictSemigroup(Semigroup, for_type=frozendict):
    def combine(self, a, b):
        return a.combine(b)
