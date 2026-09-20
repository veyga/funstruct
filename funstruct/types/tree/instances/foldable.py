from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses.foldable import Foldable
from funstruct.types.tree import Branch, Leaf, Tree

_A = TypeVar("_A")
_B = TypeVar("_B")


class _TreeFoldable(Foldable, for_type=Tree):
    def fold_right(self, fa: Tree[_A], acc: _B, f: Callable[[_A, _B], _B]) -> _B:
        match fa:
            case Leaf(value):
                return f(value, acc)
            case Branch(value, left, right):
                acc = self.fold_right(right, acc, f)
                acc = f(value, acc)
                acc = self.fold_right(left, acc, f)
                return acc
            case _:
                raise TypeError(f"Expected Tree, got {type(fa)}")

    def fold_left(self, fa: Tree[_A], acc: _B, f: Callable[[_B, _A], _B]) -> _B:
        items: list[_A] = []
        self.fold_right(fa, None, lambda a, _: items.append(a))
        for item in items:
            acc = f(acc, item)
        return acc
