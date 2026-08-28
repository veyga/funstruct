"""
MonadTransformer: a monad that wraps another monad, combining their effects.

MonadTransformer[F, A] — F is the inner monad, A is the value type.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Generic, TypeVar

from funstruct.typeclasses._monad import Monad

_F = TypeVar("_F")  # The inner monad (must support .bind/.map/.from_value)
_A = TypeVar("_A")  # The value type


class MonadTransformer(Monad, Generic[_F, _A]):
    """Base for monad transformers (ReaderT, StateT).

    Type parameters:
        _F: The inner monad type. Must support .bind(), .map(), .from_value().
            Python cannot enforce this at the type level — it's duck-typed at runtime.
        _A: The value type produced by the transformer.

    Each transformer implements its own do and and_then.
    """

    @abstractmethod
    def and_then(self, other) -> "MonadTransformer[_F, _A]":
        """Kleisli composition: output of self becomes input of other."""
        ...


__all__ = [
    "MonadTransformer",
]
