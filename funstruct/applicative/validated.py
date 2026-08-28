"""Validated: applicative error-accumulating functor.

>>> from funstruct.applicative.validated import Validated, Valid, Invalid
>>> Validated.cond(True, 42, "err")
Valid(value=42)
>>> Validated.cond(False, 42, "err")
Invalid(errors=Cons('err', Nil()))
>>> Valid(1) + Valid(2)
Valid(value=(1, 2))
>>> Invalid("a:") + Invalid("b")
Invalid(errors='a:b')
"""

from _funstruct._validated import *  # noqa F403
