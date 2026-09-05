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
result = await option_t.run()  # Future[Option[A]] → Option[A]
```

## Do-notation with Future

`Future.do` uses a regular generator (**not `async def`**). The driver loop
awaits each yielded `Future` internally. Using `async def` with `yield`
creates an async generator, which Python forbids from returning a value.

### Passing arguments

Define a generator that takes parameters and call `Future.do` with args:

```python
from funstruct.monad.future import Future

def get_city(username):
    user = yield get_user(username)
    address = yield get_address(user)
    return address.street

# Call with arguments:
result = await Future.do(get_city, "alice")
```

Wrap it in a function for a reusable API:

```python
def get_city(username: str) -> Future[str]:
    return Future.do(__get_city, username)

def __get_city(username: str):
    user = yield get_user(username)
    address = yield get_address(user)
    return address.street

result = await get_city("alice")  # "avalon"
```

### As a decorator (zero-arg only)

`@Future.do` runs immediately, so the generator cannot take arguments.
This works for pipelines with no parameters:

```python
@Future.do
def startup():
    config = yield load_config()
    db = yield connect(config)
    return db

db = await startup
```

**This does not work** — the decorator calls `city()` with no args at
definition time:

```python
@Future.do  # TypeError: city() missing argument 'username'
def city(username: str):
    user = yield get_user(username)
    ...
```

### Baking in arguments at definition time

`Future.do(gen_fn, args)` returns a `Future`, not a function. The arguments
are captured when `do` is called:

```python
def __get_city(username):
    user = yield get_user(username)
    address = yield get_address(user)
    return address.street

# This is a Future[str], not a function — "andrew" is baked in:
andrew_city: Future[str] = Future.do(__get_city, "andrew")

result = await andrew_city  # not andrew_city("andrew")
```
