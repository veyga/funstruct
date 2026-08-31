# Monads

::: funstruct.monad

Monads model sequenced computations with context — failure, absence,
environment, state, logging, or async effects. Chain with `.bind()`,
transform with `.map()`.

- [Either](either.md) — success or failure with a value
- [Option](option.md) — presence or absence
- [Result](result.md) — Either with Exception fixed as the error type
- [Reader](reader.md) — shared read-only environment
- [Writer](writer.md) — computation with accumulated output
- [State](state.md) — threaded mutable state
- [Future](future.md) — lazy async computation
