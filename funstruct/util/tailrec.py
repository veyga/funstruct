"""Trampoline-based tail recursion.

Examples:
    >>> from funstruct.util.tailrec import tco, tail_call
    >>> @tco
    ... def sum_up_to(n, acc=0):
    ...     if n == 0:
    ...         return acc
    ...     return tail_call(sum_up_to)(n - 1, acc + n)
    >>> sum_up_to(100)
    5050
"""

from _funstruct._tailrec import tail_call as tail_call
from _funstruct._tailrec import tco as tco
