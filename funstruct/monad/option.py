"""Option monad — presence or absence of a value.

Examples:
    >>> from funstruct.monad.option import Option, Some, Nothing
    >>> from funstruct.collections.cons import Cons, Nil, CList
    >>> Some(1).map(lambda x: x + 10)
    Some(11)
    >>> Nothing().bind(lambda x: Some(x * 2))
    Nothing()
    >>> Some(1) >> (lambda x: Some(x + 1))
    Some(2)
    >>> Option.from_optional(None)
    Nothing()

    map2 — combine two Options with a function:

    >>> Some(2).map2(Some(3), lambda a, b: a + b)
    Some(5)
    >>> Some(2).map2(Nothing(), lambda a, b: a + b)
    Nothing()

    sequence — CList[Option[A]] → Option[CList[A]]:

    >>> Option.sequence(Cons(Some(1), Cons(Some(2), Cons(Some(3), Nil()))))
    Some(Cons(1, Cons(2, Cons(3, Nil()))))
    >>> Option.sequence(Cons(Some(1), Cons(Nothing(), Cons(Some(3), Nil()))))
    Nothing()

    traverse — map then sequence:

    >>> Option.traverse(CList.from_iterable([1, 2, 3]), lambda x: Some(x * 10))
    Some(Cons(10, Cons(20, Cons(30, Nil()))))
    >>> safe = lambda x: Some(x) if x != 0 else Nothing()
    >>> Option.traverse(CList.from_iterable([1, 0, 3]), safe)
    Nothing()
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, TypeVar, final

from funstruct.typeclasses._alternative import Alternative
from funstruct.typeclasses._monad import Monad

if TYPE_CHECKING:
    from funstruct.collections.cons import CList

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


class Option(Monad, Alternative, Generic[A]):
    """Option[A]: either Some(value) or Nothing.

    Performance characteristics:
        - map/bind/ap: O(1)
        - pure:        O(1)
    """

    # Type-narrowed signatures so type checkers see Option[B], not Monad[B].
    # Implementations live in Some/Nothing below. @abstractmethod with ...
    # means "must be implemented by subclasses" without raising anything.
    @abstractmethod
    def bind(fa: Option, f: Callable[[A], Option[B]]) -> Option[B]: ...

    @abstractmethod
    def get_or_else(fa: Option, default: A) -> A: ...

    @abstractmethod
    def handle_error_with(
        fa: Option, fallback: Callable[[], Option[A]]
    ) -> Option[A]: ...

    @classmethod
    @final
    def pure(cls, value: A) -> Option[A]:
        return Some(value)

    @classmethod
    def empty(cls) -> Option:
        return Nothing()

    @classmethod
    def from_optional(cls, value: A | None) -> Option[A]:
        """Convert a Python value that might be None into an Option."""
        return Nothing() if value is None else Some(value)

    @classmethod
    def sequence(cls, options: CList[Option[A]]) -> Option[CList[A]]:
        """CList[Option[A]] → Option[CList[A]].

        Returns Some(clist) if all are Some, Nothing if any is Nothing.
        Tail-recursive via @tco.
        """
        from funstruct.collections.cons import Cons, Nil
        from funstruct.util.tailrec import tail_call, tco

        @tco
        def _go(remaining, acc):
            match remaining:
                case Nil():
                    return Some(acc.reversed())
                case Cons(head, tail):
                    match head:
                        case Nothing():
                            return Nothing()
                        case Some(v):
                            return tail_call(_go)(tail, Cons(v, acc))

        return _go(options, Nil())

    @classmethod
    def traverse(cls, values: CList[A], f: Callable[[A], Option]) -> Option[CList]:
        """CList[A] → (A → Option[B]) → Option[CList[B]].

        Applies f to each element, short-circuits on first Nothing.
        """
        return cls.sequence(values.map(f))

    @classmethod
    def do(cls, gen_fn: Callable) -> Callable[..., Option]:
        """Do-notation. Short-circuits on Nothing. Returns a callable.

        >>> def pipeline():
        ...     x = yield Some(1)
        ...     y = yield Some(x + 10)
        ...     return x + y
        >>> Option.do(pipeline)()
        Some(12)
        """

        def _thunk(*args, **kwargs):
            gen = gen_fn(*args, **kwargs)
            try:
                monadic_val = next(gen)
                while True:
                    match monadic_val:
                        case Nothing():
                            return Nothing()
                        case Some(value):
                            monadic_val = gen.send(value)
            except StopIteration as e:
                return Some(e.value)

        return _thunk

    @property
    @abstractmethod
    def is_some(self) -> bool: ...

    @property
    def is_nothing(self) -> bool:
        return not self.is_some


@dataclass(frozen=True, eq=False)
class Some(Option[A]):
    """Presence of a value."""

    value: A

    @property
    def is_some(self) -> bool:
        return True

    def bind(fa: Some, f: Callable[[A], Option]) -> Option:
        return f(fa.value)

    def get_or_else(fa: Some, default: A) -> A:
        return fa.value

    def handle_error_with(fa: Some, fallback: Callable[[], Option[A]]) -> Option[A]:
        return fa

    def or_else(fa: Some, fb: Option[A]) -> Option[A]:
        return fa

    def filter(fa: Some, f: Callable[[A], bool]) -> Option[A]:
        return fa if f(fa.value) else Nothing()

    def fold(fa: Some, on_nothing: Callable[[], C], on_some: Callable[[A], C]) -> C:
        return on_some(fa.value)

    def __eq__(self, other: object) -> bool:
        match other:
            case Some(val):
                return self.value == val
            case _:
                return False

    def __bool__(self) -> bool:
        return True

    def __repr__(self) -> str:
        return f"Some({repr(self.value)})"


class Nothing(Option):
    """Absence of a value (singleton)."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def is_some(self) -> bool:
        return False

    def bind(fa: Nothing, f: Callable[[A], Option[B]]) -> Option[B]:
        return fa

    def get_or_else(fa: Nothing, default: A) -> A:
        return default

    def handle_error_with(fa: Nothing, fallback: Callable[[], Option[A]]) -> Option[A]:
        return fallback()

    def or_else(fa: Nothing, fb: Option[A]) -> Option[A]:
        return fb

    def filter(fa: Nothing, f: Callable[[A], bool]) -> Option:
        return fa

    def fold(fa: Nothing, on_nothing: Callable[[], C], on_some: Callable[[A], C]) -> C:
        return on_nothing()

    def __eq__(self, other: object) -> bool:
        match other:
            case Nothing():
                return True
            case _:
                return False

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return "Nothing()"


__all__ = [
    "Option",
    "Some",
    "Nothing",
]
