"""Alternative — an Applicative with a monoidal choice structure.

empty:   the identity / zero value
or_else: try fa, if it fails/is empty try fb
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from funstruct.typeclasses.applicative import Applicative


class Alternative(Applicative):
    """empty + or_else."""

    @abstractmethod
    def empty(self) -> Any: ...

    @abstractmethod
    def or_else(self, fa, fb) -> Any: ...


__all__ = ["Alternative"]
