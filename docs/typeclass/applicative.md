# Applicative

::: funstruct.typeclasses.Applicative

## Overview

An Applicative combines independent computations in context. It provides
three operations:

- **`pure(value)`** — lift a plain value into the context
- **`ap(other)`** — apply a wrapped function to a wrapped value: `F[A → B].ap(F[A]) → F[B]`
- **`product(other)`** — combine two values into a tuple: `F[A].product(F[B]) → F[(A, B)]`

The `*` operator is an alias for `product`:

```python
Some(1) * Some(2)       # Some((1, 2))
Some(1) * Nothing()     # Nothing()
```

### ap vs product

`ap` applies a **wrapped function** to a wrapped value:

```python
Some(lambda x: x + 1).ap(Some(2))  # Some(3)
```

`product` combines two wrapped **values** into a tuple:

```python
Some(1).product(Some(2))  # Some((1, 2))
Some(1) * Some(2)         # same thing
```

`product` is derived from `map` + `ap`:
`fa.product(fb) == fa.map(lambda a: lambda b: (a, b)).ap(fb)`

### Applicative vs Monad

With `Applicative`, computations are **independent** — later values can't
depend on earlier results. This enables parallel execution and error
accumulation.

With `Monad`, computations are **sequential** — each step can depend on the
previous result via `bind`.

Every `Monad` is an `Applicative`, but not every `Applicative` is a `Monad`.
`Validated` is the key example: it accumulates errors independently (applicative),
but cannot sequence dependent computations (not a monad).
