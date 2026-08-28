"""
MonadTransformer: a monad that wraps another monad, combining their effects.

MonadTransformer[F, A] — F is the inner monad, A is the value type.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Generic, TypeVar

from funstruct.typeclasses._monad import Monad

_F = TypeVar("_F")  # The inner monad (must support .bind/.map/.pure)
_A = TypeVar("_A")  # The value type


class MonadTransformer(Monad, Generic[_F, _A]):
    """Base for monad transformers (ReaderT, StateT).

    Note: Mathematically, a monad transformer is a type constructor (Monad -> Monad),
    not a class. In Haskell: `class MonadTrans t where lift :: Monad m => m a -> t m a`.
    Python lacks higher-kinded types, so we can't express "a function from type to type"
    at the type level. This class is a pragmatic marker — it signals "I wrap an inner
    monad and provide lift/and_then" without capturing the full mathematical concept.

    Type parameters:
        _F: The inner monad type. Must support .bind(), .map(),
            .pure(). Duck-typed at runtime.
        _A: The value type produced by the transformer.

    Each transformer implements its own do and and_then.
    """

    @classmethod
    @abstractmethod
    def lift(cls, inner: _F) -> MonadTransformer[_F, _A]:
        """Lift an inner monad value into the transformer.

        This is the defining operation of a monad transformer —
        the bridge from the inner monad into the combined monad.
        """
        ...

    @abstractmethod
    def and_then(self, other) -> MonadTransformer[_F, _A]:
        """Kleisli composition: output of self becomes input of other."""
        ...


__all__ = [
    "MonadTransformer",
]
