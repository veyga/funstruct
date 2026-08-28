"""Option monad — presence or absence of a value.

Some(value) represents presence; Nothing represents absence.
bind/>> short-circuits on Nothing.

Mirrors Scala's Option[A] from fpinscala.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

from funstruct.typeclasses._monad import Monad

A = TypeVar("A")


class Option(Monad, Generic[A]):
    """Option[A]: either Some(value) or Nothing.

    Performance characteristics:
        - map/bind/ap: O(1)
        - from_value:  O(1)
    """

    @classmethod
    def pure(cls, value: A) -> Option[A]:
        return Some(value)

    @classmethod
    def from_value(cls, value: A) -> Option[A]:
        """Alias for pure — lifts a value into Some."""
        return Some(value)

    @classmethod
    def from_optional(cls, value: A | None) -> Option[A]:
        """Convert a Python value that might be None into an Option."""
        return Nothing() if value is None else Some(value)

    @classmethod
    def sequence(cls, options: "CList[Option[A]]") -> "Option[CList[A]]":
        """CList[Option[A]] → Option[CList[A]].

        Returns Some(clist) if all are Some, Nothing if any is Nothing.
        Tail-recursive via @tco.
        """
        from _funstruct._cons import Cons, Nil
        from _funstruct._tailrec import tail_call, tco

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
    def traverse(cls, values: "CList[A]", f: Callable[[A], Option]) -> "Option[CList]":
        """CList[A] → (A → Option[B]) → Option[CList[B]].

        Applies f to each element, short-circuits on first Nothing.
        """
        return cls.sequence(values.map(f))

    @classmethod
    def do(cls, gen_fn: Callable) -> Option:
        """Do-notation. Short-circuits on Nothing."""
        gen = gen_fn()
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

    @property
    def is_some(self) -> bool:
        raise NotImplementedError

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

    def map(self, f: Callable) -> Option:
        return Some(f(self.value))

    def ap(self, other: Option) -> Option:
        match other:
            case Some(val):
                return Some((self.value, val))
            case _:
                return other

    def bind(self, f: Callable[[A], Option]) -> Option:
        return f(self.value)

    def get_or_else(self, default: A) -> A:
        return self.value

    def or_else(self, fallback: Callable[[], Option[A]]) -> Option[A]:
        return self

    def filter(self, f: Callable[[A], bool]) -> Option[A]:
        return self if f(self.value) else Nothing()

    def fold(self, on_nothing: Callable, on_some: Callable):
        return on_some(self.value)

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

    def map(self, f: Callable) -> Option:
        return self

    def ap(self, other: Option) -> Option:
        return self

    def bind(self, f: Callable) -> Option:
        return self

    def get_or_else(self, default: A) -> A:
        return default

    def or_else(self, fallback: Callable[[], Option[A]]) -> Option[A]:
        return fallback()

    def filter(self, f: Callable) -> Option:
        return self

    def fold(self, on_nothing: Callable, on_some: Callable):
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


__all__ = ["Option", "Some", "Nothing"]
