"""MonadError — a Monad that can raise and handle typed errors.

Monad gives you pure + bind (construct and sequence successes).
MonadError adds raise_error + handle_error_with (construct and
sequence failures). Together they cover both rails:

    pure(a)                — put a value ON the success rail
    raise_error(e)         — put a value ON the error rail
    bind(f)                — continue along the success rail
    handle_error_with(f)   — recover FROM the error rail

Scala/Cats: ``MonadError[F, E]``
Haskell:    ``MonadError e m``

This is what lets tagless final programs fail generically —
instead of calling Err() directly,
they call raise_error through the typeclass.

Instances:
    Result, Either, and AsyncResult are MonadError instances.
    Option is NOT — it has no error channel (Nothing carries no value).
    State is NOT — it always succeeds (S -> (S, A) has no error rail).
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from typing import TypeVar


from funstruct.typeclasses._monad import Monad

_A = TypeVar("_A")
_E = TypeVar("_E")


class MonadError(Monad[_A]):
    """A Monad with an error channel.

    Scala: ``trait MonadError[F[_], E] extends Monad[F]``
    """

    @classmethod
    @abstractmethod
    def raise_error(cls, error: _E) -> MonadError[_A]:
        """Lift an error into the monad.

        Scala: ``def raiseError[A](e: E): F[A]``
        """
        ...

    @abstractmethod
    def handle_error_with(
        fa: MonadError[_A], f: Callable[[_E], MonadError[_A]]
    ) -> MonadError[_A]:
        """Recover from an error. f can succeed or re-fail.

        Scala: ``def handleErrorWith[A](fa: F[A])(f: E => F[A]): F[A]``
        """
        ...



__all__ = [
    "MonadError",
]
