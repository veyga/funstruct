"""Type class protocols and abstract bases."""

from funstruct.typeclass.applicative import Applicative
from funstruct.typeclass.functor import Functor
from funstruct.typeclass.monad import Monad
from funstruct.typeclass.monoid import Monoid
from funstruct.typeclass.semigroup import Semigroup

__all__ = [
    "Functor",
    "Applicative",
    "Monad",
    "Semigroup",
    "Monoid",
]
