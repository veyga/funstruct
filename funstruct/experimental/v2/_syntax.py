"""DotNotation mixin — provides dot-syntax by delegating to summon.

In Scala/Cats, `import cats.syntax.all._` gives you:
    Some(10).map(_ + 1)

which desugars to:
    Functor[Option].map(Some(10))(_ + 1)

This mixin does the same thing for Python. Data types that extend
DotNotation get dot-syntax for all registered typeclass methods.

    class Option(DotNotation, Generic[A]):
        _type_constructor = Option  # set after class definition
        ...

    Some(10).map(lambda x: x + 1)  # delegates to summon(Functor, Option).map(...)

Both styles work:
    # Dot syntax (convenient)
    Some(10).map(lambda x: x + 1)

    # Explicit (tagless final, generic programs)
    F = summon(Monad, Option)
    F.map(Some(10), lambda x: x + 1)
"""

from __future__ import annotations


class DotNotation:
    """Mixin that provides dot-syntax for typeclass operations.

    Subclasses must set _type_constructor to their base type after
    class definition (since the class doesn't exist yet during definition).

    How it works:
        Some(10).map(f)
        → __getattr__('map')
        → finds OptionMonad in registry (has 'map')
        → returns lambda that calls OptionMonad.map(Some(10), f)
    """

    _type_constructor: type | None = None

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name)

        tc = self._resolve_type_constructor()
        if tc is None:
            raise AttributeError(
                f"'{type(self).__name__}' has no _type_constructor set"
            )

        from funstruct.experimental.v2._registry import _registry

        for (typeclass, t), instance in _registry.items():
            if t is tc and hasattr(instance, name):
                method = getattr(instance, name)
                return lambda *args, **kwargs: method(self, *args, **kwargs)

        raise AttributeError(
            f"'{type(self).__name__}' has no typeclass method '{name}'"
        )

    def _resolve_type_constructor(self) -> type | None:
        if type(self)._type_constructor is not None:
            return type(self)._type_constructor
        for base in type(self).__mro__:
            tc = getattr(base, "_type_constructor", None)
            if tc is not None:
                return tc
        return None


__all__ = ["DotNotation"]
