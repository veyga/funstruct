# funstruct

A helpful collection of functional utilities.

## Install

```bash
pip install funstruct || uv add funstruct
```

## Functional Primer

### Type Class Hierarchy

```
Semigroup              Functor
    │                      │
 Monoid              Applicative
                           │
                         Monad
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
# Value-level typeclasses (not inherited — instantiated per type)
@dataclass(frozen=True)
class Semigroup:
    typ: type
    combine: Callable[[A, A], A]

@dataclass(frozen=True)
class Monoid(Semigroup):
    empty: A  # identity element

# Type-level hierarchy (inherited by data types)
class Functor(ABC, Generic[A]):
    def map(self, f: Callable[[A], B]) -> Functor[B]: ...          # abstract

class Applicative(Functor[A]):
    def pure(cls, value: A) -> Applicative[A]: ...                  # abstract
    def ap(self: Applicative[Callable[[A], B]],
           other: Applicative[A]) -> Applicative[B]: ...            # abstract
    def map(self, f) -> Applicative[B]: ...                         # derived: pure(f).ap(self)
    def product(self, other: Applicative[B]) -> Applicative[tuple[A, B]]: ...
    __mul__ = product                                               # * operator

class Monad(Applicative[A]):
    def bind(self, f: Callable[[A], Monad[B]]) -> Monad[B]: ...    # abstract
    def do(cls, gen_fn: Callable) -> Callable[..., Monad[A]]: ...  # abstract
    def map(self, f) -> Monad[B]: ...                               # @final: bind + pure
    def ap(self, other) -> Monad[B]: ...                            # @final: bind + map
    def then(self, other: Monad[B]) -> Monad[B]: ...                # derived: bind
    def map2(self, other, f) -> Monad: ...                          # derived: bind + map
    __rshift__ = bind                                               # >> operator

# Separate hierarchy (experimental) — not a typeclass in Haskell/Scala
class MonadTransformer(ABC, Generic[F, A]):
    def bind(self, f) -> MonadTransformer: ...                      # abstract
    def map(self, f) -> MonadTransformer: ...                       # abstract
    def pure(cls, value, monad: type) -> MonadTransformer: ...      # abstract
    def lift_f(cls, inner: F) -> MonadTransformer: ...              # abstract
    def do(cls, gen_fn) -> Callable[..., MonadTransformer]: ...     # abstract
    def ap(self, other) -> MonadTransformer: ...                    # derived: bind + map
    def then(self, other) -> MonadTransformer: ...                  # derived: bind
    def product(self, other) -> MonadTransformer: ...               # derived: map + ap
    __mul__ = product                                               # * operator
    __rshift__ = bind                                               # >> operator
```

### Implementations

| Typeclass        | Implementations                                                           |
| ---------------- | ------------------------------------------------------------------------- |
| Functor          | Tree, frozendict, + all below                                             |
| Applicative      | Validated, + all below                                                    |
| Monad            | Option, Either, Result, State, Reader, Writer, CList, Future, AsyncResult |
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

### Monad Transformers (experimental)

> The transformer API is alpha and may change. For most use cases, plain
> monads with `do`-notation and `fold` are sufficient.

A transformer combines effects by wrapping one monad inside another.

```
ReaderT[F, Ctx, A]  =  Ctx -> F[A]         (environment + F's effects)
StateT[F, S, A]     =  S -> F[(S, A)]      (state + F's effects)
EitherT[F, E, A]    =  F[Either[E, A]]     (errors + F's effects)
OptionT[F, A]       =  F[Option[A]]        (absence + F's effects)
WriterT[F, W, A]    =  F[(A, W)]           (output + F's effects)
```

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
