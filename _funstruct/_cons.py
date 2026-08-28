from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field
from typing import Generic, TypeVar

from funstruct.typeclasses._monad import Monad

A = TypeVar("A")
B = TypeVar("B")


class CList(Monad, Generic[A]):
    """A Lisp/ML/Scala style singly linked list (cons list).

    Provides an interface for working with a singly linked list, including methods for
    traversal, transformation, and manipulation of list elements.
    """

    @abstractmethod
    def append(self, other: CList) -> CList:
        """Append another list to the end of this list.

        Args:
            other: The list to append.

        Returns:
            A new list with the elements of `other` appended to this list.
        """
        ...

    @abstractmethod
    def fold_right(self, acc: B, f: Callable[[A, B], B]) -> B:
        """Fold the list from right to left.

        Args:
            acc: The initial accumulator value.
            f: A function to apply, taking an element and the current accumulator.

        Returns:
            The result of folding the list from right to left.
        """
        ...

    @abstractmethod
    def fold_left(self, acc: B, f: Callable[[B, A], B]) -> B:
        """Fold the list from left to right.

        Args:
            acc: The initial accumulator value.
            f: A function to apply, taking the current accumulator and an element.

        Returns:
            The result of folding the list from left to right.
        """
        ...

    @abstractmethod
    def drop(self, n: int) -> CList:
        """Drop the first `n` elements from the list.

        Args:
            n: The number of elements to drop.

        Returns:
            A new list with the first `n` elements removed.
        """
        ...

    @abstractmethod
    def drop_while(self, f: Callable[[A], bool]) -> CList:
        """Drop elements from the list as long as the predicate function `f` is true.

        Args:
            f: A predicate function to apply to each element.

        Returns:
            A new list with elements removed while `f` is true.
        """
        ...

    @abstractmethod
    def take(self, n: int) -> CList:
        """Take the first `n` elements from the list.

        Args:
            n: The number of elements to take.

        Returns:
            A new list containing the first `n` elements.
        """
        ...

    @abstractmethod
    def take_while(self, f: Callable[[A], bool]) -> CList:
        """Take elements from the list as long as the predicate function `f` is true.

        Args:
            f: A predicate function to apply to each element.

        Returns:
            A new list with elements taken while `f` is true.
        """
        ...

    @abstractmethod
    def split_at(self, i: int) -> tuple[CList, CList]:
        """Split the list into two lists at index `i`.

        Args:
            i: The index to split at.

        Returns:
            A tuple of two lists: the first containing elements up to `i`,
            and the second containing the rest.
        """
        ...

    @abstractmethod
    def insert_at(self, i: int, value: A) -> CList:
        """Insert an element at index `i`.

        Args:
            i: The index to split at.

        Returns:
            The new list
        """
        ...

    def partition(self, f: Callable[[A], bool]) -> tuple[CList, CList]:
        """Partition the list into two lists based on a predicate function.

        Args:
            f: A predicate function to apply to each element.

        Returns:
            A tuple of two lists: the first containing elements that satisfy `f`,
            and the second containing the rest.
        """
        accum = lambda a, x: (a << x[0], x[1]) if f(a) else (x[0], a << x[1])
        return self.fold_right((Nil(), Nil()), accum)

    def length(self) -> int:
        """Compute the length of the list.

        Returns:
            The number of elements in the list.
        """
        return self.fold_right(0, lambda _, acc: acc + 1)

    def prepend(self, new_head: A) -> CList:
        """Prepend an element to the list.

        Args:
            new_head: The element to prepend.

        Returns:
            A new list with `new_head` added to the beginning.
        """
        return Cons(new_head, self)

    def reversed(self) -> CList:
        """Reverse the order of the elements in the list.

        Returns:
            A new list with the elements in reversed order.
        """
        return self.fold_left(Nil(), lambda acc, h: Cons(h, acc))

    def map(self, f: Callable) -> CList:
        """Apply a function to each element of the list, producing a new list
        with the results.

        Args:
            f: A function to apply to each element.

        Returns:
            A new list with the results of applying `f` to each element.
        """
        return self.fold_right(Nil(), lambda a, acc: Cons(f(a), acc))

    def ap(self, other) -> CList:
        """Cartesian product — pair each element of self with each element of other."""
        return self.bind(lambda a: other.map(lambda b: (a, b)))

    def filter(self, f: Callable[[A], bool]) -> CList:
        """Filter the elements of the list based on a predicate function.

        Args:
            f: A predicate function to apply to each element.

        Returns:
            A new list containing only the elements that satisfy `f`.
        """
        return self.fold_right(
            Nil(), lambda a, acc: Cons(a, acc) if f(a) else acc
        )

    def flatten(self) -> CList:
        """Flatten a list of lists into a single list.

        Returns:
            A new list with all nested lists flattened into a single list.
        """
        return CList.flatten_(self)  # type: ignore

    def flat_map(self, f: Callable[[A], CList]) -> CList:
        """Apply a function to each element of the list,
        then flatten the resulting lists.

        Args:
            f: A function that returns a list for each element.

        Returns:
            A new list with the results of applying `f` to each element,
            flattened into a single list.
        """
        return self.map(f).flatten()

    def bind(self, f: Callable[[A], CList]) -> CList:
        """Apply a function to each element of the list and flatten the results.
        (alias for 'flat_map')

        Args:
            f: A function that returns a list for each element.

        Returns:
            A new list with the results of applying `f` to each element,
            flattened into a single list.
        """
        return self.flat_map(f)

    def sorted(self, cmp: Callable[[A, A], int]) -> CList:
        """Sort the list using a comparison function.

        Args:
            cmp: A comparison function to use for sorting.

        Returns:
            A new list with the elements sorted according to `cmp`.
        """

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
    def do(cls, gen_fn) -> CList:
        """Do-notation for CList. Collects all yielded results via flatMap."""

        def _collect():
            gen = gen_fn()
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

    @classmethod
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
        return Cons(xs[0], CList.new(*xs[1:])) if xs else Nil()

    @staticmethod
    def from_iterable(iterable: Iterable[A]) -> CList:
        """Create a new list from an iterable of elements.
        Ex:
        CList.from_iterable([1,2]) == Cons(1, Cons(2))

        Args:
            iterable: An iterable of elements.

        Returns:
            A new list containing the elements from the iterable.
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

    def __iter__(self) -> Iterator[A]:
        """Iterate over the elements of the list.

        Yields:
            Each element of the list.
        """
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

    def append(self, other: CList) -> CList:
        """Append another list to the empty list.

        Args:
            other: The list to append.

        Returns:
            The list `other`, since appending to an empty list results in `other`.
        """
        return other

    def fold_right(self, acc: B, f: Callable[[A, B], B]) -> B:
        """Fold the empty list from right to left.

        Args:
            acc: The initial accumulator value.
            f: A function to apply, taking an element and the current accumulator.

        Returns:
            The accumulator value, since folding an empty list results
            in the initial value.
        """
        return acc

    def fold_left(self, acc: B, f: Callable[[B, A], B]) -> B:
        """Fold the empty list from left to right.

        Args:
            acc: The initial accumulator value.
            f: A function to apply, taking the current accumulator and an element.

        Returns:
            The accumulator value, since folding an empty list results
            in the initial value.
        """
        return acc

    def drop(self, n: int) -> CList:
        """Drop the first `n` elements from the empty list.

        Args:
            n: The number of elements to drop.

        Returns:
            The empty list, since dropping elements from an empty list results
            in an empty list.
        """
        return self

    def drop_while(self, f: Callable[[A], bool]) -> CList:
        """Drop elements from the empty list as long as the predicate function
        `f` is true.

        Args:
            f: A predicate function to apply to each element.

        Returns:
            The empty list, since dropping elements from an empty list results
            in an empty list.
        """
        return self

    def take(self, n: int) -> CList:
        """Take the first `n` elements from the empty list.

        Args:
            n: The number of elements to take.

        Returns:
            The empty list, since taking elements from an empty list results
            in an empty list.
        """
        return self

    def take_while(self, f: Callable[[A], bool]) -> CList:
        """Take elements from the empty list as long as the predicate function
        `f` is true.

        Args:
            f: A predicate function to apply to each element.

        Returns:
            The empty list, since taking elements from an empty list results
            in an empty list.
        """
        return self

    def split_at(self, i: int) -> tuple[CList, CList]:
        """Split the empty list into two lists at index `i`.

        Args:
            i: The index to split at.

        Returns:
            A tuple of two empty lists.
        """
        return self, self

    def insert_at(self, i: int, value: A) -> CList:
        """Insert an element at index `i`.

        Args:
            i: The index to split at.

        Returns:
            The new list
        """
        return Cons(value, Nil())


@dataclass(frozen=True, eq=False)
class Cons(CList[A]):
    """Represents a non-empty list with a head element and a tail list."""

    head: A
    tail: CList[A] = field(default_factory=Nil)

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
        """Append another list to the end of this non-empty list.

        Args:
            other: The list to append.

        Returns:
            A new list with `other` appended to the end of this list.
        """
        return Cons(self.head, self.tail.append(other))

    def fold_right(self, acc: B, f: Callable[[A, B], B]) -> B:
        """Fold the non-empty list from right to left.

        Args:
            acc: The initial accumulator value.
            f: A function to apply, taking an element and the current accumulator.

        Returns:
            The result of folding the list from right to left.
        """
        return f(self.head, self.tail.fold_right(acc, f))

    def fold_left(self, acc: B, f: Callable[[B, A], B]) -> B:
        """Fold the non-empty list from left to right.

        Args:
            acc: The initial accumulator value.
            f: A function to apply, taking the current accumulator and an element.

        Returns:
            The result of folding the list from left to right.
        """
        return self.tail.fold_left(f(acc, self.head), f)

    def drop(self, n: int) -> CList:
        """Drop the first `n` elements from the non-empty list.

        Args:
            n: The number of elements to drop.

        Returns:
            A new list with the first `n` elements removed.
        """
        return self if n <= 0 else self.tail.drop(n - 1)

    def drop_while(self, f: Callable[[A], bool]) -> CList:
        """Drop elements from the non-empty list as long as the predicate function
        `f` is true.

        Args:
            f: A predicate function to apply to each element.

        Returns:
            A new list with elements removed while `f` is true.
        """
        return self if not f(self.head) else self.tail.drop_while(f)

    def take(self, n: int) -> CList:
        """Take the first `n` elements from the non-empty list.

        Args:
            n: The number of elements to take.

        Returns:
            A new list containing the first `n` elements.
        """
        return Cons(self.head) if n <= 1 else self.head << self.tail.take(n - 1)

    def take_while(self, f: Callable[[A], bool]) -> CList:
        """Take elements from the non-empty list as long as the predicate function
        `f` is true.

        Args:
            f: A predicate function to apply to each element.

        Returns:
            A new list with elements taken while `f` is true.
        """
        return self.head << self.tail.take_while(f) if f(self.head) else Nil()

    def split_at(self, i: int) -> tuple[CList, CList]:
        """Split the non-empty list into two lists at index `i`.

        Args:
            i: The index to split at.

        Returns:
            A tuple of two lists: the first containing elements up to `i`,
            and the second containing the rest.
        """
        return self.take(i), self.drop(i)

    def insert_at(self, i: int, value: A) -> CList:
        """Insert an element at index `i`.

        Args:
            i: The index to split at.

        Returns:
            The new list
        """
        if i <= 0:
            return Cons(value, self)
        return Cons(self.head, self.tail.insert_at(i - 1, value))


__all__ = [
    "CList",
    "Cons",
    "Nil",
]
