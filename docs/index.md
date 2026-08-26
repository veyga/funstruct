# funstruct

Fun & functional structures for Python.

## Modules

| Module | Description |
|--------|-------------|
| [State](modules/state.md) | Pure State monad: `S -> (S, A)` |
| [StateT](modules/state_t.md) | State monad transformer over any monad |
| [ReaderT](modules/reader_t.md) | Reader monad transformer (dependency injection) |
| [Validated](modules/validated.md) | Applicative error accumulation |
| [Cons](modules/cons.md) | Persistent cons list |
| [FrozenDict](modules/frozendict.md) | Immutable dictionary |
| [TailRec](modules/tailrec.md) | Tail-call optimization decorator |

## Install

```bash
uv add funstruct
```

## Operators

All monadic types support:

| Op | Method | Description |
|----|--------|-------------|
| `>>` | `bind` | Monadic flatMap |
| `+` | `product` | Applicative product |
