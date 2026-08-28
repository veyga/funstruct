# funstruct

A small, helpful collection of functional utilities.

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
                           │
                    MonadTransformer
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

**Applicative** — combine independent computations

```
F[A] ─┐
       ├──> F[(A, B)]
F[B] ─┘
```

**Monad** — sequence computations that produce new contexts

```
F[A] ---( f: A -> F[B] )---> F[B]
```

```python
@dataclass(frozen=True)
class Semigroup:
    typ: type
    combine: Callable  # (A, A) -> A

@dataclass(frozen=True)
class Monoid(Semigroup):
    typ: type
    combine: Callable  # (A, A) -> A
    empty: object      # identity element

class Functor(ABC):
    def map(self, f) -> Functor: ...

class Applicative(Functor):
    def pure(cls, value) -> Applicative: ...
    def ap(self, other) -> Applicative: ...
    def __add__ = ap  # alias

class Monad(Applicative):
    def bind(self, f) -> Monad: ...
    def do(cls, gen_fn) -> Monad: ...
    def __rshift__ = bind  # >>

class MonadTransformer(Monad, Generic[_F, _A]):
    def and_then(self, other) -> MonadTransformer: ...
```

```python
# Multiple semigroups for the same type:
int_add = Monoid(typ=int, combine=lambda a, b: a + b, empty=0)
int_mul = Monoid(typ=int, combine=lambda a, b: a * b, empty=1)
```

### ~ Scala equivalent

```scala
trait Semigroup[A] {
  def combine(x: A, y: A): A
}

trait Monoid[A] extends Semigroup[A] {
  def empty: A
}

trait Functor[F[_]] {
  def map[A, B](fa: F[A])(f: A => B): F[B]
}

trait Applicative[F[_]] extends Functor[F] {
  def pure[A](a: A): F[A]
  def ap[A, B](ff: F[A => B])(fa: F[A]): F[B]
}

trait Monad[F[_]] extends Applicative[F] {
  def bind(fa: F[A])(f: A => F[B]): F[B]
}
```

### Implementations

| Typeclass        | Implementations                              |
| ---------------- | -------------------------------------------- |
| Functor          | Tree, frozendict, + all below                |
| Applicative      | Validated, + all below                       |
| Monad            | Option, Either, State, Reader, Writer, CList |
| MonadTransformer | ReaderT, StateT, EitherT, OptionT, WriterT   |

| Type                | What it models                              |
| ------------------- | ------------------------------------------- |
| `Option[A]`         | Value might not exist                       |
| `Either[E, A]`      | Value or typed error                        |
| `Result[A]` (alias) | `Either[Exception, A]` + `@Try` decorator   |
| `State[S, A]`       | Stateful computation                        |
| `Reader[Ctx, A]`    | Shared environment                          |
| `Writer[W, A]`      | Accumulated output                          |
| `Validated[E, A]`   | Error accumulation (applicative, not monad) |
| `Future[E, A]`      | Lazy async + typed error                    |
| `CList[A]`          | Persistent singly-linked list               |
| `Tree[A]`           | Immutable binary tree (functor only)        |
| `frozendict[K, V]`  | Persistent HAMT dictionary                  |

### Monad Transformers

A transformer combines effects by wrapping one monad inside another.

```
ReaderT[F, Ctx, A]  =  Ctx -> F[A]         (environment + F's effects)
StateT[F, S, A]     =  S -> F[(S, A)]      (state + F's effects)
EitherT[F, E, A]    =  F[Either[E, A]]     (errors + F's effects)
OptionT[F, A]       =  F[Option[A]]        (absence + F's effects)
WriterT[F, W, A]    =  F[(A, W)]           (output + F's effects)
```

**Why transformers?** Monads don't compose automatically. If you need
config + errors + logging, you'd manually unwrap 3 nested layers at
every step. Transformers flatten that into one `bind`:

```python
# Without transformer — nested pattern matching at every step:
result = fetch_user(id)          # Either[Err, Option[User]]
match result:
    case Left(e): ...            # handle error
    case Right(Nothing()): ...   # handle absence
    case Right(Some(user)): ...  # finally, the value

# With OptionT — one flat pipeline:
pipeline = (
    OptionT(fetch_user(id))
    .bind(lambda user: OptionT(get_email(user)))
    .map(lambda email: email.upper())
)
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

**Monad**

- Left identity: `pure(a).bind(f) == f(a)`
- Right identity: `m.bind(pure) == m`
- Associativity: `m.bind(f).bind(g) == m.bind(λx. f(x).bind(g))`

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

- **`Either[E, A]`** — for operations that might fail (the error is a value)
- **`Future[E, A]`** — for async operations that might fail (lazy, composable)
- **`@Try` / `@TryAsync`** — for wrapping exception-throwing code at boundaries

These give you the composition benefits of monadic pipelines where they
matter (error handling, async sequencing) without pretending Python is
something it isn't.
