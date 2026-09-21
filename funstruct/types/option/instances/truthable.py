"""Truthable instance for Option."""

from __future__ import annotations

from funstruct.typeclasses.truthable import Truthable
from funstruct.types.option import Nothing, Option, Some


class _OptionTruthable(Truthable, for_type=Option):
    def is_truthy(self, a) -> bool:
        match a:
            case Some():
                return True
            case Nothing():
                return False
            case _:
                return True
