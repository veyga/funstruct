"""A singly linked list.

Examples:
    >>> from funstruct.types.cons import Cons, Nil
    >>> xs = Cons(1, Cons(2, Cons(3, Nil())))
    >>> xs.map(lambda x: x * 2)
    Cons(2, Cons(4, Cons(6, Nil())))
    >>> xs.filter(lambda x: x > 1)
    Cons(2, Cons(3, Nil()))
    >>> xs >> (lambda x: Cons(x, Cons(x, Nil())))
    Cons(1, Cons(1, Cons(2, Cons(2, Cons(3, Cons(3, Nil()))))))
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Generic, TypeVar, final

from funstruct.typeclasses.mixins.data_type import DataType

A = TypeVar("A")


class CList(DataType, Generic[A]):
    """A Lisp/ML/Scala style singly linked list (cons list).

    Performance characteristics:
        - prepend (<<):  O(1) — just creates a new head node
        - head/tail:     O(1) — direct field access
        - append (+):    O(n) — must traverse to the end
        - length:        O(n) — traverses entire list
        - drop(k):       O(k) — follows k tail pointers
        - take(k):       O(k) — copies k nodes
        - map/filter:    O(n) — traverses and rebuilds
        - bind:          O(n*m) — maps then flattens
        - reversed:      O(n) — builds new list via fold
        - index access:  O(n) — no random access (use Python list for that)

    This is a persistent, immutable, singly-linked structure.
    """

    @abstractmethod
    def append(self, other: CList) -> CList: ...

    @abstractmethod
    def drop(self, n: int) -> CList: ...

    @abstractmethod
    def drop_while(self, f: Callable[[A], bool]) -> CList: ...

    @abstractmethod
    def take(self, n: int) -> CList: ...

    @abstractmethod
    def take_while(self, f: Callable[[A], bool]) -> CList: ...

    @abstractmethod
    def split_at(self, i: int) -> tuple[CList, CList]: ...

    @abstractmethod
    def insert_at(self, i: int, value: A) -> CList: ...

    def partition(self, f: Callable[[A], bool]) -> tuple[CList, CList]:
        accum = lambda a, x: (a << x[0], x[1]) if f(a) else (x[0], a << x[1])
        return self.fold_right((Nil(), Nil()), accum)

    def length(self) -> int:
        return self.fold_right(0, lambda _, acc: acc + 1)

    def is_empty(self) -> bool:
        return not bool(self)

    def prepend(self, new_head: A) -> CList:
        return Cons(new_head, self)

    def reversed(self) -> CList:
        return self.fold_left(Nil(), lambda acc, h: Cons(h, acc))

    def filter(self, f: Callable[[A], bool]) -> CList:
        return self.fold_right(Nil(), lambda a, acc: Cons(a, acc) if f(a) else acc)

    def flatten(self) -> CList:
        return CList.flatten_(self)  # type: ignore[arg-type]  # A may be CList

    def sorted(self, cmp: Callable[[A, A], int]) -> CList:
        def merge(left: CList, right: CList) -> CList:
            match left, right:
                case Nil(), r:
                    return r
                case l, Nil():
                    return l
                case Cons(lh, lt), Cons(rh, rt):
                    if cmp(lh, rh) <= 0:
                        return lh << merge(lt, right)
                    return rh << merge(left, rt)
                case _:
                    return Nil()

        length = len(self)
        if length <= 1:
            return self
        left, right = self.split_at(length // 2)
        return merge(left.sorted(cmp), right.sorted(cmp))

    @staticmethod
    def flatten_(lst: CList[CList[A]]) -> CList:
        def concat(left, right):
            match left:
                case Nil():
                    return right
                case Cons(h, t):
                    return Cons(h, concat(t, right))
                case _:
                    return Nil()

        def flatten(lst: CList[CList[A]]) -> CList[A]:
            match lst:
                case Nil():
                    return Nil()
                case Cons(h, t):
                    match h:
                        case Cons(_, _):
                            return concat(flatten(h), flatten(t))
                        case _:
                            return Cons(h, flatten(t))
                case _:
                    return Nil()

        return flatten(lst)

    @staticmethod
    def cons(a: A) -> CList:
        return Cons(a)

    @staticmethod
    def new(*xs: A) -> CList:
        from funstruct.util.tailrec import tail_call, tco

        @tco
        def _go(items, idx, acc):
            if idx < 0:
                return acc
            return tail_call(_go)(items, idx - 1, Cons(items[idx], acc))

        return _go(xs, len(xs) - 1, Nil())

    @classmethod
    def fill(cls, n: int, value: A) -> CList:
        """Create a list of `n` copies of `value`.

        >>> CList.fill(3, 1).to_list()
        [1, 1, 1]
        >>> CList.fill(0, 'x')
        Nil()
        """
        from funstruct.util.tailrec import tail_call, tco

        @tco
        def _go(remaining, acc):
            if remaining <= 0:
                return acc
            return tail_call(_go)(remaining - 1, Cons(value, acc))

        return _go(n, Nil())

    @staticmethod
    def from_iterable(iterable: Iterable[A]) -> CList:
        """Create a new list from an iterable.

        >>> CList.from_iterable([1, 2, 3]).to_list()
        [1, 2, 3]
        >>> CList.from_iterable([]).to_list()
        []
        """
        return CList.new(*iterable)

    def __rlshift__(self, other: A) -> CList:
        return self.prepend(other)

    def to_list(self) -> list[A]:
        """>>> Cons(1, Cons(2, Cons(3, Nil()))).to_list()
        [1, 2, 3]
        >>> Nil().to_list()
        []
        """
        return list(self)



@final
class Nil(CList):
    """Empty list (singleton)."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def append(self, other: CList) -> CList:
        return other

    def drop(self, n: int) -> CList:
        return self

    def drop_while(self, f: Callable[[A], bool]) -> CList:
        return self

    def take(self, n: int) -> CList:
        return self

    def take_while(self, f: Callable[[A], bool]) -> CList:
        return self

    def split_at(self, i: int) -> tuple[CList, CList]:
        return self, self

    def insert_at(self, i: int, value: A) -> CList:
        return Cons(value, Nil())


@final
@dataclass(frozen=True, eq=False, repr=False)
class Cons(CList[A]):
    """Non-empty list with head and tail."""

    head: A
    tail: CList[A] = field(default_factory=Nil)

    def append(self, other: CList) -> CList:
        return self.reversed().fold_left(other, lambda acc, h: Cons(h, acc))

    def drop(self, n: int) -> CList:
        return self if n <= 0 else self.tail.drop(n - 1)

    def drop_while(self, f: Callable[[A], bool]) -> CList:
        return self if not f(self.head) else self.tail.drop_while(f)

    def take(self, n: int) -> CList:
        return Cons(self.head) if n <= 1 else self.head << self.tail.take(n - 1)

    def take_while(self, f: Callable[[A], bool]) -> CList:
        return self.head << self.tail.take_while(f) if f(self.head) else Nil()

    def split_at(self, i: int) -> tuple[CList, CList]:
        return self.take(i), self.drop(i)

    def insert_at(self, i: int, value: A) -> CList:
        if i <= 0:
            return Cons(value, self)
        return Cons(self.head, self.tail.insert_at(i - 1, value))


import funstruct.types.cons.instances  # noqa: E402, F401

__all__ = [
    "CList",
    "Cons",
    "Nil",
]
