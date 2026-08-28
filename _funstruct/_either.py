"""Either monad — computation that may fail with a typed error.

Right-biased: map/bind operate on the Right (success) value,
short-circuit on Left (error).

Either[E, A] = Right(a) | Left(e)

Haskell: Either a b
Rust:    Result<T, E> (with flipped param order)
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, TypeVar

from funstruct.typeclasses._monad import Monad

if TYPE_CHECKING:
    from _funstruct._cons import CList

E = TypeVar("E")
A = TypeVar("A")
B = TypeVar("B")


class Either(Monad, Generic[E, A]):
    """Either[E, A]: Right(value) or Left(error).

    Right-biased monad. bind/map/>> operate on the Right value
    and short-circuit on Left.

    No __bool__: Either deliberately has no truthiness. Both Right and Left
    carry a value — neither case is "empty" or "absent." Use .is_right /
    .is_left or pattern matching instead of `if my_either:`.
    """

    @classmethod
    def pure(cls, value: A) -> Either[E, A]:
        return Right(value)

    @classmethod
    def from_error(cls, error: E) -> Either[E, A]:
        """Lift an error into Left."""
        return Left(error)

    @classmethod
    def do(cls, gen_fn: Callable) -> Either:
        """Do-notation. Short-circuits on Left.

        >>> Right(1).bind(lambda x: Right(x + 10))
        Right(11)
        >>> def pipeline():
        ...     x = yield Right(1)
        ...     y = yield Right(x + 10)
        ...     return x + y
        >>> Either.do(pipeline)
        Right(12)
        """
        gen = gen_fn()
        try:
            monadic_val = next(gen)
            while True:
                match monadic_val:
                    case Left():
                        return monadic_val
                    case Right(value):
                        monadic_val = gen.send(value)
        except StopIteration as e:
            return Right(e.value)

    @classmethod
    def sequence(cls, eithers: CList[Either[E, A]]) -> Either[E, CList[A]]:
        """CList[Either[E, A]] -> Either[E, CList[A]].

        Returns Right(clist) if all are Right, first Left otherwise.
        """
        from _funstruct._cons import Cons, Nil
        from _funstruct._tailrec import tail_call, tco

        @tco
        def _go(remaining, acc):
            match remaining:
                case Nil():
                    return Right(acc.reversed())
                case Cons(head, tail):
                    match head:
                        case Left():
                            return head
                        case Right(v):
                            return tail_call(_go)(tail, Cons(v, acc))

        return _go(eithers, Nil())

    @classmethod
    def traverse(cls, values, f: Callable) -> Either:
        """CList[A] -> (A -> Either[E, B]) -> Either[E, CList[B]].

        Applies f to each element, short-circuits on first Left.
        """
        return cls.sequence(values.map(f))

    def to_option(self):
        """Convert to Option — Right(v) → Some(v), Left(_) → Nothing.

        >>> Right(1).to_option()
        Some(1)
        >>> Left("err").to_option()
        Nothing()
        """
        from _funstruct._option import Nothing, Some

        match self:
            case Right(v):
                return Some(v)
            case _:
                return Nothing()

    @property
    @abstractmethod
    def is_right(self) -> bool: ...

    @property
    def is_left(self) -> bool:
        return not self.is_right


@dataclass(frozen=True, eq=False)
class Right(Either[E, A]):
    """Success case."""

    value: A

    @property
    def is_right(self) -> bool:
        return True

    def map(self, f: Callable[[A], B]) -> Either[E, B]:
        return Right(f(self.value))

    def bind(self, f: Callable[[A], Either[E, B]]) -> Either[E, B]:
        return f(self.value)

    def ap(self, other: Either) -> Either:
        match other:
            case Right(val):
                return Right((self.value, val))
            case _:
                return other

    def alt(self, f: Callable[[E], E]) -> Either[E, A]:
        """No-op on Right — already succeeded."""
        return self

    def or_else(self, f: Callable[[E], Either]) -> Either[E, A]:
        """No-op on Right — already succeeded."""
        return self

    def get_or_else(self, default: A) -> A:
        return self.value

    def fold(self, on_left: Callable, on_right: Callable):
        return on_right(self.value)

    def swap(self) -> Either[A, E]:
        """Swap Left/Right."""
        return Left(self.value)

    def __eq__(self, other: object) -> bool:
        match other:
            case Right(val):
                return self.value == val
            case _:
                return False

    def __repr__(self) -> str:
        return f"Right({repr(self.value)})"


@dataclass(frozen=True, eq=False)
class Left(Either[E, A]):
    """Error case."""

    error: E

    @property
    def is_right(self) -> bool:
        return False

    def map(self, f: Callable) -> Either:
        return self

    def bind(self, f: Callable) -> Either:
        return self

    def ap(self, other: Either) -> Either:
        return self

    def alt(self, f: Callable[[E], E]) -> Either[E, A]:
        """Transform the error without recovering.

        >>> Left("oops").alt(lambda e: e.upper())
        Left('OOPS')
        """
        return Left(f(self.error))

    def or_else(self, f: Callable[[E], Either]) -> Either:
        """Handle error: f receives the error, returns a new Either.

        >>> Left("oops").or_else(lambda e: Right(f"recovered: {e}"))
        Right('recovered: oops')
        >>> Left("oops").or_else(lambda e: Left(f"still bad: {e}"))
        Left('still bad: oops')
        """
        return f(self.error)

    def get_or_else(self, default: A) -> A:
        return default

    def fold(self, on_left: Callable, on_right: Callable):
        return on_left(self.error)

    def swap(self) -> Either[A, E]:
        """Swap Left/Right."""
        return Right(self.error)

    def __eq__(self, other: object) -> bool:
        match other:
            case Left(err):
                return self.error == err
            case _:
                return False

    def __repr__(self) -> str:
        return f"Left({repr(self.error)})"


__all__ = [
    "Either",
    "Right",
    "Left",
]
