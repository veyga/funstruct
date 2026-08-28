"""Type class protocols and abstract bases."""

from funstruct.typeclasses._applicative import Applicative
from funstruct.typeclasses._functor import Functor
from funstruct.typeclasses._monad import Monad
from funstruct.typeclasses._monoid import Monoid
from funstruct.typeclasses._semigroup import Semigroup

__all__ = [
    "Functor",
    "Applicative",
    "Monad",
    "Semigroup",
    "Monoid",
]
