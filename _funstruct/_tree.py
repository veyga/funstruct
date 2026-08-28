"""Immutable binary tree — a Functor.

Tree[A] = Leaf(value) | Branch(value, left, right)

Every node holds a value. Leaf is terminal, Branch has children.
map applies a function to every value in the tree, preserving structure.
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

from _funstruct._cons import CList, Cons, Nil
from funstruct.typeclasses._functor import Functor

A = TypeVar("A")
B = TypeVar("B")


class Tree(Functor, Generic[A]):
    """Binary tree where every node holds a value.

    A Functor but NOT a Monad — map preserves structure,
    but there's no meaningful bind (no way to "flatten" a tree of trees
    without choosing a grafting strategy).
    """

    @abstractmethod
    def map(self, f: Callable[[A], B]) -> Tree[B]: ...

    @property
    @abstractmethod
    def size(self) -> int: ...

    @property
    @abstractmethod
    def depth(self) -> int: ...

    @abstractmethod
    def fold(self, on_leaf: Callable, on_branch: Callable): ...

    @abstractmethod
    def to_list(self) -> CList[A]: ...


@dataclass(frozen=True, eq=False)
class Leaf(Tree[A]):
    """Terminal node holding a single value."""

    value: A

    def map(self, f: Callable[[A], B]) -> Tree[B]:
        return Leaf(f(self.value))

    @property
    def size(self) -> int:
        return 1

    @property
    def depth(self) -> int:
        return 0

    def fold(self, on_leaf: Callable, on_branch: Callable):
        return on_leaf(self.value)

    def to_list(self) -> CList[A]:
        return Cons.pure(self.value)

    def __eq__(self, other: object) -> bool:
        match other:
            case Leaf(v):
                return self.value == v
            case _:
                return False

    def __repr__(self) -> str:
        return f"Leaf({repr(self.value)})"


@dataclass(frozen=True, eq=False)
class Branch(Tree[A]):
    """Internal node with a value and two children."""

    value: A
    left: Tree[A]
    right: Tree[A]

    def map(self, f: Callable[[A], B]) -> Tree[B]:
        return Branch(f(self.value), self.left.map(f), self.right.map(f))

    @property
    def size(self) -> int:
        return 1 + self.left.size + self.right.size

    @property
    def depth(self) -> int:
        return 1 + max(self.left.depth, self.right.depth)

    def fold(self, on_leaf: Callable, on_branch: Callable):
        return on_branch(
            self.value,
            self.left.fold(on_leaf, on_branch),
            self.right.fold(on_leaf, on_branch),
        )

    def to_list(self) -> CList[A]:
        return self.left.to_list() + Cons(self.value, self.right.to_list())

    def __eq__(self, other: object) -> bool:
        match other:
            case Branch(v, l, r):
                return self.value == v and self.left == l and self.right == r
            case _:
                return False

    def __repr__(self) -> str:
        return f"Branch({repr(self.value)}, {repr(self.left)}, {repr(self.right)})"


__all__ = ["Tree", "Leaf", "Branch"]
