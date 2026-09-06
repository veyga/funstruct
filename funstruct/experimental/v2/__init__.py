"""v2 prototype — separated data types + typeclass instances + summon.

This is a proof of concept for the Scala-style architecture where:
    - Data types are plain (Option, Some, Nothing — no typeclass methods)
    - Typeclasses are separate instance classes (OptionMonad extends Monad)
    - summon resolves instances from a registry
    - Derived typeclasses are resolved via the hierarchy (Monad → Functor)

Status: experimental prototype. Evaluating ergonomics before migrating.
"""
