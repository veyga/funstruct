# funstruct

A zero-dependency functional programming library for Python.

## Install

```bash
pip install funstruct || uv add funstruct
```

## Functional Primer

### Type Class Hierarchy

```
Semigroup     Bifunctor     Foldable      Functor
    │                        \       /       │
 Monoid                   Traversable    Applicative
                                        /         \
                                   Alternative    Monad
                                                    │
                                                MonadError
```

#### Diagrams

**Semigroup** — associative combine (`+` being the canonical 'combine' operation)

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

**Functor** — transform the value inside a context

```
F[A] ---( f: A -> B )---> F[B]
```

**Applicative** — apply a function in context to a value in context

```
F[A → B]  ─┐
           ├──ap──> F[B]
F[A] ──────┘
```

**Monad** — sequence computations that produce new contexts

```
F[A] ---( f: A -> F[B] )---> F[B]
```

Heavily influenced by [Scalaz](https://github.com/scalaz/scalaz) and
[Cats](https://typelevel.org/cats/).

```python
# Signatures shown in Python 3.12+ syntax for clarity.
# The library supports Python ≥3.10 for now

# Value-level typeclasses (not inherited — instantiated per type)
@dataclass(frozen=True)
class Semigroup[A]:
    typ: type
    combine: Callable[[A, A], A]

@dataclass(frozen=True)
class Monoid[A](Semigroup[A]):
    empty: A  # identity element

# Type-level hierarchy (inherited by data types)
class Functor[A](ABC):
    def map(fa: Functor[A], f) -> Functor[B]: ...              # abstract

class Applicative[A](Functor[A]):
    def pure(cls, value: A) -> Applicative[A]: ...             # abstract @final on concrete types
    def ap(
        ff: Applicative[Callable[[A], B]],
        fa: Applicative[A],
    ) -> Applicative[B]: ...                                   # abstract
    def map(fa: Applicative[A], f) -> Applicative[B]: ...      # derived: pure(f).ap(fa)
    def product(
        fa: Applicative[A],
        fb: Applicative[B],
    ) -> Applicative[tuple[A, B]]: ...
    __mul__ = product                                          # * operator

class Alternative[A](Applicative[A]):
    def empty(cls) -> Alternative[A]: ...                      # abstract
    def or_else(fa: Alternative[A], fb: Alternative[A]) -> Alternative[A]: ...  # abstract

class Monad[A](Applicative[A]):
    def bind(fa: Monad[A], f) -> Monad[B]: ...                 # abstract
    def do(cls, gen_fn) -> Callable[..., Monad[A]]: ...        # abstract
    def map(fa: Monad[A], f) -> Monad[B]: ...                  # @final: bind + pure
    def ap(
        ff: Monad[Callable[[A], B]],
        fa: Monad[A],
    ) -> Monad[B]: ...                                         # @final: bind + map
    def then(fa: Monad[A], fb: Monad[B]) -> Monad[B]: ...     # derived: bind
    def map2(fa: Monad[A], fb: Monad[B], f) -> Monad[C]: ...  # derived: bind + map
    __rshift__ = bind                                          # >> operator

class MonadError[A](Monad[A]):
    def raise_error(cls, error: E) -> MonadError[A]: ...       # abstract
    def handle_error_with(
        fa: MonadError[A], f,
    ) -> MonadError[A]: ...                                    # abstract

# Standalone — maps over two type parameters (not part of Functor)
class Bifunctor[A, B](ABC):
    def bimap(fa: Bifunctor[A, B], f, g) -> Bifunctor[C, D]: ...  # abstract
    def left_map(fa: Bifunctor[A, B], f) -> Bifunctor[C, B]: ...  # derived: bimap(f, id)

# Separate hierarchy (experimental)
# MT = MonadTransformer for brevity
class MonadTransformer[F, A](ABC):
    def bind(fa: MT[F, A], f) -> MT[F, B]: ...                 # abstract
    def map(fa: MT[F, A], f) -> MT[F, B]: ...                  # abstract
    def pure(cls, value: A, monad: type[F]) -> MT[F, A]: ...   # abstract
    def lift_f(cls, inner: F[A]) -> MT[F, A]: ...              # abstract
    def do(cls, gen_fn) -> Callable[..., MT[F, A]]: ...        # abstract
    def ap(
        ff: MT[F, Callable[[A], B]],
        fa: MT[F, A],
    ) -> MT[F, B]: ...                                         # derived: bind + map
    def then(fa: MT[F, A], fb: MT[F, B]) -> MT[F, B]: ...     # derived: bind
    def product(
        fa: MT[F, A],
        fb: MT[F, B],
    ) -> MT[F, tuple[A, B]]: ...                               # derived: map + ap
    __mul__ = product                                          # * operator
    __rshift__ = bind                                          # >> operator
```

### Implementations

| Typeclass        | Implementations                                                           |
| ---------------- | ------------------------------------------------------------------------- |
| Functor          | Tree, frozendict, + all below                                             |
| Bifunctor        | Either, Result, Validated                                                  |
| Traversable      | CList, Tree                                                               |
| Applicative      | Validated, ZipList, + all below                                           |
| Alternative      | Option, CList                                                              |
| Monad            | Option, Either, Result, State, Reader, Writer, CList, Future, AsyncResult |
| MonadError       | Either, Result, AsyncResult                                                |
| MonadTransformer | ReaderT, StateT, EitherT, OptionT, WriterT                                |

| Type               | What it models                                  |
| ------------------ | ----------------------------------------------- |
| `Option[A]`        | Value might not exist                           |
| `Either[E, A]`     | Value or typed error                            |
| `Result[A]`        | Computation that can fail (`Ok`/`Err`) + `@Try` |
| `AsyncResult[A]`   | Async computation that can fail + `@TryAsync`   |
| `State[S, A]`      | Stateful computation                            |
| `Reader[Ctx, A]`   | Shared environment                              |
| `Writer[W, A]`     | Accumulated output                              |
| `Validated[E, A]`  | Error accumulation (applicative, not monad)     |
| `Future[A]`        | Lazy async computation                          |
| `CList[A]`         | Persistent singly-linked list                   |
| `Tree[A]`          | Immutable binary tree (functor only)            |
| `frozendict[K, V]` | Persistent HAMT dictionary                      |

### Laws

Every implementation must satisfy these mathematical laws:

**Semigroup**

- Associativity: `(a + b) + c == a + (b + c)`

**Monoid**

- Left identity: `empty + a == a`
- Right identity: `a + empty == a`

**Functor**

- Identity: `fa.map(id) == fa`
- Composition: `fa.map(f).map(g) == fa.map(g ∘ f)`

**Applicative**

- Identity: `pure(id).ap(v) == v`
- Homomorphism: `pure(f).ap(pure(x)) == pure(f(x))`
- Interchange: `u.ap(pure(y)) == pure(λf. f(y)).ap(u)`
- Composition: `pure(∘).ap(u).ap(v).ap(w) == u.ap(v.ap(w))`
- Type preservation: `pure`, `map`, `ap` return the correct concrete type

**Monad**

- Left identity: `pure(a).bind(f) == f(a)`
- Right identity: `m.bind(pure) == m`
- Associativity: `m.bind(f).bind(g) == m.bind(λx. f(x).bind(g))`
- Type preservation: `pure`, `map`, `bind`, `ap` return the correct concrete type

## Why no IO type?

In Haskell, `IO` exists because the language is purely functional — there is
no way to perform side effects without wrapping them in the `IO` monad. The
type system enforces purity: if a function doesn't return `IO`, it cannot
touch the network, filesystem, or mutable state.

Python has no such constraint. Any function can perform side effects at any
time. An `IO` wrapper in Python would be:

1. **Unenforceable** — nothing stops you from doing I/O outside the wrapper.
   The type system can't prevent `print()` in a "pure" function.
1. **Purely ceremonial** — it adds a wrapper you must manually construct and
   unwrap, but provides no guarantee. It's a comment dressed as a type.
1. **Redundant with async** — Python's `async/await` already separates
   "description of a computation" from "execution of that computation,"
   which is most of what `IO` provides in Haskell.

Instead, funstruct provides:

- **`Either[E, A]`** / **`Result[A]`** — for operations that might fail
- **`Future[A]`** / **`AsyncResult[A]`** — for async operations (with or without error handling)
- **`@Try` / `@TryAsync`** — for wrapping exception-throwing code at boundaries

These give you the composition benefits of monadic pipelines where they
matter (error handling, async sequencing) without pretending Python is
something it isn't.

## Why no higher-kinded types?

In Haskell and Scala, higher-kinded types (HKTs) let you abstract over type
constructors — writing one generic `sequence` that works for any
`Traversable` + `Applicative` combination, or a single `Monad` interface
that a type checker can verify at call sites.

Python's type system does not support HKTs, and there is no indication it
will. Other Python FP libraries have attempted to encode them using Protocol
and TypeVar tricks, but the result is fragile, confuses type checkers, and
makes the library harder to use than the patterns it's trying to simplify.

funstruct takes a different approach: typeclasses are base classes, and
concrete types inherit from them (`Option` extends `Monad`, `Either`
extends `MonadError + Bifunctor`). This means:

- Each type provides its own `sequence`, `traverse`, and `do` rather than
  one polymorphic function that works for all types.
- Tagless final programs (see `playground/mt8.py`, `mt9.py`) are
  structurally typed — the type checker won't verify that `F` satisfies
  `MonadError` at the protocol level.

The tradeoff is a small amount of method duplication across types, in
exchange for a library that works with standard Python tooling. This library
does not aim to be "Pythonic" — it intentionally adopts FP conventions like
`fa`/`ff`/`fb` parameters and Cats-style naming — but it also does not
break the rules of the language or require compiler plugins.

## Experimental

Experimental modules live in `funstruct.experimental`. APIs may change.

### Monad Transformers

```python
from funstruct.experimental.monadtransformer import (
    ReaderT, StateT, EitherT, OptionT, WriterT,
)
```

Transformers combine effects by wrapping one monad inside another.
For most use cases, plain monads with `do`-notation and `fold` are
sufficient. Reach for transformers only when you need to combine
multiple effects in a single pipeline.

```
ReaderT[F, Ctx, A]  =  Ctx -> F[A]         (environment + F's effects)
StateT[F, S, A]     =  S -> F[(S, A)]      (state + F's effects)
EitherT[F, E, A]    =  F[Either[E, A]]     (errors + F's effects)
OptionT[F, A]       =  F[Option[A]]        (absence + F's effects)
WriterT[F, W, A]    =  F[(A, W)]           (output + F's effects)
```

### Optics (Lenses)

```python
from funstruct.experimental.optics import Lens, at
from funstruct.collections.frozendict import frozendict
```

Lenses let you read and update deeply nested immutable structures
without manually rebuilding the path at every level.

```python
config = frozendict({
    "app": {
        "users": {
            "alice": {"email": "alice@old.com", "role": "admin"},
        },
        "settings": {"version": 2},
    },
})

email_lens = at("app") >> at("users") >> at("alice") >> at("email")
email_lens.get(config)                          # "alice@old.com"
email_lens.set(config, "alice@new.com")         # rebuilds the path
email_lens.modify(config, str.upper)            # "ALICE@OLD.COM"

version_lens = at("app") >> at("settings") >> at("version")
version_lens.modify(config, lambda v: v + 1)    # bumps to 3
```

## Roadmap

- **Python 3.12+ minimum** — rewrite type signatures using `type X[A, B] = ...` aliases and `class Foo[A]:` syntax. Eliminates `TypeVar` boilerplate and `Callable[[A, B], C]` throughout.
- **Parser combinators** — monadic parser library (`funstruct.experimental.parsing`). Demonstrate composing parsers with `bind`/`do`.
- **Typeclass derivation** — potentially something like mypy plugins (not likely).
- **Stream** — infinite streams, lazy
- **FreeMonad** - implementation
- **EffectsSystem** - utilizing an effects system over monad transformer stacks
