"""DotNotation mixin — provides dot-syntax by delegating to summon.

Independent from TypeConstructor. Requires _type_constructor to be set
(either manually or via TypeConstructor mixin).

    Some(10).map(lambda x: x + 1)  →  summon(Functor, Option).map(Some(10), f)

Typical usage — combine both mixins:

    class Option(TypeConstructor, DotNotation, Generic[A]):
        ...
"""

from __future__ import annotations


class DotNotation:
    """Provides dot-syntax for typeclass operations.

    Requires _type_constructor to be set on the class (via TypeConstructor
    mixin or manually). Dispatches attribute access to registered typeclass
    instances via summon.
    """

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name)

        tc = getattr(type(self), "_type_constructor", None)
        if tc is None:
            for base in type(self).__mro__:
                tc = getattr(base, "_type_constructor", None)
                if tc is not None:
                    break

        if tc is None:
            raise AttributeError(
                f"'{type(self).__name__}' has no _type_constructor — "
                f"add TypeConstructor mixin or set _type_constructor manually"
            )

        from funstruct.typeclasses.utils.registry import _registry

        for (typeclass, t), instance in _registry.items():
            if t is tc and hasattr(instance, name):
                method = getattr(instance, name)
                return lambda *args, **kwargs: method(self, *args, **kwargs)

        raise AttributeError(
            f"'{type(self).__name__}' has no typeclass method '{name}'"
        )

    def __rshift__(self, f):
        """>> operator delegates to bind via DotNotation."""
        return self.bind(f)

    def __mul__(self, other):
        """* operator delegates to product via DotNotation."""
        return self.product(other)


__all__ = ["DotNotation"]
