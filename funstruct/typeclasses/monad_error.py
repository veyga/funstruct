"""MonadError — a Monad that can raise and handle typed errors.

pure(a)                — put a value ON the success rail
raise_error(e)         — put a value ON the error rail
bind(f)                — continue along the success rail
handle_error_with(f)   — recover FROM the error rail
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from typing import Any

from funstruct.typeclasses.monad import Monad


class MonadError(Monad):
    """raise_error + handle_error_with."""

    @abstractmethod
    def raise_error(self, error) -> Any: ...

    @abstractmethod
    def handle_error_with(self, fa, f: Callable[[Any], Any]) -> Any: ...


__all__ = ["MonadError"]
