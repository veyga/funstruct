"""Type class protocols and abstract bases."""

from funstruct.typeclasses.alternative import Alternative
from funstruct.typeclasses.applicative import Applicative
from funstruct.typeclasses.bifunctor import Bifunctor
from funstruct.typeclasses.mixins.dot_notation import DotNotation
from funstruct.typeclasses.foldable import Foldable
from funstruct.typeclasses.functor import Functor
from funstruct.typeclasses.monad import Monad
from funstruct.typeclasses.monad_error import MonadError
from funstruct.typeclasses.monoid import Monoid
from funstruct.typeclasses.utils.registry import register, summon, tc_of
from funstruct.typeclasses.semigroup import Semigroup
from funstruct.typeclasses.traversable import Traversable
from funstruct.typeclasses.typeclass import BaseTypeclass

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
    "BaseTypeclass",
    "register",
    "summon",
    "tc_of",
]
