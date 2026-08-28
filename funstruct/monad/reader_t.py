"""ReaderT — reader monad transformer over any monad.

**ReaderT** — shared environment + inner monad's effects (failure, state, etc.)

```python
ReaderT[F, Ctx, A]  =  Ctx -> F[A]
```

bind: chain computations that share context, any can fail.
and_then: pipe output forward as the next context (Kleisli composition).

Examples:
    >>> from funstruct.monad.reader_t import ReaderT
    >>> from returns.result import Result, Success, Failure

    bind — shared context, with failure:

    >>> get_db = ReaderT(lambda cfg: (
    ...     Result.from_value(cfg["db"]) if "db" in cfg
    ...     else Result.from_failure("missing db")))
    >>> validate = lambda url: ReaderT(lambda cfg: (
    ...     Result.from_value(url) if url.startswith("postgres://")
    ...     else Result.from_failure(f"bad url: {url}")))
    >>> connect = lambda url: ReaderT(lambda cfg: (
    ...     Result.from_value(f"{url} as {cfg['user']}")))
    >>> pipeline = (
    ...     get_db
    ...     .bind(validate)
    ...     .bind(connect)
    ... )
    >>> pipeline.run({"db": "postgres://localhost/app", "user": "admin"})
    <Success: postgres://localhost/app as admin>
    >>> pipeline.run({"db": "mysql://bad", "user": "admin"})
    <Failure: bad url: mysql://bad>

    and_then — output feeds as next input, short-circuits on failure:

    >>> parse_int = ReaderT(lambda s: (
    ...     Result.from_value(int(s)) if s.isdigit()
    ...     else Result.from_failure(f"not a number: {s}")))
    >>> double = ReaderT(lambda n: Result.from_value(n * 2))
    >>> to_str = ReaderT(lambda n: Result.from_value(str(n)))
    >>> pipeline = (
    ...     parse_int
    ...     .and_then(double)
    ...     .and_then(to_str)
    ... )
    >>> pipeline.run("21")
    <Success: 42>
    >>> pipeline.run("abc")
    <Failure: not a number: abc>
"""

from _funstruct._reader_t import *  # noqa F403
