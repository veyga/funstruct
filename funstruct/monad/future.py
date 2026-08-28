"""Future — lazy async computation that may fail.

Future[E, A] wraps an awaitable that produces Either[E, A].
Compose pipelines without await, execute once at the boundary.

Examples:
    >>> import asyncio
    >>> from funstruct.monad.future import Future, TryAsync
    >>> from funstruct.monad.either import Right, Left

    Build a pipeline — no await until the end:

    >>> async def fetch_user(id):
    ...     if id == 1:
    ...         return {"name": "alice"}
    ...     raise ValueError(f"not found: {id}")

    >>> pipeline = (
    ...     Future.from_coroutine(fetch_user(1))
    ...     .map(lambda u: u["name"].upper())
    ... )
    >>> asyncio.run(pipeline._awaitable())
    Right('ALICE')

    >>> failed = Future.from_coroutine(fetch_user(99))
    >>> asyncio.run(failed._awaitable())  # doctest: +ELLIPSIS
    Left(ValueError('not found: 99'))

    @TryAsync decorator:

    >>> @TryAsync
    ... async def safe_fetch(id):
    ...     if id == 1:
    ...         return {"name": "alice"}
    ...     raise ValueError(f"not found: {id}")
    >>> asyncio.run(safe_fetch(1)._awaitable())
    Right({'name': 'alice'})
    >>> asyncio.run(safe_fetch(99)._awaitable())  # doctest: +ELLIPSIS
    Left(ValueError('not found: 99'))
"""

from _funstruct._future import Future as Future
from _funstruct._future import TryAsync as TryAsync
