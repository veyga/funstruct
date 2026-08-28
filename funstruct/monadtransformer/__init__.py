"""
Monad transformer types.

"Transformer" just means "adds a new effect to an existing monad."
- Applicatives compose generically (you can always combine two applicatives into one)
- Monads do NOT compose generically (you need a transformer specific to each monad)

Pattern:
- StateT[F, S, A] = S -> F[(S, A)] — adds state to F
- ReaderT[F, Ctx, A] = Ctx -> F[A] — adds shared env to F
- EitherT[F, E, A] = F[Either[E, A]] — adds typed errors to F
- OptionT[F, A] = F[Option[A]] — adds "might not exist" to F

"""

from _funstruct._reader_t import ReaderT as ReaderT
from _funstruct._state_t import StateT as StateT
