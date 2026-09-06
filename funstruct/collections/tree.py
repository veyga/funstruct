"""Immutable binary tree — a Functor.

Tree[A] = Leaf(value) | Branch(value, left, right)

Every node holds a value. map applies a function to all values,
preserving structure. Tree is a Functor but not a Monad.

Examples:
    >>> from funstruct.collections.tree import Tree, Leaf, Branch
    >>> from funstruct.collections.cons import Cons, Nil
    >>> t = Branch(1, Leaf(2), Leaf(3))
    >>> t.map(lambda x: x * 10)
    Branch(10, Leaf(20), Leaf(30))

    >>> t.size
    3
    >>> t.depth
    1

    >>> big = Branch(1, Branch(2, Leaf(3), Leaf(4)), Leaf(5))
    >>> big.map(str)
    Branch('1', Branch('2', Leaf('3'), Leaf('4')), Leaf('5'))
    >>> big.to_list()
    Cons(3, Cons(2, Cons(4, Cons(1, Cons(5, Nil())))))
    >>> big.depth
    2

    fold — reduce the tree:

    >>> t.fold(lambda v: v, lambda v, l, r: v + l + r)
    6
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

from funstruct.collections.cons import CList, Cons
from funstruct.typeclasses._dot_notation import DotNotation

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


class Tree(DotNotation, Generic[A]):
    """Binary tree where every node holds a value."""

    @abstractmethod
    def map(self, f: Callable[[A], B]) -> Tree[B]: ...

    @property
    @abstractmethod
    def size(self) -> int: ...

    @property
    @abstractmethod
    def depth(self) -> int: ...

    @abstractmethod
    def fold(self, on_leaf: Callable[[A], C], on_branch: Callable[[A, C, C], C]) -> C: ...

    @abstractmethod
    def to_list(self) -> CList[A]: ...

    @abstractmethod
    def fold_right(self, acc, f): ...

    def fold_left(self, acc, f):
        items = []
        self.fold_right(None, lambda a, _: items.append(a))
        for item in items:
            acc = f(acc, item)
        return acc

    def length(self) -> int:
        return self.fold_right(0, lambda _, acc: acc + 1)

    def is_empty(self) -> bool:
        return False

    @abstractmethod
    def traverse(self, f: Callable, pure_fn: Callable) -> object: ...

    def sequence(self, pure_fn: Callable) -> object:
        return self.traverse(lambda x: x, pure_fn)


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

    def fold(self, on_leaf: Callable[[A], C], on_branch: Callable[[A, C, C], C]) -> C:
        return on_leaf(self.value)

    def fold_right(self, acc, f):
        return f(self.value, acc)

    def traverse(self, f: Callable, pure_fn: Callable) -> object:
        return f(self.value).map(Leaf)

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

    def fold(self, on_leaf: Callable[[A], C], on_branch: Callable[[A, C, C], C]) -> C:
        return on_branch(
            self.value,
            self.left.fold(on_leaf, on_branch),
            self.right.fold(on_leaf, on_branch),
        )

    def fold_right(self, acc, f):
        acc = self.right.fold_right(acc, f)
        acc = f(self.value, acc)
        acc = self.left.fold_right(acc, f)
        return acc

    def traverse(self, f: Callable, pure_fn: Callable) -> object:
        fv = f(self.value)
        fl = self.left.traverse(f, pure_fn)
        fr = self.right.traverse(f, pure_fn)
        return (
            pure_fn(lambda v: lambda l: lambda r: Branch(v, l, r)).ap(fv).ap(fl).ap(fr)
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


Tree._type_constructor = Tree
Leaf._type_constructor = Tree
Branch._type_constructor = Tree

__all__ = ["Tree", "Leaf", "Branch"]
