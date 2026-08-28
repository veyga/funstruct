"""EitherT — monad transformer that adds typed errors to any monad F.

``EitherT[F, E, A]`` wraps ``F[Either[E, A]]``.

Examples:
    >>> from funstruct.monadtransformer.either_t import EitherT
    >>> from funstruct.monad.option import Option, Some, Nothing
    >>> from funstruct.monad.either import Right, Left

    EitherT over Option — combines "might not exist" with "might fail":

    >>> EitherT(Some(Right(1))).map(lambda x: x + 10).run()
    Some(Right(11))
    >>> EitherT(Some(Left("err"))).map(lambda x: x + 10).run()
    Some(Left('err'))
    >>> EitherT(Nothing()).map(lambda x: x + 10).run()
    Nothing()

    bind — chains that short-circuit on Left OR Nothing:

    >>> inc = lambda x: EitherT(Some(Right(x + 1)))
    >>> EitherT(Some(Right(1))).bind(inc).bind(inc).run()
    Some(Right(3))
    >>> EitherT(Some(Left("stop"))).bind(inc).run()
    Some(Left('stop'))

    or_else — recover from Left:

    >>> EitherT(Some(Left("err"))).or_else(
    ...     lambda e: EitherT(Some(Right(f"recovered: {e}")))
    ... ).run()
    Some(Right('recovered: err'))

    lift — bring F[A] into EitherT (wraps value in Right):

    >>> EitherT.lift(Some(42)).run()
    Some(Right(42))

    pure — lift a plain value:

    >>> EitherT.pure(99, Option).run()
    Some(Right(99))
"""

from _funstruct._either_t import *  # noqa: F403
