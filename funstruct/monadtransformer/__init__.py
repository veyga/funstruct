"""
Monad transformer types.

"Transformer" just means "adds a new effect to an existing monad."
- Applicatives compose generically (you can always combine two applicatives into one)
- Monads do NOT compose generically (you need a transformer specific to each monad)

A monad transformer combines one monad with another monadic effect.

Nesting monads is always possible. Transformers make the nesting implicit.
You write one flat pipeline; the transformer peels both layers in bind.

This is the entire reason transformers exist — not to enable nesting
(you can already do that), but to eliminate the boilerplate of unwrapping
nested layers at every step.

Pattern:
- StateT[F, S, A] = S -> F[(S, A)] — adds state to F
- ReaderT[F, Ctx, A] = Ctx -> F[A] — adds shared env to F
- EitherT[F, E, A] = F[Either[E, A]] — adds typed errors to F
- OptionT[F, A] = F[Option[A]] — adds "might not exist" to F


"""

from funstruct.monadtransformer.either_t import EitherT as EitherT
from funstruct.monadtransformer.option_t import OptionT as OptionT
from funstruct.monadtransformer.reader_t import ReaderT as ReaderT
from funstruct.monadtransformer.state_t import StateT as StateT
from funstruct.monadtransformer.writer_t import WriterT as WriterT
