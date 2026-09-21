"""Truthable instance for CList."""

from __future__ import annotations

from funstruct.typeclasses.truthable import Truthable
from funstruct.types.cons import CList, Cons, Nil


class _CListTruthable(Truthable, for_type=CList):
    def is_truthy(self, a) -> bool:
        match a:
            case Cons():
                return True
            case Nil():
                return False
            case _:
                return True
