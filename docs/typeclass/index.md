# Type Classes

Abstract type definitions that describe what operations a type supports.
A type class defines the interface; concrete types provide the implementation.

```
Semigroup               Functor
    │                      │
 Monoid                Applicative
                           │
                         Monad
                           │
                    MonadTransformer
```

- [Semigroup](semigroup.md)
- [Monoid](monoid.md)
- [Functor](../functor/index.md)
- [Applicative](applicative.md)
- [Monad](monad.md)
- [MonadTransformer](monadtransformer.md)
