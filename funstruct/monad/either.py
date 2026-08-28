"""Either monad — typed error handling.

Either[E, A] = Right(a) | Left(e). Right-biased.

Examples:
    >>> from funstruct.monad.either import Either, Right, Left
    >>> Right(10).map(lambda x: x + 1)
    Right(11)
    >>> Left("err").map(lambda x: x + 1)
    Left('err')
    >>> Right(10).bind(lambda x: Right(x * 2))
    Right(20)
    >>> Left("err").bind(lambda x: Right(x * 2))
    Left('err')

    or_else — recover from Left:

    >>> Left("err").or_else(lambda e: Right("default"))
    Right('default')
    >>> Right(10).or_else(lambda e: Right("default"))
    Right(10)

    do-notation:

    >>> def pipeline():
    ...     x = yield Right(1)
    ...     y = yield Right(x + 10)
    ...     return x + y
    >>> Either.do(pipeline)
    Right(12)
"""

from _funstruct._either import *  # noqa: F403
