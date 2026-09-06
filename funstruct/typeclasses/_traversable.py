"""Traversable — containers that can be traversed with an effect.

Traversable extends Functor with the ability to traverse the structure
with an effectful function, collecting results.

Haskell: ``class (Functor t, Foldable t) => Traversable t``
Cats: ``trait Traverse[F[_]] extends Functor[F] with Foldable[F]``

The two key operations:

    traverse: map each element to an applicative, then "flip" the nesting.
        ``T[A] → (A → F[B]) → F[T[B]]``

    sequence: flip the nesting without mapping (traverse with identity).
        ``T[F[A]] → F[T[A]]``

The ``pure_fn`` parameter is needed because Python lacks higher-kinded
type inference — you must tell traverse which Applicative to collect into.

Examples::

    from funstruct.collections.cons import CList
    from funstruct.monad.either import Either, Right, Left

    # traverse: map + collect
    CList.from_iterable([1, 2, 3]).traverse(
        lambda x: Right(x * 2), Either.pure
    )
    # Right(CList([2, 4, 6]))

    # sequence: just collect
    CList.from_iterable([Right(1), Right(2)]).sequence(Either.pure)
    # Right(CList([1, 2]))

    # short-circuits on failure
    CList.from_iterable([Right(1), Left("err")]).sequence(Either.pure)
    # Left("err")
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses._foldable import Foldable
from funstruct.typeclasses._functor import Functor

_A = TypeVar("_A")
_B = TypeVar("_B")


class Traversable(Foldable, Functor[_A]):
    """Container that can be traversed with an effectful function.

    Subclasses must implement ``traverse``. ``sequence`` is derived
    from ``traverse`` automatically.
    """

    @abstractmethod
    def traverse(self, f: Callable[[_A], object], pure_fn: Callable) -> object:
        """Map each element through f, then collect the results.

        Args:
            f: A → F[B] — effectful function applied to each element.
            pure_fn: the target Applicative's ``pure`` (e.g., ``Either.pure``).

        Returns:
            F[T[B]] — the collected results inside the applicative.
        """
        ...

    def sequence(self, pure_fn: Callable) -> object:
        """Flip the nesting: T[F[A]] → F[T[A]].

        Derived from traverse with identity.

        Args:
            pure_fn: the target Applicative's ``pure``.
        """
        return self.traverse(lambda x: x, pure_fn)


__all__ = [
    "Traversable",
]
