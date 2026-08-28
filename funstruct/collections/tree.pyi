from collections.abc import Callable

from funstruct.collections.cons import CList

class Tree[A]:
    def map[B](self, f: Callable[[A], B]) -> Tree[B]: ...
    @property
    def size(self) -> int: ...
    @property
    def depth(self) -> int: ...
    def fold[C](
        self, on_leaf: Callable[[A], C], on_branch: Callable[[A, C, C], C]
    ) -> C: ...
    def to_list(self) -> CList[A]: ...

class Leaf[A](Tree[A]):
    value: A
    def __init__(self, value: A) -> None: ...

class Branch[A](Tree[A]):
    value: A
    left: Tree[A]
    right: Tree[A]
    def __init__(self, value: A, left: Tree[A], right: Tree[A]) -> None: ...
