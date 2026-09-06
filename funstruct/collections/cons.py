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
from typing import Generic, TypeVar, final

from funstruct.typeclasses._monad import Monad
from funstruct.typeclasses._traversable import Traversable

A = TypeVar("A")
B = TypeVar("B")


class CList(Monad, Traversable, Generic[A]):
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

    This is a persistent, immutable, singly-linked structure. Prepend is cheap;
    append is expensive. Best for recursive algorithms and stack-like access patterns.
    """

    @abstractmethod
    def append(fa: CList, other: CList) -> CList: ...

    @abstractmethod
    def fold_right(fa: CList, acc: B, f: Callable[[A, B], B]) -> B: ...

    @abstractmethod
    def fold_left(fa: CList, acc: B, f: Callable[[B, A], B]) -> B: ...

    @abstractmethod
    def drop(fa: CList, n: int) -> CList: ...

    @abstractmethod
    def drop_while(fa: CList, f: Callable[[A], bool]) -> CList: ...

    @abstractmethod
    def take(fa: CList, n: int) -> CList: ...

    @abstractmethod
    def take_while(fa: CList, f: Callable[[A], bool]) -> CList: ...

    @abstractmethod
    def split_at(fa: CList, i: int) -> tuple[CList, CList]: ...

    @abstractmethod
    def insert_at(fa: CList, i: int, value: A) -> CList: ...

    def partition(fa: CList, f: Callable[[A], bool]) -> tuple[CList, CList]:
        accum = lambda a, x: (a << x[0], x[1]) if f(a) else (x[0], a << x[1])
        return fa.fold_right((Nil(), Nil()), accum)

    def length(fa: CList) -> int:
        return fa.fold_right(0, lambda _, acc: acc + 1)

    def prepend(fa: CList, new_head: A) -> CList:
        return Cons(new_head, fa)

    def reversed(fa: CList) -> CList:
        return fa.fold_left(Nil(), lambda acc, h: Cons(h, acc))

    def filter(fa: CList, f: Callable[[A], bool]) -> CList:
        return fa.fold_right(Nil(), lambda a, acc: Cons(a, acc) if f(a) else acc)

    def flatten(fa: CList) -> CList:
        return CList.flatten_(fa)

    def bind(fa: CList, f: Callable[[A], CList]) -> CList:
        return fa.fold_right(Nil(), lambda a, acc: f(a).append(acc))

    def traverse(fa: CList, f: Callable, pure_fn: Callable) -> object:
        return fa.fold_right(
            pure_fn(Nil()),
            lambda a, acc: f(a).map2(acc, lambda b, bs: Cons(b, bs)),
        )

    def sorted(fa: CList, cmp: Callable[[A, A], int]) -> CList:
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

        length = len(fa)
        if length <= 1:
            return fa
        left, right = fa.split_at(length // 2)
        return merge(left.sorted(cmp), right.sorted(cmp))

    @staticmethod
    def flatten_(lst: CList[CList[A]]) -> CList:
        """Flatten a nested list of lists into a single list.

        Args:
            lst: A list of lists to be flattened.

        Returns:
            A new list with all nested lists flattened into a single list.
        """

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
        """Do-notation for CList. Collects all yielded results via flatMap. Returns a callable."""

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
    @final
    def pure(cls, value) -> CList:
        """Lift a value into a single-element list."""
        return Cons(value)

    @staticmethod
    def cons(a: A) -> CList:
        """Create a new list with a single element.

        Args:
            a: The element to add to the list.

        Returns:
            A new list containing the single element `a`.
        """
        return Cons(a)

    @staticmethod
    def empty() -> CList:
        """Create an empty list.

        Returns:
            An empty list.
        """
        return Nil()

    @staticmethod
    def new(*xs: A) -> CList:
        """Create a new list from the given elements.

        Args:
            *xs: The elements to add to the list.

        Returns:
            A new list containing the elements `xs`.
        """
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
        """Create a new list from an iterable of elements.

        >>> CList.from_iterable([1, 2, 3]).to_list()
        [1, 2, 3]
        >>> CList.from_iterable([]).to_list()
        []
        """
        return CList.new(*iterable)

    def __rlshift__(self, other: A) -> CList:
        """Prepend an element to the list using the `<<` operator.
        Ex:
        1 << Nil() == Cons(1)

        Args:
            other: The element to prepend.

        Returns:
            A new list with `other` added to the beginning.
        """
        return self.prepend(other)

    def __add__(self, other: CList) -> CList:
        """Concatenate two lists (Monoid append, not Applicative ap)."""
        return self.append(other)

    def __len__(self) -> int:
        """Compute the length of the list.

        Returns:
            The number of elements in the list.
        """
        return self.fold_right(0, lambda _, acc: acc + 1)

    def to_list(fa: CList) -> list[A]:
        """>>> Cons(1, Cons(2, Cons(3, Nil()))).to_list()
        [1, 2, 3]
        >>> Nil().to_list()
        []
        """
        return list(fa)

    def __iter__(self) -> Iterator[A]:
        current = self
        while isinstance(current, Cons):
            yield current.head
            current = current.tail

    def __eq__(self, other: object) -> bool:
        """Check if this list is equal to another list.

        Args:
            other: The list to compare with.

        Returns:
            True if the lists are equal, False otherwise.
        """
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
    """A singleton representing the empty list/end of a singly linked list."""

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

    def append(fa: Nil, other: CList) -> CList:
        return other

    def fold_right(fa: Nil, acc: B, f: Callable[[A, B], B]) -> B:
        return acc

    def fold_left(fa: Nil, acc: B, f: Callable[[B, A], B]) -> B:
        return acc

    def drop(fa: Nil, n: int) -> CList:
        return fa

    def drop_while(fa: Nil, f: Callable[[A], bool]) -> CList:
        return fa

    def take(fa: Nil, n: int) -> CList:
        return fa

    def take_while(fa: Nil, f: Callable[[A], bool]) -> CList:
        return fa

    def split_at(fa: Nil, i: int) -> tuple[CList, CList]:
        return fa, fa

    def insert_at(fa: Nil, i: int, value: A) -> CList:
        return Cons(value, Nil())


@dataclass(frozen=True, eq=False)
class Cons(CList[A]):
    """Represents a non-empty list with a head element and a tail list."""

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

    def append(fa: Cons, other: CList) -> CList:
        return fa.reversed().fold_left(other, lambda acc, h: Cons(h, acc))

    def fold_right(fa: Cons, acc: B, f: Callable[[A, B], B]) -> B:
        return fa.reversed().fold_left(acc, lambda a, b: f(b, a))

    def fold_left(fa: Cons, acc: B, f: Callable[[B, A], B]) -> B:
        from funstruct.util.tailrec import tail_call, tco

        @tco
        def _go(current, result):
            match current:
                case Nil():
                    return result
                case Cons(h, t):
                    return tail_call(_go)(t, f(result, h))

        return _go(fa, acc)

    def drop(fa: Cons, n: int) -> CList:
        return fa if n <= 0 else fa.tail.drop(n - 1)

    def drop_while(fa: Cons, f: Callable[[A], bool]) -> CList:
        return fa if not f(fa.head) else fa.tail.drop_while(f)

    def take(fa: Cons, n: int) -> CList:
        return Cons(fa.head) if n <= 1 else fa.head << fa.tail.take(n - 1)

    def take_while(fa: Cons, f: Callable[[A], bool]) -> CList:
        return fa.head << fa.tail.take_while(f) if f(fa.head) else Nil()

    def split_at(fa: Cons, i: int) -> tuple[CList, CList]:
        return fa.take(i), fa.drop(i)

    def insert_at(fa: Cons, i: int, value: A) -> CList:
        if i <= 0:
            return Cons(value, fa)
        return Cons(fa.head, fa.tail.insert_at(i - 1, value))


__all__ = [
    "CList",
    "Cons",
    "Nil",
]
