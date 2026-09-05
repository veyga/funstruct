"""MonadTransformer: a monad that wraps another monad, combining effects.

MonadTransformer[F, A] — F is the inner monad, A is the value type.

**A monad transformer is not really a typeclass, but for the ergonomics
of this library, we treat it as such**

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

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Generic, TypeVar

_F = TypeVar("_F")
_A = TypeVar("_A")
_B = TypeVar("_B")


class MonadTransformer(ABC, Generic[_F, _A]):
    """Base for monad transformers — separate from the Monad hierarchy.

    In Scala/Haskell, transformers are not a typeclass — they're data types
    with separate Monad instances. This base provides the shared interface
    and derived methods without inheriting from Monad.

    Haskell equivalent: ``class MonadTrans t where lift :: Monad m => m a -> t m a``
    In funstruct this is ``lift_f``.

    Type parameters:
        _F: The inner monad type (must support .bind(), .map(), .pure()).
        _A: The value type produced by the transformer.
    """

    @abstractmethod
    def bind(self, f: Callable) -> MonadTransformer: ...

    @abstractmethod
    def map(self, f: Callable) -> MonadTransformer: ...

    @classmethod
    @abstractmethod
    def pure(cls, value, monad: type) -> MonadTransformer: ...

    @classmethod
    @abstractmethod
    def lift_f(cls, inner: _F) -> MonadTransformer: ...

    @classmethod
    @abstractmethod
    def do(cls, gen_fn: Callable) -> Callable[..., MonadTransformer]: ...

    def ap(self, other: MonadTransformer) -> MonadTransformer:
        """Derived from bind + map."""
        return self.bind(lambda f: other.map(f))

    def map2(self, other: MonadTransformer, f: Callable) -> MonadTransformer:
        """Combine two values with a function."""
        return self.bind(lambda a: other.map(lambda b: f(a, b)))

    def then(self, other: MonadTransformer) -> MonadTransformer:
        """Sequence: run self, discard value, run next."""
        return self.bind(lambda _: other)

    def product(self, other: MonadTransformer) -> MonadTransformer:
        """Combine two values into a tuple."""
        return self.map(lambda a: lambda b: (a, b)).ap(other)

    def __mul__(self, other: MonadTransformer) -> MonadTransformer:
        """Alias for product."""
        return self.product(other)

    def __rshift__(self, f: Callable) -> MonadTransformer:
        """Alias for bind."""
        return self.bind(f)


__all__ = [
    "MonadTransformer",
]
