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


# See _functor.py for the fa/ff/fb naming convention.


class Traversable(Foldable, Functor[_A]):
    """Container that can be traversed with an effectful function.

    Subclasses must implement ``traverse``. ``sequence`` is derived
    from ``traverse`` automatically.
    """

    @abstractmethod
    def traverse(fa: Traversable, f: Callable[[_A], object], pure_fn: Callable) -> object:
        """Map each element through f, then collect the results.

        Scala: ``def traverse[G[_]: Applicative, B](f: A => G[B]): G[F[B]]``

        fa: T[A], f: A → G[B], pure_fn: G.pure → G[T[B]]
        """
        ...

    def sequence(fa: Traversable, pure_fn: Callable) -> object:
        """Flip the nesting: T[F[A]] → F[T[A]].

        Derived from traverse with identity.
        """
        return fa.traverse(lambda x: x, pure_fn)


__all__ = [
    "Traversable",
]
