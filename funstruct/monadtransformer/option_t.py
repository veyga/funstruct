"""OptionT — adds optionality to any monad F.

OptionT[F, A] wraps F[Option[A]]. bind short-circuits on Nothing,
map transforms the value inside Some.

Examples:
    >>> from funstruct.monadtransformer.option_t import OptionT
    >>> from funstruct.monad.either import Either, Right, Left
    >>> from funstruct.monad.option import Some, Nothing

    Wrapping Either — a computation that can fail OR be absent:

    >>> OptionT(Right(Some(1))).map(lambda x: x + 10).run()
    Right(Some(11))
    >>> OptionT(Right(Nothing())).map(lambda x: x + 10).run()
    Right(Nothing())
    >>> OptionT(Left("db error")).map(lambda x: x + 10).run()
    Left('db error')

    bind chains — short-circuits on Nothing OR Left:

    >>> OptionT(Right(Some(1))).bind(
    ...     lambda x: OptionT(Right(Some(x * 10)))
    ... ).run()
    Right(Some(10))
    >>> OptionT(Right(Nothing())).bind(
    ...     lambda x: OptionT(Right(Some(x * 10)))
    ... ).run()
    Right(Nothing())

    or_else — recover from Nothing (not from Left):

    >>> OptionT(Right(Nothing())).or_else(
    ...     lambda: OptionT(Right(Some(99)))
    ... ).run()
    Right(Some(99))

    lift — bring F[A] into OptionT (wraps in Some):

    >>> OptionT.lift(Right(42)).run()
    Right(Some(42))
"""

from _funstruct._option_t import OptionT as OptionT
