from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses.foldable import Foldable
from funstruct.types.frozendict import frozendict

K = TypeVar("K")
V = TypeVar("V")
B = TypeVar("B")


class _FrozendictFoldable(Foldable, for_type=frozendict):
    def fold_left(self, fa: frozendict[K, V], acc: B, f: Callable[[B, V], B]) -> B:
        return fa._fold_left_internal(acc, f)

    def fold_right(self, fa: frozendict[K, V], acc: B, f: Callable[[V, B], B]) -> B:
        return fa._fold_right_internal(acc, f)
