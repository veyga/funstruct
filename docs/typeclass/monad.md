# Monad

Sequence computations that produce new contexts. Extends [Applicative](applicative.md).

```
F[A] ---( f: A -> F[B] )---> F[B]
```

```python
Cons(1, Cons(2, Nil)) >> (lambda x: Cons(x, Cons(x * 10, Nil)))
```

### Implementations

- [State](../monad/state.md)
- [StateT](../monad/state_t.md)
- [ReaderT](../monad/reader_t.md)
- [Cons](../collections/cons.md)

## API Reference

::: funstruct.typeclass.monad.Monad
