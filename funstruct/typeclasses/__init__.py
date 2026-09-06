"""Type class protocols and abstract bases."""

from funstruct.typeclasses.alternative import Alternative
from funstruct.typeclasses.applicative import Applicative
from funstruct.typeclasses.bifunctor import Bifunctor
from funstruct.typeclasses.foldable import Foldable
from funstruct.typeclasses.functor import Functor
from funstruct.typeclasses.mixins.data_type import DataType
from funstruct.typeclasses.mixins.dot_notation import DotNotation
from funstruct.typeclasses.mixins.type_constructor import TypeConstructor
from funstruct.typeclasses.monad import Monad
from funstruct.typeclasses.monad_error import MonadError
from funstruct.typeclasses.monoid import Monoid
from funstruct.typeclasses.semigroup import Semigroup
from funstruct.typeclasses.traversable import Traversable
from funstruct.typeclasses.typeclass import BaseTypeclass
from funstruct.typeclasses.utils.registry import register, summon, tc_of

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
    "DataType",
    "TypeConstructor",
    "register",
    "summon",
    "tc_of",
]
