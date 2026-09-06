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

from funstruct.typeclasses._dot_notation import DotNotation

_Ctx = TypeVar("_Ctx")
_A = TypeVar("_A")
_B = TypeVar("_B")


class Reader(DotNotation, Generic[_Ctx, _A]):
    """Reader: Ctx -> A."""

    def __init__(self, run: Callable[[_Ctx], _A]) -> None:
        self._run = run

    def run(self, ctx):
        return self._run(ctx)

    def __call__(self, ctx):
        return self.run(ctx)

    def bind(self, f: Callable[[_A], Reader[_Ctx, _B]]) -> Reader[_Ctx, _B]:
        return Reader(lambda ctx: f(self._run(ctx)).run(ctx))

    @classmethod
    def do(cls, gen_fn: Callable) -> Callable[..., Reader]:
        """Do-notation via generators. Returns a callable.

        >>> def pipeline():
        ...     x = yield Reader(lambda ctx: ctx["x"])
        ...     y = yield Reader(lambda ctx: ctx["y"])
        ...     return x + y
        >>> Reader.do(pipeline)().run({"x": 1, "y": 10})
        11
        """
        def _thunk(*args, **kwargs):
            def _run(ctx):
                gen = gen_fn(*args, **kwargs)
                try:
                    monadic_val = next(gen)
                    while True:
                        result = monadic_val.run(ctx)
                        monadic_val = gen.send(result)
                except StopIteration as e:
                    return e.value
            return cls(_run)
        return _thunk

    @classmethod
    def pure(cls, value, *args, **kwargs) -> Reader:
        return cls(lambda _: value)

    @classmethod
    def ask(cls) -> Reader:
        return cls(lambda ctx: ctx)

    def __repr__(self) -> str:
        return f"Reader({self._run})"


Reader._type_constructor = Reader

import funstruct.monad.reader_instances  # noqa: E402, F401

__all__ = [
    "Reader",
]
