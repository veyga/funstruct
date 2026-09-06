# MonadTransformer

> **Experimental** — this API is alpha and may change.

> **Note:** MonadTransformer is not a typeclass in Haskell or Scala — it's
> a design pattern. In funstruct, it's implemented as a base class for
> convenience, using the same mechanism as the real typeclasses (Functor,
> Applicative, Monad).

::: funstruct.typeclasses.MonadTransformer

## Overview

A monad transformer wraps one monad inside another, combining their effects
into a single flat pipeline. Without transformers, nested monads require
manual unwrapping at every step.

### Primitives

Every transformer must implement:

- **`pure(value, monad)`** — lift a value into the transformer
- **`bind(f)`** — chain computations (inherited from Monad)
- **`lift_f(inner)`** — lift an inner monad value into the transformer
- **`run()`** — unwrap the transformer to access the inner structure

### Unwrapping with `.run()`

Transformers add a layer of wrapping. Use `.run()` at the boundary to
unwrap back to the inner monad:

```python
from funstruct.monadtransformer.option_t import OptionT
from funstruct.monad.either import Right

# Build a pipeline inside the transformer:
result = (
    OptionT(Right(Some(1)))
    .bind(lambda x: OptionT(Right(Some(x + 10))))
)

# Unwrap at the boundary:
result.run()  # Right(Some(11))
```

For async transformers wrapping `Future`, chain `.run()` with `await`:

```python
result = await my_option_t_pipeline.run()  # Option[A]
```

Each transformer's `.run()` returns a different shape:

| Transformer | `.run()` returns |
|---|---|
| `OptionT` | `F[Option[A]]` |
| `EitherT` | `F[Either[E, A]]` |
| `WriterT` | `F[(A, W)]` |
| `StateT` | `S → F[(S, A)]` (call with initial state) |
| `ReaderT` | `Ctx → F[A]` (call with context) |

`StateT` and `ReaderT` take an argument: `state_t.run(initial_state)`,
`reader_t.run(context)`.
