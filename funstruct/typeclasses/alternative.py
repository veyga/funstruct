"""Alternative — an Applicative with a monoidal choice structure.

empty:   the identity / zero value
or_else: try fa, if it fails/is empty try fb
"""

from __future__ import annotations

from abc import abstractmethod

from funstruct.typeclasses.applicative import Applicative


class Alternative(Applicative):
    """empty + or_else."""

    @abstractmethod
    def empty(self) -> object: ...

    @abstractmethod
    def or_else(self, fa, fb) -> object: ...


__all__ = ["Alternative"]
