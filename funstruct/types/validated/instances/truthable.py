"""Truthable instance for Validated."""

from __future__ import annotations

from funstruct.typeclasses.truthable import Truthable
from funstruct.types.validated import Invalid, Valid, Validated


class _ValidatedTruthable(Truthable, for_type=Validated):
    def is_truthy(self, a) -> bool:
        match a:
            case Valid():
                return True
            case Invalid():
                return False
            case _:
                return True
