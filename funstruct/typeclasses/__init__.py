"""Type class protocols and abstract bases."""

from funstruct.typeclasses._applicative import Applicative
from funstruct.typeclasses._foldable import Foldable
from funstruct.typeclasses._functor import Functor
from funstruct.typeclasses._monad import Monad
from funstruct.typeclasses._monoid import Monoid
from funstruct.typeclasses._semigroup import Semigroup
from funstruct.typeclasses._traversable import Traversable

__all__ = [
    "Foldable",
    "Functor",
    "Traversable",
    "Applicative",
    "Monad",
    "Semigroup",
    "Monoid",
]
