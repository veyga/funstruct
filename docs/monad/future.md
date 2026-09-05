# Future

::: funstruct.monad.future

## Awaiting

`Future` and `AsyncResult` are directly awaitable — no `.run()` needed:

```python
result = await Future.pure(42)         # 42
result = await AsyncResult.pure(42)    # Ok(42)
```

This is different from monad transformers (`OptionT`, `EitherT`, etc.) which
require `.run()` to unwrap the transformer layer before awaiting:

```python
result = await option_t_pipeline().run()  # Future[Option[A]] → Option[A]
```

## Do-notation with Future

`Future.do` uses a regular generator (**not `async def`**). The driver loop
awaits each yielded `Future` internally. Using `async def` with `yield`
creates an async generator, which Python forbids from returning a value.

`do` returns a **callable** — call it with `()` to execute:

```python
from funstruct.monad.future import Future

@Future.do
def fetch_and_transform(url):
    response = yield fetch(url)
    parsed = yield parse(response)
    return parsed.title

result = await fetch_and_transform("https://example.com")
```

Without the decorator:

```python
result = await Future.do(fetch_and_transform)("https://example.com")
```

## Do-notation with AsyncResult

`AsyncResult.do` works the same way, but short-circuits on `Err`. It also
accepts sync `Either` values (Ok/Err) alongside `AsyncResult`:

```python
from funstruct.monad.result import AsyncResult, TryAsync

@TryAsync
def get_user(name):
    ...

@AsyncResult.do
def get_nickname(username):
    user = yield get_user(username)
    age = yield get_age(user)
    nickname = yield get_nickname_from_db(user)
    return f"{nickname}{age}"

result = await get_nickname("me")  # Ok("andrew3000") or Err(...)
```
