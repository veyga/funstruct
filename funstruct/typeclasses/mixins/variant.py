"""@variant — decorator for ADT variant classes.

Applies @final + @dataclass(frozen=True, eq=False, repr=False).
Eq, Representable, Stringable, and Truthable are handled by typeclass instances,
not by dataclass auto-generation.

Note: type checkers only enforce @final when used as a decorator, not
when called as a function. For static enforcement, use @final and
@dataclass separately:

    @final
    @dataclass(frozen=True, eq=False, repr=False)
    class Ok(Result[_A]):
        value: _A
"""

from __future__ import annotations

from dataclasses import dataclass


def variant(cls):
    """Seal and freeze an ADT variant. No auto __eq__, __repr__, or __bool__."""
    cls = dataclass(frozen=True, eq=False, repr=False)(cls)
    cls.__final__ = True  # runtime marker (type checkers won't enforce)
    return cls


__all__ = ["variant"]
