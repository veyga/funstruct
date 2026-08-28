"""Converters between funstruct types.

Examples:
    >>> from funstruct.converters import option_to_result, result_to_option
    >>> from funstruct.monad.option import Some, Nothing
    >>> from funstruct.monad.result import Ok, Err

    >>> option_to_result(Some(42), "was empty")
    Right(42)
    >>> option_to_result(Nothing(), "was empty")
    Left('was empty')

    >>> result_to_option(Ok(42))
    Some(42)
    >>> result_to_option(Err("failed"))
    Nothing()
"""

from funstruct.monad.either import Left, Right
from funstruct.monad.option import Nothing, Option, Some


def option_to_result(opt: Option, error):
    """Convert Option to Result — Some(v) → Ok(v), Nothing → Err(error).

    >>> from funstruct.monad.option import Some, Nothing
    >>> option_to_result(Some(1), "missing")
    Right(1)
    >>> option_to_result(Nothing(), "missing")
    Left('missing')
    """
    match opt:
        case Some(v):
            return Right(v)
        case _:
            return Left(error)


def result_to_option(result):
    """Convert Result/Either to Option — Ok(v) → Some(v), Err(_) → Nothing.

    >>> from funstruct.monad.result import Ok, Err
    >>> result_to_option(Ok(1))
    Some(1)
    >>> result_to_option(Err("failed"))
    Nothing()
    """
    match result:
        case Right(v):
            return Some(v)
        case _:
            return Nothing()


__all__ = ["option_to_result", "result_to_option"]
