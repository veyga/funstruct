from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses.foldable import Foldable
from funstruct.types.ziplist import ZipList

_A = TypeVar("_A")
_B = TypeVar("_B")


class _ZipListFoldable(Foldable, for_type=ZipList):
    def fold_left(self, fa: ZipList[_A], acc: _B, f: Callable[[_B, _A], _B]) -> _B:
        for v in fa._values:
            acc = f(acc, v)
        return acc

    def fold_right(self, fa: ZipList[_A], acc: _B, f: Callable[[_A, _B], _B]) -> _B:
        for v in reversed(fa._values):
            acc = f(v, acc)
        return acc
