"""
Validated: applicative error-accumulating functor.

Use Validated for independent validations.

Example::

    >>> from funstruct.applicative.validated import Validated
    >>> (Validated.valid(None)
    ...     .ap(Validated.invalid("too short"))
    ...     .ap(Validated.invalid("missing @")))
    Invalid(errors=Cons('too short', Cons('missing @', Nil())))

"""

from _funstruct._validated import *  # noqa F403
