# funstruct

A small, helpful collection of functional utilities.

These are not meant to be highly performant, but are useful for smaller datasets.

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

```python
class Semigroup(Protocol):
    def __add__(self, other) -> Semigroup: ...

class Monoid(Semigroup, Protocol):
    def empty() -> Monoid: ...

class Functor(ABC):
    def map(self, f) -> Functor: ...

class Applicative(Functor):
    def pure(cls, value) -> Applicative: ...
    def ap(self, other) -> Applicative: ...
    def __add__ = ap  # alias

class Monad(Applicative):
    def bind(self, f) -> Monad: ...
```

### ~ Scala equivalent

```scala
trait Semigroup[A] {
  def +(x: A, y: A): A
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
