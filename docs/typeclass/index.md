# Typeclasses

## Architecture

funstruct has two separate class hierarchies connected by a registry:

```text
DataType (data)                         BaseTypeclass (behavior)
─────────────                           ────────────────────────
Option, Result, Either, ...             Functor → Applicative → Monad → MonadError
State, Reader, Writer, Future           Alternative, Bifunctor
CList, Tree, frozendict                 Foldable → Traversable
Validated, ZipList                      Semigroup → Monoid
```

**DataType** holds values — `Some(10)`, `Ok(42)`, `State(lambda s: ...)`.
It provides `TypeConstructor` (so `Some` resolves to `Option`) and
`DotNotation` (so `Some(10).map(f)` works).

**BaseTypeclass** defines operations — `map`, `bind`, `pure`, `fold_left`, etc.
Concrete instances like `_OptionMonad` implement these for a specific type.

**They never inherit from each other.** The connection is the registry:

```python
# Instance: implements Monad operations for Option
class _OptionMonad(Monad, for_type=Option):
    def pure(self, value):
        return Some(value)
    def bind(self, fa, f):
        match fa:
            case Some(v): return f(v)
            case Nothing(): return fa

# summon resolves the connection
summon(Monad, Option)  # → _OptionMonad instance

# Dot syntax is sugar over summon
Some(10).map(f)
# equivalent to:
summon(Functor, Option).map(Some(10), f)
```

Instances only implement **primitives** (`pure` + `bind` for Monad).
Derived operations (`map`, `ap`, `do`, `product`, `then`, `map2`) come
from the typeclass hierarchy automatically.

## Instance Grid

Which types implement which typeclasses:

| Type | Eq | Repr | Truth | Semi | Monoid | Func | App | Monad | MErr | Alt | Fold | Trav | Bifu | Str |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Option | ✓ | ✓ | ✓ | | | | | ✓ | | ✓ | | ✓ | | |
| Either | ✓ | ✓ | | | | | | | ✓ | | | ✓ | ✓ | |
| Result | ✓ | ✓ | | | | | | | ✓ | | | | ✓ | |
| AsyncResult | | ✓ | | | | | | | ✓ | | | | ✓ | |
| CList | ✓ | ✓ | ✓ | | ✓ | | | ✓ | | ✓ | | ✓ | | ✓ |
| Tree | ✓ | ✓ | | | | ✓ | | | | | ✓ | ✓ | | |
| frozendict | ✓ | ✓ | ✓ | ✓ | | ✓ | | | | | ✓ | | | |
| Validated | ✓ | ✓ | ✓ | | | | ✓ | | | | | | ✓ | |
| ZipList | ✓ | ✓ | | | | | ✓ | | | | ✓ | | | |
| State | | ✓ | | | | | | ✓ | | | | | | |
| Reader | | ✓ | | | | | | ✓ | | | | | | |
| Writer | ✓ | ✓ | | | | | | ✓ | | | | | | |
| Future | | ✓ | | | | | | ✓ | | | | | | |

**Key:** Eq = equality + hash, Repr = `__repr__`, Truth = `__bool__`, Str = `__str__`,
Func = Functor, App = Applicative, MErr = MonadError, Alt = Alternative,
Fold = Foldable, Trav = Traversable, Bifu = Bifunctor

Types without Eq (State, Reader, Future, AsyncResult) use identity comparison.
Types without Truthable default to `True` (Python default).

## Typeclasses

- [Semigroup](semigroup.md)
- [Monoid](monoid.md)
- [Functor](functor.md)
- [Applicative](applicative.md)
- [Alternative](alternative.md)
- [Monad](monad.md)
- [MonadError](monad_error.md)
- [Bifunctor](bifunctor.md)
- [Foldable](foldable.md)
- [Traversable](traversable.md)
