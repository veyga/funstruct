# Monad

::: funstruct.typeclasses.Monad

## Do-notation

Haskell and Scala have built-in `do`/`for` syntax that flattens nested
`bind` chains into sequential-looking code. Python doesn't, but generators
give us something close.

Every monad in funstruct provides a `do` classmethod that accepts a
**zero-argument generator function**. Each `yield` unwraps a monadic value;
the final `return` is wrapped back into the monad.

### Basic usage

Without do-notation, chaining multiple steps requires nested lambdas:

```python
from funstruct.monad.either import Either, Right, Left

result = (
    Right(1)
    .bind(lambda x: Right(x + 10)
    .bind(lambda y: Right(x + y)))
)
# Right(12)
```

With do-notation, the same logic reads top-to-bottom:

```python
def pipeline():
    x = yield Right(1)
    y = yield Right(x + 10)
    return x + y

Either.do(pipeline)  # Right(12)
```

Each `yield` is equivalent to a `bind` — it unwraps the value if the
computation succeeds, or short-circuits if it doesn't (e.g., `Left`,
`Nothing`, depending on the monad).

### The zero-argument rule

`do` always takes a **zero-argument function**. This is because Python
generators are single-use — `do` calls `gen_fn()` internally to create the
generator and drives it to completion.

If your pipeline needs arguments, wrap the generator in a regular function
and close over them:

```python
from funstruct.monad.option import Option, Some, Nothing

def lookup(user_id: int) -> Option[str]:
    @Option.do
    def _run():
        user = yield find_user(user_id)      # user_id from closure
        email = yield get_email(user)
        return email

    return _run
```

### As a decorator

You can also use `do` as a decorator. The decorated function becomes the
result (not a callable), so this works best for module-level definitions or
inside a function that returns the result:

```python
from funstruct.monad.state import State

inc = State(lambda s: (s + 1, s))
get = State(lambda s: (s, s))

@State.do
def count_to_three():
    a = yield inc
    b = yield inc
    c = yield inc
    total = yield get
    return (a, b, c, total)

count_to_three.run(0)  # (3, (0, 1, 2, 3))
```

### Short-circuiting

Each monad's `do` knows how to short-circuit according to its semantics:

```python
from funstruct.monad.option import Option, Some, Nothing

def pipeline():
    x = yield Some(1)
    y = yield Nothing()   # short-circuits here
    return x + y          # never reached

Option.do(pipeline)  # Nothing()
```

```python
from funstruct.monad.either import Either, Right, Left

def pipeline():
    x = yield Right(1)
    y = yield Left("boom")   # short-circuits here
    return x + y              # never reached

Either.do(pipeline)  # Left("boom")
```

### Monad transformers

Monad transformers also support do-notation. The short-circuiting respects
both layers:

```python
from funstruct.monad.either import Right, Left
from funstruct.monad.option import Some, Nothing
from funstruct.monadtransformer.either_t import EitherT

@EitherT.do
def pipeline():
    x = yield EitherT(Some(Right(1)))
    y = yield EitherT(Some(Right(x + 10)))
    return x + y

pipeline.run()  # Some(Right(12))
```

### Future (async)

`Future.do` uses a regular (sync) generator — not `async def`. The driver
loop handles awaiting internally. Using `async def` with `yield` creates an
async generator, which Python forbids from returning a value.

```python
from funstruct.monad.future import Future

def fetch_and_transform(url: str) -> Future[str]:
    @Future.do
    def _run():
        response = yield fetch(url)       # yield awaits the Future
        parsed = yield parse(response)
        return parsed.title

    return _run

# await at the boundary
result = await fetch_and_transform("https://example.com")
```

### CList (the exception)

`CList.do` exists but cannot express list-monad nondeterminism. The list
monad needs to replay the generator body once per element (exploring all
combinations), but Python generators are single-use. Use explicit `.bind()`
chains instead:

```python
from funstruct.collections.cons import CList, Cons, Nil

xs = CList.from_iterable([1, 2])
ys = CList.from_iterable(["a", "b"])

result = xs.bind(lambda x: ys.map(lambda y: (x, y)))
# CList([(1, "a"), (1, "b"), (2, "a"), (2, "b")])
```
