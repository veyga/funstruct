"""Result — Either with domain-oriented naming.

Result[E, A] = Ok(a) | Err(e). Same type as Either, clearer names.

Examples:
    >>> from funstruct.monad.result import Result, Ok, Err, Try
    >>> Ok(10).map(lambda x: x + 1)
    Right(11)
    >>> Err("bad").map(lambda x: x + 1)
    Left('bad')
    >>> Ok(10).bind(lambda x: Ok(x * 2))
    Right(20)

    or_else — recover from Err:

    >>> Err("bad").or_else(lambda e: Ok("default"))
    Right('default')

    @Try decorator:

    >>> @Try
    ... def safe_div(a, b):
    ...     return a / b
    >>> safe_div(10, 2)
    Right(5.0)
    >>> safe_div(10, 0)  # doctest: +ELLIPSIS
    Left(ZeroDivisionError(...))

    do-notation:

    >>> def pipeline():
    ...     x = yield Ok(1)
    ...     y = yield Ok(x + 10)
    ...     return x + y
    >>> Result.do(pipeline)
    Right(12)
"""

from _funstruct._result import *  # noqa: F403
