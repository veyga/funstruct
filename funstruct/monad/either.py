"""Either monad — typed error handling.

Either[E, A] = Right(a) | Left(e). Right-biased.

Examples:
    >>> from funstruct.monad.either import Either, Right, Left
    >>> Right(10).map(lambda x: x + 1)
    Right(11)
    >>> Left("err").map(lambda x: x + 1)
    Left('err')
    >>> Right(10).bind(lambda x: Right(x * 2))
    Right(20)
    >>> Left("err").bind(lambda x: Right(x * 2))
    Left('err')

    handle_error_with — recover from Left:

    >>> Left("err").handle_error_with(lambda e: Right("default"))
    Right('default')
    >>> Right(10).handle_error_with(lambda e: Right("default"))
    Right(10)

    do-notation:

    >>> def pipeline():
    ...     x = yield Right(1)
    ...     y = yield Right(x + 10)
    ...     return x + y
    >>> Either.do(pipeline)()
    Right(12)
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, TypeVar, final

from funstruct.typeclasses._monad import Monad
from funstruct.util.created_at import CapturesCreationSiteMixin

if TYPE_CHECKING:
    from funstruct.collections.cons import CList

E = TypeVar("E")
A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


class Either(Monad, Generic[E, A]):
    """Either[E, A]: Right(value) or Left(error).

    Right-biased monad. bind/map/>> operate on the Right value
    and short-circuit on Left.

    No __bool__: Either deliberately has no truthiness. Both Right and Left
    carry a value — neither case is "empty" or "absent." Use .is_right /
    .is_left or pattern matching instead of `if my_either:`.
    """

    @classmethod
    @final
    def pure(cls, value: A) -> Either[E, A]:
        return Right(value)

    @classmethod
    def from_error(cls, error: E) -> Either[E, A]:
        """Lift an error into Left."""
        return Left(error)

    @classmethod
    def do(cls, gen_fn: Callable) -> Callable[..., Either]:
        """Do-notation. Short-circuits on Left. Returns a callable.

        >>> def pipeline():
        ...     x = yield Right(1)
        ...     y = yield Right(x + 10)
        ...     return x + y
        >>> Either.do(pipeline)()
        Right(12)
        """

        def _thunk(*args, **kwargs):
            gen = gen_fn(*args, **kwargs)
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

        return _thunk

    @classmethod
    def sequence(cls, eithers: CList[Either[E, A]]) -> Either[E, CList[A]]:
        """CList[Either[E, A]] -> Either[E, CList[A]].

        Returns Right(clist) if all are Right, first Left otherwise.
        """
        from funstruct.collections.cons import Cons, Nil
        from funstruct.util.tailrec import tail_call, tco

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
    def traverse(cls, values, f: Callable[[A], Either[E, B]]) -> Either:
        """CList[A] -> (A -> Either[E, B]) -> Either[E, CList[B]].

        Applies f to each element, short-circuits on first Left.
        """
        return cls.sequence(values.map(f))

    @abstractmethod
    def left_map(self, f: Callable[[E], E]) -> Either[E, A]:
        """Transform the error without recovering. No-op on Right.

        Cats: ``leftMap``
        """
        ...

    @abstractmethod
    def handle_error_with(self, f: Callable[[E], Either]) -> Either:
        """Recover from error — f can succeed (Right) or re-fail (Left). No-op on Right.

        Cats: ``handleErrorWith``
        """
        ...

    @abstractmethod
    def bimap(self, on_left: Callable[[E], E], on_right: Callable[[A], B]) -> Either:
        """Transform both sides.

        Cats: ``bimap``
        """
        ...

    @abstractmethod
    def get_or_else(self, default: A) -> A:
        """Extract the value, or return default if Left."""
        ...

    @abstractmethod
    def fold(self, on_left: Callable[[E], C], on_right: Callable[[A], C]) -> C:
        """Eliminate — apply on_left or on_right depending on the case."""
        ...

    @abstractmethod
    def swap(self) -> Either[A, E]:
        """Swap Left and Right."""
        ...

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

    def bind(fa: Right, f: Callable[[A], Either[E, B]]) -> Either[E, B]:
        return f(fa.value)

    def left_map(fa: Right, f: Callable[[E], E]) -> Either[E, A]:
        return fa

    def handle_error_with(fa: Right, f: Callable[[E], Either]) -> Either[E, A]:
        return fa

    def bimap(
        fa: Right, on_left: Callable[[E], E], on_right: Callable[[A], B]
    ) -> Either:
        return Right(on_right(fa.value))

    def get_or_else(fa: Right, default: A) -> A:
        return fa.value

    def fold(fa: Right, on_left: Callable[[E], C], on_right: Callable[[A], C]) -> C:
        return on_right(fa.value)

    def swap(fa: Right) -> Either[A, E]:
        return Left(fa.value)

    def __eq__(self, other: object) -> bool:
        match other:
            case Right(val):
                return self.value == val
            case _:
                return False

    def __repr__(self) -> str:
        return f"Right({repr(self.value)})"


@dataclass(frozen=True, eq=False)
class Left(CapturesCreationSiteMixin, Either[E, A]):
    """Error case. Captures creation site automatically."""

    error: E

    @property
    def is_right(self) -> bool:
        return False

    def bind(fa: Left, f: Callable[[A], Either[E, B]]) -> Either[E, B]:
        return fa

    def left_map(fa: Left, f: Callable[[E], E]) -> Either[E, A]:
        """>>> Left("oops").left_map(lambda e: e.upper())
        Left('OOPS')
        """
        return Left(f(fa.error))

    def handle_error_with(fa: Left, f: Callable[[E], Either]) -> Either:
        """>>> Left("oops").handle_error_with(lambda e: Right(f"recovered: {e}"))
        Right('recovered: oops')
        """
        return f(fa.error)

    def bimap(
        fa: Left, on_left: Callable[[E], E], on_right: Callable[[A], B]
    ) -> Either:
        return Left(on_left(fa.error))

    def get_or_else(fa: Left, default: A) -> A:
        return default

    def fold(fa: Left, on_left: Callable[[E], C], on_right: Callable[[A], C]) -> C:
        return on_left(fa.error)

    def swap(fa: Left) -> Either[A, E]:
        return Right(fa.error)

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
