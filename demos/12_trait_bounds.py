"""Trait bounds: constraining generic functions to types with specific capabilities.

In Scala:   def sort[A: Ordering](xs: List[A]): List[A]
In Rust:    fn sort<A: Ord>(xs: &mut [A])
In Haskell: sort :: Ord a => [a] -> [a]
In Python:  summon enforces the bound at runtime

The bound says: "this function works for ANY type A, as long as A has
an Ordering instance." If A doesn't have one, you get a clear error.

This demo shows:
    1. Defining a typeclass (Ordering)
    2. Implementing it for specific types
    3. Writing generic functions with trait bounds
    4. What happens when the bound is NOT met
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import functools

from funstruct.typeclasses.utils.registry import register, summon


# ═══════════════════════════════════════════════════════════════════════
# Part 1: Define the typeclass
# ═══════════════════════════════════════════════════════════════════════


class Ordering(ABC):
    """Typeclass for types that can be compared."""

    @abstractmethod
    def compare(self, a, b) -> int: ...


class Showable(ABC):
    """Typeclass for types that can be displayed."""

    @abstractmethod
    def show(self, value) -> str: ...


# ═══════════════════════════════════════════════════════════════════════
# Part 2: Data types (plain, no typeclass methods)
# ═══════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class User:
    name: str
    age: int


@dataclass(frozen=True)
class Temperature:
    celsius: float


@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int


# ═══════════════════════════════════════════════════════════════════════
# Part 3: Instances (only for types that HAVE the capability)
# ═══════════════════════════════════════════════════════════════════════


class _UserOrdering(Ordering):
    def compare(self, a: User, b: User) -> int:
        return a.age - b.age


class _UserShowable(Showable):
    def show(self, u: User) -> str:
        return f"{u.name}({u.age})"


class _TempOrdering(Ordering):
    def compare(self, a: Temperature, b: Temperature) -> int:
        return int(a.celsius - b.celsius)


class _TempShowable(Showable):
    def show(self, t: Temperature) -> str:
        return f"{t.celsius}°C"


# Note: Color has NO Ordering instance. It can't be sorted.
class _ColorShowable(Showable):
    def show(self, c: Color) -> str:
        return f"rgb({c.r},{c.g},{c.b})"


register(Ordering, User, _UserOrdering())
register(Showable, User, _UserShowable())
register(Ordering, Temperature, _TempOrdering())
register(Showable, Temperature, _TempShowable())
register(Showable, Color, _ColorShowable())
# NOT registered: Ordering for Color


# ═══════════════════════════════════════════════════════════════════════
# Part 4: Generic functions with trait bounds
# ═══════════════════════════════════════════════════════════════════════


def sort_by(items: list, O: Ordering) -> list:
    """Sort using an explicit Ordering instance.

    The caller provides the bound explicitly.
    Scala: sort(items)(using ord)
    """
    return sorted(items, key=functools.cmp_to_key(O.compare))


def auto_sort(items: list) -> list:
    """Sort using auto-resolved Ordering — trait bound enforced by summon.

    Scala: def sort[A: Ordering](items: List[A]): List[A]
    The bound is: A must have an Ordering instance.
    """
    if not items:
        return []
    O = summon(Ordering, type(items[0]))
    return sorted(items, key=functools.cmp_to_key(O.compare))


def show_all(items: list) -> list[str]:
    """Show all items — requires Showable for the element type."""
    if not items:
        return []
    S = summon(Showable, type(items[0]))
    return [S.show(item) for item in items]


def show_sorted(items: list) -> list[str]:
    """Sort AND show — requires BOTH Ordering AND Showable.

    Scala: def showSorted[A: Ordering: Showable](items: List[A]): List[String]
    Rust:  fn show_sorted<A: Ord + Display>(items: &[A]) -> Vec<String>
    """
    if not items:
        return []
    O = summon(Ordering, type(items[0]))
    S = summon(Showable, type(items[0]))
    sorted_items = sorted(items, key=functools.cmp_to_key(O.compare))
    return [S.show(item) for item in sorted_items]


# ═══════════════════════════════════════════════════════════════════════
# Demo
# ═══════════════════════════════════════════════════════════════════════


def main():
    users = [User("Charlie", 20), User("Alice", 30), User("Bob", 25)]
    temps = [Temperature(100), Temperature(0), Temperature(37)]
    colors = [Color(255, 0, 0), Color(0, 255, 0), Color(0, 0, 255)]

    print("=== Trait bounds: enforced at runtime via summon ===\n")

    # Sorting users — Ordering[User] exists
    print("  auto_sort(users):")
    for u in auto_sort(users):
        print(f"    {u}")

    # Sorting temperatures — Ordering[Temperature] exists
    print(f"\n  auto_sort(temps): {auto_sort(temps)}")

    # Show + sort — requires BOTH bounds
    print(f"\n  show_sorted(users): {show_sorted(users)}")
    print(f"  show_sorted(temps): {show_sorted(temps)}")

    # Show colors — Showable[Color] exists
    print(f"\n  show_all(colors): {show_all(colors)}")

    # ═══ TRAIT BOUND NOT MET ═══
    print("\n=== What happens when the bound is NOT met ===\n")

    # Sorting colors — NO Ordering[Color] instance!
    try:
        auto_sort(colors)
    except TypeError as e:
        print(f"  auto_sort(colors) → TypeError: {e}")

    # show_sorted(colors) — has Showable but NOT Ordering
    try:
        show_sorted(colors)
    except TypeError as e:
        print(f"  show_sorted(colors) → TypeError: {e}")

    # Sorting ints — no Ordering[int] registered
    try:
        auto_sort([3, 1, 2])
    except TypeError as e:
        print(f"  auto_sort([3,1,2]) → TypeError: {e}")

    print("\n=== The error is clear and immediate ===")
    print("  Scala/Rust: caught at compile time")
    print("  Python/funstruct: caught at runtime via summon")
    print("  The message tells you exactly what's missing")


if __name__ == "__main__":
    main()
