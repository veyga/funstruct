"""DotNotation mixin — provides dot-syntax by delegating to summon.

Data types that extend DotNotation get dot-syntax for all registered
typeclass methods. This is the Python equivalent of Scala's extension
methods / cats.syntax.

    Some(10).map(lambda x: x + 1)  →  summon(Functor, Option).map(Some(10), f)

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

    Subclasses must set _type_constructor to their base type.
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

        from funstruct.typeclasses._registry import _registry

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

    def __rshift__(self, f):
        """>> operator delegates to bind via DotNotation."""
        return self.bind(f)

    def __mul__(self, other):
        """* operator delegates to product via DotNotation."""
        return self.product(other)


__all__ = ["DotNotation"]
