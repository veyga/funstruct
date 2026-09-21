"""Truthable instance for frozendict."""

from __future__ import annotations

from funstruct.typeclasses.truthable import Truthable
from funstruct.types.frozendict import frozendict


class _FrozendictTruthable(Truthable, for_type=frozendict):
    def is_truthy(self, a) -> bool:
        return a._size > 0
