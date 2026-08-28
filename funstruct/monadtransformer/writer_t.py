"""WriterT — writer monad transformer over any monad.

Adds accumulated output/logging to any monad F.
WriterT[F, W, A] wraps F[(A, W)].

Examples:
    >>> from funstruct.monadtransformer.writer_t import WriterT
    >>> from funstruct.monad import Either, Right, Left
    >>> from funstruct.typeclasses import Monoid

    >>> list_monoid = Monoid(typ=list, combine=lambda a, b: a + b, empty=[])
    >>> class LogT(WriterT):
    ...     _monoid = list_monoid

    bind accumulates output:

    >>> w = LogT.pure(1, Either).bind(lambda x: LogT(Right((x + 1, ["inc"]))))
    >>> w.run()
    Right((2, ['inc']))

    map doesn't touch output:

    >>> LogT(Right((5, ["init"]))).map(lambda x: x * 2).run()
    Right((10, ['init']))

    tell produces output:

    >>> LogT.tell(["hello"], Either).run()
    Right((None, ['hello']))

    lift wraps F[A] with empty output:

    >>> LogT.lift(Right(42)).run()
    Right((42, []))

    short-circuits on Left:

    >>> LogT(Left("err")).map(lambda x: x + 1).run()
    Left('err')
"""

from _funstruct._writer_t import *  # noqa: F403
