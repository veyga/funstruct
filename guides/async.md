# Async Operations

## The recommended approach: AsyncResult

For async code that can fail, use `AsyncResult`. It's essentially
`Future[Result[A]]` — an async computation that produces either
`Ok(value)` or `Err(exception)`.

```python
from funstruct.monad.result import AsyncResult, Ok, Err, TryAsync

# Wrap async functions that might throw
@TryAsync
async def fetch_user(id: int) -> User:
    resp = await httpx.get(f"/users/{id}")
    if resp.status_code != 200:
        raise NotFoundError(f"user {id}")
    return User(**resp.json())

# Wrap sync functions that might throw
@TryAsync
def parse_id(raw: str) -> int:
    return int(raw)

# Compose — nothing executes until await
pipeline = (
    parse_id("42")
    .bind(fetch_user)
    .map(lambda u: u.email)
)

# Await once at the boundary
result = await pipeline  # Ok("alice@example.com") or Err(...)
```

## @TryAsync — wrapping exception-throwing code

`@TryAsync` wraps both sync and async functions. Exceptions become
`Err`, return values become `Ok`:

```python
# Async function
@TryAsync
async def fetch(url: str) -> dict:
    resp = await httpx.get(url)
    return resp.json()

# Sync function (also works)
@TryAsync
def parse(raw: str) -> int:
    return int(raw)

await fetch("https://api.example.com")  # Ok({"data": ...}) or Err(...)
await parse("42")                        # Ok(42)
await parse("bad")                       # Err(ValueError(...))
```

## Do-notation for async

```python
@AsyncResult.do
def get_profile(user_id: str):
    user = yield fetch_user(user_id)
    email = yield fetch_email(user)
    prefs = yield fetch_preferences(user)
    return Profile(user, email, prefs)

result = await get_profile("alice")
```

Each `yield` awaits the `AsyncResult` and extracts the value. If any
step returns `Err`, the rest is skipped.

**Important:** `@AsyncResult.do` uses generators (`yield`), NOT
`async`/`await`. You cannot write `async def` with `@do`.

## Bind chains

For 1-2 steps, bind chains are cleaner (and ~2x faster) than do:

```python
# One step
result = await fetch_user(42).map(lambda u: u.email)

# Two steps
result = await fetch_user(42).bind(lambda u: fetch_email(u))

# >> operator is bind
result = await fetch_user(42) >> fetch_email
```

## Error handling

```python
# Recover from errors
result = await (
    fetch_user(42)
    .handle_error_with(lambda e: AsyncResult.pure(default_user))
)

# Transform errors
result = await (
    fetch_user(42)
    .left_map(lambda e: CustomError(f"user fetch failed: {e}"))
)

# Pattern match the final result
match await pipeline:
    case Ok(value):
        return value
    case Err(e):
        log.error(f"Failed: {e}")
        return fallback
```

## Creating AsyncResult values

```python
AsyncResult.pure(42)                     # Ok(42) wrapped in async
AsyncResult.raise_error(ValueError("x")) # Err wrapped in async
AsyncResult.from_result(Ok(42))          # lift sync Result
AsyncResult.from_either(Right(42))       # lift sync Either
```

## When to use which

| Type | Use for |
|------|---------|
| `Result[A]` | Sync computations that can fail |
| `AsyncResult[A]` | Async computations that can fail |
| `Future[A]` | Async computations that always succeed |
| `@Try` | Wrapping sync exception-throwing code |
| `@TryAsync` | Wrapping async (or sync) exception-throwing code |

## See also

- `demos/01_result_pipeline.py` — AsyncResult pipeline
- `demos/transformers/03_alternative.py` — all functions return AsyncResult
