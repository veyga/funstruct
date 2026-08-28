"""Result — Either specialized for error handling.

Result = Either, Ok = Right, Err = Left.
AsyncResult = Future (specialized for E = Exception).
Try wraps sync functions, TryAsync wraps async functions.
"""

from collections.abc import Callable
from functools import wraps

from _funstruct._either import Either as Result
from _funstruct._either import Left as Err
from _funstruct._either import Right as Ok
from _funstruct._future import Future as AsyncResult
from _funstruct._future import TryAsync


def Try(f: Callable) -> Callable:
    """Decorator: wraps a sync function so exceptions become Err.

    >>> @Try
    ... def divide(a, b):
    ...     return a / b
    >>> divide(10, 2)
    Right(5.0)
    >>> divide(10, 0)  # doctest: +ELLIPSIS
    Left(ZeroDivisionError(...))
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return Ok(f(*args, **kwargs))
        except Exception as e:
            return Err(e)

    return wrapper


__all__ = ["Result", "Ok", "Err", "Try", "AsyncResult", "TryAsync"]
