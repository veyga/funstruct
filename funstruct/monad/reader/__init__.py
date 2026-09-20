"""Reader monad — computations that read from a shared environment.

Examples:
    >>> from funstruct.monad.reader import Reader
    >>> get_host = Reader(lambda cfg: cfg["host"])
    >>> get_port = Reader(lambda cfg: cfg["port"])
    >>> get_path = Reader(lambda cfg: cfg.get("path", "/"))
    >>> build_url = (
    ...     get_host
    ...     .bind(lambda h: get_port
    ...     .bind(lambda p: get_path
    ...     .map(lambda path: f"http://{h}:{p}{path}")))
    ... )
    >>> build_url.run({"host": "localhost", "port": 8080, "path": "/api"})
    'http://localhost:8080/api'
    >>> build_url.run({"host": "prod.co", "port": 443})
    'http://prod.co:443/'
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

from funstruct.typeclasses.mixins.data_type import DataType

_Ctx = TypeVar("_Ctx")
_A = TypeVar("_A")
_B = TypeVar("_B")


class Reader(DataType, Generic[_Ctx, _A]):
    """Reader: Ctx -> A."""

    def __init__(self, run: Callable[[_Ctx], _A]) -> None:
        self._run = run

    def run(self, ctx):
        return self._run(ctx)

    def __call__(self, ctx):
        return self.run(ctx)

    @classmethod
    def ask(cls) -> Reader:
        return cls(lambda ctx: ctx)  # type: ignore[arg-type,return-value]  # ask returns Reader[Ctx, Ctx]

    def __repr__(self) -> str:
        return f"Reader({self._run})"


import funstruct.monad.reader.instances  # noqa: E402, F401

__all__ = [
    "Reader",
]
