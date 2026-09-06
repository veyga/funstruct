"""Monad transformers — combine two monadic effects in a single pipeline.

Transformers exist because monads do NOT compose generically. If you have
``Future[Option[User]]``, you can't ``bind`` through both layers at once —
you'd need to unwrap the Future, then pattern match the Option, at every step.

A transformer makes the nesting implicit. You write one flat pipeline;
the transformer peels both layers in ``bind``.

Types:
    OptionT[F, A]       = F[Option[A]]       — absence + F's effects
    EitherT[F, E, A]    = F[Either[E, A]]    — typed errors + F's effects
    ReaderT[F, Ctx, A]  = Ctx -> F[A]        — shared environment + F's effects
    StateT[F, S, A]     = S -> F[(S, A)]     — threaded state + F's effects
    WriterT[F, W, A]    = F[(A, W)]          — accumulated output + F's effects

Example — OptionT flattens ``Future[Option[...]]`` into a single pipeline::

    from funstruct.monad.option import Option, Some, Nothing
    from funstruct.monad.future import Future
    from funstruct.experimental.monadtransformer.option_t import OptionT

    # These return different nested shapes:
    def get_user(name: str) -> Future[Option[User]]:
        return Future.pure(Option.from_optional(users.get(name)))

    def get_age(user: User) -> Future[int]:
        return Future.pure(3000)

    def get_nickname(user: User) -> Option[str]:
        return Option.from_optional(nicknames.get(user.name))

    # Without transformer — manual unwrapping at every step:
    #   result = await get_user("me")     # Future[Option[User]]
    #   match result:
    #       case Some(user):
    #           age = await get_age(user)  # Future[int] — different shape!
    #           ...

    # With OptionT — one flat pipeline, lift mismatched types:
    @OptionT.do
    def pipeline() -> OptionT[Future, str]:
        user = yield OptionT(get_user("me"))                      # Future[Option[User]] — exact match
        age  = yield OptionT.lift_f(get_age(user))                # Future[int] → OptionT (missing Option layer)
        nick = yield OptionT.from_option(get_nickname(user), Future)  # Option[str] → OptionT (missing Future layer)
        return f"{nick}{age}"

    result: Option[str] = await pipeline().run()  # unwrap at the boundary

Status: experimental. API may change.
"""

from funstruct.experimental.monadtransformer.either_t import EitherT as EitherT
from funstruct.experimental.monadtransformer.option_t import OptionT as OptionT
from funstruct.experimental.monadtransformer.reader_t import ReaderT as ReaderT
from funstruct.experimental.monadtransformer.state_t import StateT as StateT
from funstruct.experimental.monadtransformer.writer_t import WriterT as WriterT
