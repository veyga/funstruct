from abc import abstractmethod, ABC
from dataclasses import dataclass, field
from typing import Callable, Iterable, Tuple
from typing import TypeVar


A = TypeVar("A")

type _CList = "CList[A]"


class CList[A](ABC):
    """
    A Lisp/ML/Scala style singly linked list (cons list).

    Provides an interface for working with a singly linked list, including methods for
    traversal, transformation, and manipulation of list elements.
    """

    @abstractmethod
    def append(self, other: _CList) -> _CList:
        """
        Append another list to the end of this list.

        Args:
            other: The list to append.

        Returns:
            A new list with the elements of `other` appended to this list.
        """
        ...

    @abstractmethod
    def fold_right[B](self, acc: B, f: Callable[[A, B], B]) -> B:
        """
        Fold the list from right to left.

        Args:
            acc: The initial accumulator value.
            f: A function to apply, taking an element and the current accumulator.

        Returns:
            The result of folding the list from right to left.
        """
        ...

    @abstractmethod
    def fold_left[B](self, acc: B, f: Callable[[B, A], B]) -> B:
        """
        Fold the list from left to right.

        Args:
            acc: The initial accumulator value.
            f: A function to apply, taking the current accumulator and an element.

        Returns:
            The result of folding the list from left to right.
        """
        ...

    @abstractmethod
    def drop(self, n: int) -> _CList:
        """
        Drop the first `n` elements from the list.

        Args:
            n: The number of elements to drop.

        Returns:
            A new list with the first `n` elements removed.
        """
        ...

    @abstractmethod
    def drop_while(self, f: Callable[[A], bool]) -> _CList:
        """
        Drop elements from the list as long as the predicate function `f` is true.

        Args:
            f: A predicate function to apply to each element.

        Returns:
            A new list with elements removed while `f` is true.
        """
        ...

    @abstractmethod
    def take(self, n: int) -> _CList:
        """
        Take the first `n` elements from the list.

        Args:
            n: The number of elements to take.

        Returns:
            A new list containing the first `n` elements.
        """
        ...

    @abstractmethod
    def take_while(self, f: Callable[[A], bool]) -> _CList:
        """
        Take elements from the list as long as the predicate function `f` is true.

        Args:
            f: A predicate function to apply to each element.

        Returns:
            A new list with elements taken while `f` is true.
        """
        ...

    @abstractmethod
    def split_at(self, i: int) -> Tuple[_CList, _CList]:
        """
        Split the list into two lists at index `i`.

        Args:
            i: The index to split at.

        Returns:
            A tuple of two lists: the first containing elements up to `i`,
            and the second containing the rest.
        """
        ...

    def partition(self, f: Callable[[A], bool]) -> Tuple[_CList, _CList]:
        """
        Partition the list into two lists based on a predicate function.

        Args:
            f: A predicate function to apply to each element.

        Returns:
            A tuple of two lists: the first containing elements that satisfy `f`,
            and the second containing the rest.
        """
        accum = lambda a, x: (a << x[0], x[1]) if f(a) else (x[0], a << x[1])
        return self.fold_right((Nil(), Nil()), accum)

    def length(self) -> int:
        """
        Compute the length of the list.

        Returns:
            The number of elements in the list.
        """
        return self.fold_right(0, lambda _, acc: acc + 1)

    def prepend(self, new_head: A) -> _CList:
        """
        Prepend an element to the list.

        Args:
            new_head: The element to prepend.

        Returns:
            A new list with `new_head` added to the beginning.
        """
        return Cons(new_head, self)

    def reversed(self) -> _CList:
        """
        Reverse the order of the elements in the list.

        Returns:
            A new list with the elements in reversed order.
        """
        return self.fold_left(Nil(), lambda acc, h: Cons(h, acc))

    def map[B](self, f: Callable[[A], B]) -> "CList[B]":
        """
        Apply a function to each element of the list, producing a new list
        with the results.

        Args:
            f: A function to apply to each element.

        Returns:
            A new list with the results of applying `f` to each element.
        """
        return self.fold_right(Nil(), lambda a, acc: Cons(f(a), acc))

    def filter(self, f: Callable[[A], bool]) -> _CList:
        """
        Filter the elements of the list based on a predicate function.

        Args:
            f: A predicate function to apply to each element.

        Returns:
            A new list containing only the elements that satisfy `f`.
        """
        return self.fold_right(Nil(), lambda a, acc: Cons(a, acc) if f(a) else acc)

    def flatten(self) -> _CList:
        """
        Flatten a list of lists into a single list.

        Returns:
            A new list with all nested lists flattened into a single list.
        """
        return CList.flatten_(self)

    def flat_map[B](self, f: Callable[[A], "CList[B]"]) -> "CList[B]":
        """
        Apply a function to each element of the list,
        then flatten the resulting lists.

        Args:
            f: A function that returns a list for each element.

        Returns:
            A new list with the results of applying `f` to each element,
            flattened into a single list.
        """
        return self.map(f).flatten()

    def bind[B](self, f: Callable[[A], "CList[B]"]) -> "CList[B]":
        """
        Apply a function to each element of the list and flatten the results.
        (alias for 'flat_map')

        Args:
            f: A function that returns a list for each element.

        Returns:
            A new list with the results of applying `f` to each element,
            flattened into a single list.
        """
        return self.flat_map(f)

    def sorted(self, cmp: Callable[[A, A], int]) -> _CList:
        """
        Sort the list using a comparison function.

        Args:
            cmp: A comparison function to use for sorting.

        Returns:
            A new list with the elements sorted according to `cmp`.
        """

        def merge(left: _CList, right: _CList) -> _CList:
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
    def flatten_(lst: "CList[CList[A]]") -> _CList:
        """
        Flatten a nested list of lists into a single list.

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

        def flatten(lst: "CList[CList[A]]") -> "CList[A]":
            match lst:
                case Nil():
                    return Nil()
                case Cons(h, t):
                    match h:
                        case Cons(_, _):
                            return concat(flatten(h), flatten(t))
                        case _:
                            return Cons(h, flatten(t))

        return flatten(lst)

    @staticmethod
    def cons(a: A) -> _CList:
        """
        Create a new list with a single element.

        Args:
            a: The element to add to the list.

        Returns:
            A new list containing the single element `a`.
        """
        return Cons(a)

    @staticmethod
    def empty() -> _CList:
        """
        Create an empty list.

        Returns:
            An empty list.
        """
        return Nil()

    @staticmethod
    def new(*xs: A) -> _CList:
        """
        Create a new list from the given elements.

        Args:
            *xs: The elements to add to the list.

        Returns:
            A new list containing the elements `xs`.
        """
        return Cons(xs[0], CList.new(*xs[1:])) if xs else Nil()

    @staticmethod
    def from_iterable(iterable: Iterable[A]) -> _CList:
        """
        Create a new list from an iterable of elements.
        Ex:
        CList.from_iterable([1,2]) == Cons(1, Cons(2))

        Args:
            iterable: An iterable of elements.

        Returns:
            A new list containing the elements from the iterable.
        """
        return CList.new(*iterable)

    def __rlshift__(self, other) -> _CList:
        """
        Prepend an element to the list using the `<<` operator.
        Ex:
        1 << Nil() == Cons(1)

        Args:
            other: The element to prepend.

        Returns:
            A new list with `other` added to the beginning.
        """
        return self.prepend(other)

    def __add__(self, other) -> _CList:
        """
        Append another list to the end of this list using the `+` operator.
        (alias for 'append')

        Args:
            other: The list to append.

        Returns:
            A new list with the elements of `other` appended to this list.
        """
        return self.append(other)

    def __len__(self) -> int:
        """
        Compute the length of the list.

        Returns:
            The number of elements in the list.
        """
        return self.fold_right(0, lambda _, acc: acc + 1)

    def __iter__(self):
        """
        Iterate over the elements of the list.

        Yields:
            Each element of the list.
        """
        current = self
        while isinstance(current, Cons):
            yield current.head
            current = current.tail

    def __eq__(self, other) -> bool:
        """
        Check if this list is equal to another list.

        Args:
            other: The list to compare with.

        Returns:
            True if the lists are equal, False otherwise.
        """
        match self, other:
            case Cons(sh, st), Cons(oh, ot):
                return sh == oh and st == ot
            case Nil(), Nil():
                return True
            case _:
                return False


class Nil(CList):
    """
    A singleton representing the empty list/end of a singly linked list.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Nil, cls).__new__(cls)
        return cls._instance

    def __repr__(self):
        """
        Return a string representation of the empty list.

        Returns:
            A string representing the empty list.
        """
        return "Nil()"

    def append(self, other: _CList) -> _CList:
        """
        Append another list to the empty list.

        Args:
            other: The list to append.

        Returns:
            The list `other`, since appending to an empty list results in `other`.
        """
        return other

    def fold_right[A, B](self, acc: B, f: Callable[[A, B], B]) -> B:
        """
        Fold the empty list from right to left.

        Args:
            acc: The initial accumulator value.
            f: A function to apply, taking an element and the current accumulator.

        Returns:
            The accumulator value, since folding an empty list results
            in the initial value.
        """
        return acc

    def fold_left[A, B](self, acc: B, f: Callable[[B, A], B]) -> B:
        """
        Fold the empty list from left to right.

        Args:
            acc: The initial accumulator value.
            f: A function to apply, taking the current accumulator and an element.

        Returns:
            The accumulator value, since folding an empty list results
            in the initial value.
        """
        return acc

    def drop(self, n: int) -> _CList:
        """
        Drop the first `n` elements from the empty list.

        Args:
            n: The number of elements to drop.

        Returns:
            The empty list, since dropping elements from an empty list results
            in an empty list.
        """
        return self

    def drop_while(self, f: Callable[[A], bool]) -> _CList:
        """
        Drop elements from the empty list as long as the predicate function
        `f` is true.

        Args:
            f: A predicate function to apply to each element.

        Returns:
            The empty list, since dropping elements from an empty list results
            in an empty list.
        """
        return self

    def take(self, n: int) -> _CList:
        """
        Take the first `n` elements from the empty list.

        Args:
            n: The number of elements to take.

        Returns:
            The empty list, since taking elements from an empty list results
            in an empty list.
        """
        return self

    def take_while(self, f: Callable[[A], bool]) -> _CList:
        """
        Take elements from the empty list as long as the predicate function
        `f` is true.

        Args:
            f: A predicate function to apply to each element.

        Returns:
            The empty list, since taking elements from an empty list results
            in an empty list.
        """
        return self

    def split_at(self, i: int) -> Tuple[_CList, _CList]:
        """
        Split the empty list into two lists at index `i`.

        Args:
            i: The index to split at.

        Returns:
            A tuple of two empty lists.
        """
        return self, self


@dataclass(frozen=True)
class Cons[A](CList[A]):
    """
    Represents a non-empty list with a head element and a tail list.
    """

    head: A
    tail: CList[A] = field(default_factory=Nil)

    def __repr__(self):
        """
        Return a string representation of the non-empty list.

        Returns:
            A string representing the list, showing the head and tail.
        """
        match self.tail:
            case Nil():
                return f"Cons({self.head})"
        return f"Cons({self.head}, {self.tail})"

    def append(self, other: _CList) -> _CList:
        """
        Append another list to the end of this non-empty list.

        Args:
            other: The list to append.

        Returns:
            A new list with `other` appended to the end of this list.
        """
        return Cons(self.head, self.tail.append(other))

    def fold_right[B](self, acc: B, f: Callable[[A, B], B]) -> B:
        """
        Fold the non-empty list from right to left.

        Args:
            acc: The initial accumulator value.
            f: A function to apply, taking an element and the current accumulator.

        Returns:
            The result of folding the list from right to left.
        """
        return f(self.head, self.tail.fold_right(acc, f))

    def fold_left[B](self, acc: B, f: Callable[[B, A], B]) -> B:
        """
        Fold the non-empty list from left to right.

        Args:
            acc: The initial accumulator value.
            f: A function to apply, taking the current accumulator and an element.

        Returns:
            The result of folding the list from left to right.
        """
        return self.tail.fold_left(f(acc, self.head), f)

    def drop(self, n: int) -> _CList:
        """
        Drop the first `n` elements from the non-empty list.

        Args:
            n: The number of elements to drop.

        Returns:
            A new list with the first `n` elements removed.
        """
        return self if n <= 0 else self.tail.drop(n - 1)

    def drop_while(self, f: Callable[[A], bool]) -> _CList:
        """
        Drop elements from the non-empty list as long as the predicate function
        `f` is true.

        Args:
            f: A predicate function to apply to each element.

        Returns:
            A new list with elements removed while `f` is true.
        """
        return self if not f(self.head) else self.tail.drop_while(f)

    def take(self, n: int) -> _CList:
        """
        Take the first `n` elements from the non-empty list.

        Args:
            n: The number of elements to take.

        Returns:
            A new list containing the first `n` elements.
        """
        return Cons(self.head) if n <= 1 else self.head << self.tail.take(n - 1)

    def take_while(self, f: Callable[[A], bool]) -> _CList:
        """
        Take elements from the non-empty list as long as the predicate function
        `f` is true.

        Args:
            f: A predicate function to apply to each element.

        Returns:
            A new list with elements taken while `f` is true.
        """
        return self.head << self.tail.take_while(f) if f(self.head) else Nil()

    def split_at(self, i: int) -> Tuple[_CList, _CList]:
        """
        Split the non-empty list into two lists at index `i`.

        Args:
            i: The index to split at.

        Returns:
            A tuple of two lists: the first containing elements up to `i`,
            and the second containing the rest.
        """
        return self.take(i), self.drop(i)
