"""Alternative — an Applicative with a monoidal choice structure.

empty       — the identity / zero value
or_else(fb) — try fa, if it fails/is empty try fb

Scala/Cats: ``trait Alternative[F[_]] extends Applicative[F]``
Haskell:    ``class Applicative f => Alternative f``

Instances: Option, CList.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import TypeVar

from funstruct.typeclasses._applicative import Applicative

_A = TypeVar("_A")


class Alternative(Applicative[_A]):
    """Applicative with choice: empty + or_else."""

    @classmethod
    @abstractmethod
    def empty(cls) -> Alternative[_A]:
        """The zero/identity value. Nothing() for Option, Nil() for CList."""
        ...

    @abstractmethod
    def or_else(fa: Alternative[_A], fb: Alternative[_A]) -> Alternative[_A]:
        """Try fa, if it fails/is empty, use fb instead."""
        ...


__all__ = [
    "Alternative",
]
