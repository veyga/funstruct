"""A singly linked list.

Examples:
    >>> from funstruct.collections.cons import Cons, Nil
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
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field
from typing import Generic, TypeVar

from funstruct.typeclasses.mixins.data_type import DataType

A = TypeVar("A")
B = TypeVar("B")


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
    def fold_right(self, acc: B, f: Callable[[A, B], B]) -> B: ...

    @abstractmethod
    def fold_left(self, acc: B, f: Callable[[B, A], B]) -> B: ...

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
        return CList.flatten_(self)

    def bind(self, f: Callable[[A], CList]) -> CList:
        return self.fold_right(Nil(), lambda a, acc: f(a).append(acc))

    def traverse(self, f: Callable, pure_fn: Callable) -> object:
        return self.fold_right(
            pure_fn(Nil()),
            lambda a, acc: f(a).map2(acc, lambda b, bs: Cons(b, bs)),
        )

    def sequence(self, pure_fn: Callable) -> object:
        return self.traverse(lambda x: x, pure_fn)

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

    @classmethod
    def do(cls, gen_fn) -> Callable[..., CList]:
        """Do-notation for CList."""

        def _thunk(*args, **kwargs):
            def _collect():
                gen = gen_fn(*args, **kwargs)
                try:
                    first = next(gen)
                    result = first.bind(lambda v: _send(gen, v))
                    return result
                except StopIteration as e:
                    return Cons.pure(e.value)

            def _send(gen, value):
                try:
                    next_val = gen.send(value)
                    return next_val.bind(lambda v: _send(gen, v))
                except StopIteration as e:
                    return Cons.pure(e.value)

            return _collect()

        return _thunk

    @classmethod
    def pure(cls, value) -> CList:
        return Cons(value)

    @staticmethod
    def cons(a: A) -> CList:
        return Cons(a)

    @classmethod
    def empty(cls) -> CList:
        return Nil()

    def or_else(self, fb: CList) -> CList:
        return self.append(fb)

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

    def __add__(self, other: CList) -> CList:
        return self.append(other)

    def __len__(self) -> int:
        return self.fold_right(0, lambda _, acc: acc + 1)

    def to_list(self) -> list[A]:
        """>>> Cons(1, Cons(2, Cons(3, Nil()))).to_list()
        [1, 2, 3]
        >>> Nil().to_list()
        []
        """
        return list(self)

    def __iter__(self) -> Iterator[A]:
        current = self
        while isinstance(current, Cons):
            yield current.head
            current = current.tail

    def __eq__(self, other: object) -> bool:
        match other:
            case list():
                return list(self) == other
            case _:
                pass
        match self, other:
            case Cons(sh, st), Cons(oh, ot):
                return sh == oh and st == ot
            case Nil(), Nil():
                return True
            case _:
                return False


class Nil(CList):
    """Empty list (singleton)."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "Nil()"

    def __str__(self) -> str:
        return "Nil"

    def __bool__(self) -> bool:
        return False

    def append(self, other: CList) -> CList:
        return other

    def fold_right(self, acc: B, f: Callable[[A, B], B]) -> B:
        return acc

    def fold_left(self, acc: B, f: Callable[[B, A], B]) -> B:
        return acc

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


@dataclass(frozen=True, eq=False)
class Cons(CList[A]):
    """Non-empty list with head and tail."""

    head: A
    tail: CList[A] = field(default_factory=Nil)

    def __bool__(self) -> bool:
        return True

    def __repr__(self) -> str:
        return f"Cons({repr(self.head)}, {repr(self.tail)})"

    def __str__(self) -> str:
        def _fmt(elem) -> str:
            match elem:
                case CList():
                    return f"[{', '.join(_fmt(e) for e in elem)}]"
                case _:
                    return str(elem)

        return f"CList([{', '.join(_fmt(e) for e in self)}])"

    def append(self, other: CList) -> CList:
        return self.reversed().fold_left(other, lambda acc, h: Cons(h, acc))

    def fold_right(self, acc: B, f: Callable[[A, B], B]) -> B:
        return self.reversed().fold_left(acc, lambda a, b: f(b, a))

    def fold_left(self, acc: B, f: Callable[[B, A], B]) -> B:
        from funstruct.util.tailrec import tail_call, tco

        @tco
        def _go(current, result):
            match current:
                case Nil():
                    return result
                case Cons(h, t):
                    return tail_call(_go)(t, f(result, h))

        return _go(self, acc)

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


import funstruct.collections.cons.instances  # noqa: E402, F401

__all__ = [
    "CList",
    "Cons",
    "Nil",
]
