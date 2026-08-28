"""Result — aliases for Either with domain-oriented naming.

Result[E, A] = Ok(a) | Err(e)

Same type as Either, just clearer names for error-handling contexts.
"""

from _funstruct._either import Either as Result
from _funstruct._either import Left as Err
from _funstruct._either import Right as Ok
from _funstruct._either import Try

__all__ = ["Result", "Ok", "Err", "Try"]
