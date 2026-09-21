# Foldable

## `fold_left` / `fold_right` vs `fold` (catamorphism)

funstruct has two different concepts that share the name "fold":

**`Foldable.fold_left` / `fold_right`** — iterates over elements in a structure,
accumulating a result. Defined on the `Foldable` typeclass.

```python
from funstruct.typeclasses import summon
from funstruct.typeclasses.foldable import Foldable
from funstruct.types.option import Some, Nothing

F = summon(Foldable, Option)
F.fold_left(Some(10), 0, lambda acc, x: acc + x)   # 10
F.fold_left(Nothing(), 0, lambda acc, x: acc + x)   # 0
```

**`.fold(on_left, on_right)`** — the catamorphism (eliminator) for an ADT.
It handles each variant, like a structured `match`. Defined directly on
the data type, not on a typeclass.

```python
from funstruct.types.option import Some, Nothing

Some(10).fold(on_nothing=lambda: "empty", on_some=lambda x: f"got {x}")
# "got 10"

Nothing().fold(on_nothing=lambda: "empty", on_some=lambda x: f"got {x}")
# "empty"
```

Every ADT has its own `fold`:

- `Option.fold(on_nothing, on_some)`
- `Result.fold(on_err, on_ok)`
- `Either.fold(on_left, on_right)`

These are not interchangeable. `Foldable` is a typeclass for iteration;
`.fold()` is a structural eliminator for pattern matching.

## Foldable vs Traversable

Every `Traversable` is also `Foldable` (since `Traversable` extends `Foldable`),
but not every `Foldable` is `Traversable`.

A type is **Foldable** when you can reduce/iterate its elements.
A type is **Traversable** when you can also **reconstruct the structure**
within an applicative context.

```text
Foldable            Traversable
────────            ───────────
frozendict[K, V]    Option[A]
                    Either[E, A]
                    CList[A]
                    Tree[A]
```

`frozendict` is Foldable but not Traversable — you can fold over its values,
but you can't rebuild a dict from within an applicative effect because keys
would need to be preserved through the effect.

```python
# Foldable: reduce values — works
F = summon(Foldable, frozendict)
F.fold_left(fd, 0, lambda acc, v: acc + v)

# Traversable: would need dict reconstruction inside the effect
# fd.traverse(f)  →  G[frozendict[K, B]]  — keys can't thread through G
```

## API Reference

::: funstruct.typeclasses.foldable
