"""MonadTransformer: a monad that wraps another monad, combining effects.

MonadTransformer[F, A] — F is the inner monad, A is the value type.

The problem transformers solve:

    Monads don't compose automatically. If you have Either (for errors)
    and Option (for absence), nesting them gives you Either[E, Option[A]].
    Every bind now requires you to manually unwrap BOTH layers:

        # Without transformers — nested pattern matching at every step:
        result = fetch_user(id)                  # Either[Err, Option[User]]
        match result:
            case Left(e): return Left(e)         # propagate error
            case Right(None): return Right(None) # propagate absence
            case Right(user):                    # finally, the value
                email = get_email(user)          # Either[Err, Option[Email]]
                match email:                     # ...same nesting again
                    ...

    This boilerplate multiplies with every step. With 5 steps and 2 effects,
    you have 10 match arms instead of a clean pipeline.

    With OptionT, the transformer handles the nesting for you:

        # With OptionT[Either, A] — one flat pipeline:
        pipeline = (
            OptionT(fetch_user(id))
            .bind(lambda user: OptionT(get_email(user)))
            .bind(lambda email: OptionT(send_notification(email)))
        )
        # bind automatically propagates BOTH Left and None.
        # You write the happy path; the transformer handles the rest.

    This is not just convenience — it's correctness. Manual nesting
    invites bugs (forgetting to propagate one layer) and obscures intent.

"You can get along fine without transformers":

    True for simple code with one effect. But real services typically have:
        - Config/environment (Reader)
        - Database state (State)
        - Failure modes (Either)
        - Optional data (Option)
        - Audit logs (Writer)

    Combining even 2 of these manually means nested match arms at every
    step. Transformers let you write a flat pipeline that threads ALL
    effects automatically. The alternative is either:
        1. Deeply nested pattern matching (verbose, error-prone)
        2. Exceptions for everything (loses type safety, no composition)

    Transformers are the composable middle ground.

Raw Monad vs Transformer — when to use which:

    Raw monad: your computation has exactly ONE effect.
        - Validating a form → Either[ValidationError, FormData]
        - Looking up a cache → Option[CachedValue]

    Transformer: you need to COMBINE effects in a pipeline.
        - DB lookup that needs config AND might fail:
          ReaderT[Either, Config, User]
        - Stateful parser that accumulates warnings:
          StateT[Writer, ParseState, AST]
        - HTTP handler that reads env, might fail, might 404:
          ReaderT over EitherT over Option
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Generic, TypeVar

from funstruct.typeclasses._monad import Monad

_F = TypeVar("_F")  # The inner monad (must support .bind/.map/.pure)
_A = TypeVar("_A")  # The value type


class MonadTransformer(Monad, Generic[_F, _A]):
    """Base for monad transformers.

    Mathematically, a monad transformer is a type constructor (Monad -> Monad).
    In Haskell: `class MonadTrans t where lift :: Monad m => m a -> t m a`.
    Python lacks higher-kinded types, so this class is a pragmatic marker.

    Type parameters:
        _F: The inner monad type. Must support .bind(), .map(),
            .pure(). Duck-typed at runtime.
        _A: The value type produced by the transformer.
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
