# funstruct

A small, helpful collection of functional utilities.

(These are not meant to be highly performant, but are useful for smaller datasets)

Like all functional stuctures, they play very well with recursive algos, and compose
quit well

### Install

Install like any PyPI package:</br> `pip install funstruct`, `uv add funstruct`, ...

###

```python
from funstruct import tailrec
from funstruct.collections import Cons, FrozenDict
from funstruct.monad import State, StateT, ReaderT
from funstruct.applicative import Validated, Valid, Invalid, map_n
from funstruct.typeclass import Semigroup
```

## Functional Primer

TODO

### Type Class Diagrams

**Functor** — transform the value inside a context

```
F[A] ---( f: A -> B )---> F[B]
```

**Monad** — sequence computations that produce new contexts

```
F[A] ---( f: A -> F[B] )---> F[B]
```

**Applicative** — combine independent computations

```
F[A] ─┐
       ├──> F[(A, B)]
F[B] ─┘
```

**Semigroup** — associative combine (any type with `+`)

```
A ─┐
    ├──( + )──> A
A ─┘
```

**Monoid** — semigroup with an identity element

```
A ─┐
    ├──( + )──> A       (+ identity = A)
A ─┘
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup.
