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

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, TypeVar

from funstruct.typeclasses.mixins.dot_notation import DotNotation
from funstruct.util.created_at import CapturesCreationSiteMixin

if TYPE_CHECKING:
    from funstruct.collections.cons import CList

E = TypeVar("E")
A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


class Either(DotNotation, Generic[E, A]):
    """Either[E, A]: Right(value) or Left(error).

    Right-biased monad. bind/map/>> operate on the Right value
    and short-circuit on Left.
    """

    @classmethod
    def pure(cls, value: A) -> Either[E, A]:
        return Right(value)

    @classmethod
    def raise_error(cls, error: E) -> Either[E, A]:
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
        """CList[Either[E, A]] -> Either[E, CList[A]]."""
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
        return cls.sequence(values.map(f))

    @property
    def is_right(self) -> bool:
        return False

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

    def bind(self, f: Callable[[A], Either[E, B]]) -> Either[E, B]:
        return f(self.value)

    def left_map(self, f: Callable[[E], E]) -> Either[E, A]:
        return self

    def handle_error_with(self, f: Callable[[E], Either]) -> Either[E, A]:
        return self

    def bimap(self, on_left: Callable[[E], E], on_right: Callable[[A], B]) -> Either:
        return Right(on_right(self.value))

    def get_or_else(self, default: A) -> A:
        return self.value

    def fold(self, on_left: Callable[[E], C], on_right: Callable[[A], C]) -> C:
        return on_right(self.value)

    def swap(self) -> Either[A, E]:
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
class Left(CapturesCreationSiteMixin, Either[E, A]):
    """Error case. Captures creation site automatically."""

    error: E

    @property
    def is_right(self) -> bool:
        return False

    def bind(self, f: Callable[[A], Either[E, B]]) -> Either[E, B]:
        return self

    def left_map(self, f: Callable[[E], E]) -> Either[E, A]:
        """>>> Left("oops").left_map(lambda e: e.upper())
        Left('OOPS')
        """
        return Left(f(self.error))

    def handle_error_with(self, f: Callable[[E], Either]) -> Either:
        """>>> Left("oops").handle_error_with(lambda e: Right(f"recovered: {e}"))
        Right('recovered: oops')
        """
        return f(self.error)

    def bimap(self, on_left: Callable[[E], E], on_right: Callable[[A], B]) -> Either:
        return Left(on_left(self.error))

    def get_or_else(self, default: A) -> A:
        return default

    def fold(self, on_left: Callable[[E], C], on_right: Callable[[A], C]) -> C:
        return on_left(self.error)

    def swap(self) -> Either[A, E]:
        return Right(self.error)

    def __eq__(self, other: object) -> bool:
        match other:
            case Left(err):
                return self.error == err
            case _:
                return False

    def __repr__(self) -> str:
        return f"Left({repr(self.error)})"


Either._type_constructor = Either
Right._type_constructor = Either
Left._type_constructor = Either


import funstruct.monad.either.instances  # noqa: E402, F401

__all__ = [
    "Either",
    "Right",
    "Left",
]
