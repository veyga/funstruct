"""ReaderT — reader monad transformer over any monad.

**ReaderT** — shared environment + inner monad's effects (failure, state, etc.)

```python
ReaderT[F, Ctx, A]  =  Ctx -> F[A]
```

bind: chain computations that share context, any can fail.
and_then: pipe output forward as the next context (Kleisli composition).

Examples:
    >>> from funstruct.monadtransformer import ReaderT
    >>> from funstruct.monad import Either, Right, Left

    bind — shared context, with failure:

    >>> get_db = ReaderT(lambda cfg: (
    ...     Right(cfg["db"]) if "db" in cfg
    ...     else Left("missing db")))
    >>> validate = lambda url: ReaderT(lambda cfg: (
    ...     Right(url) if url.startswith("postgres://")
    ...     else Left(f"bad url: {url}")))
    >>> connect = lambda url: ReaderT(lambda cfg: (
    ...     Right(f"{url} as {cfg['user']}")))
    >>> pipeline = (
    ...     get_db
    ...     .bind(validate)
    ...     .bind(connect)
    ... )
    >>> pipeline.run({"db": "postgres://localhost/app", "user": "admin"})
    Right('postgres://localhost/app as admin')
    >>> pipeline.run({"db": "mysql://bad", "user": "admin"})
    Left('bad url: mysql://bad')

    and_then — output feeds as next input, short-circuits on failure:

    >>> parse_int = ReaderT(lambda s: (
    ...     Right(int(s)) if s.isdigit()
    ...     else Left(f"not a number: {s}")))
    >>> double = ReaderT(lambda n: Right(n * 2))
    >>> to_str = ReaderT(lambda n: Right(str(n)))
    >>> pipeline = (
    ...     parse_int
    ...     .and_then(double)
    ...     .and_then(to_str)
    ... )
    >>> pipeline.run("21")
    Right('42')
    >>> pipeline.run("abc")
    Left('not a number: abc')
"""

from _funstruct._reader_t import *  # noqa F403
