# Applicatives

::: funstruct.applicative

Applicative functors allow combining independent computations.
Unlike Monad (where each step can depend on the previous),
Applicative combines values that don't depend on each other —
which enables error accumulation.

- [Validated](validated.md) — accumulate all errors instead of short-circuiting
