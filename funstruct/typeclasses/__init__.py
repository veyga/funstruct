"""Type class protocols and abstract bases."""

from funstruct.typeclasses._dot_notation import DotNotation
from funstruct.typeclasses._monoid import Monoid
from funstruct.typeclasses._registry import register, summon, tc_of
from funstruct.typeclasses._semigroup import Semigroup
from funstruct.typeclasses._typeclasses import (
    Alternative,
    Applicative,
    Bifunctor,
    Foldable,
    Functor,
    Monad,
    MonadError,
    Traversable,
)

__all__ = [
    "Alternative",
    "Applicative",
    "Bifunctor",
    "DotNotation",
    "Foldable",
    "Functor",
    "Monad",
    "MonadError",
    "Monoid",
    "Semigroup",
    "Traversable",
    "register",
    "summon",
    "tc_of",
]
