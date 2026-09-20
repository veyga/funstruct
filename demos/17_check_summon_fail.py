"""Demo: static summon verification — missing instance detected.

This demonstrates how ``funstruct-check`` catches a missing typeclass
instance BEFORE your code runs. The Showable instance for ``Color``
was never registered, but the code calls ``summon(Showable, Color)``.

At runtime this would raise TypeError. The checker catches it statically::

    funstruct-check --import demos.17_check_summon_fail demos/17_check_summon_fail.py

Output::

    Found 1 unresolvable summon() calls:

      demos/17_check_summon_fail.py:52: summon(Showable, Color) — no instance registered

Or from Python::

    from funstruct.check import check_summon
    result = check_summon(
        paths=["demos/17_check_summon_fail.py"],
        imports=["demos.17_check_summon_fail"],
    )
    assert not result.ok   # one unresolvable call
"""

from funstruct.typeclasses import BaseTypeclass, summon


# ── Custom typeclass ────────────────────────────────────────────────
class Showable(BaseTypeclass):
    def show(self, value) -> str: ...


# ── Two data types, but only ONE gets an instance ───────────────────
class Temperature:
    _type_constructor = None

    def __init__(self, celsius: float):
        self.celsius = celsius


Temperature._type_constructor = Temperature


class Color:
    _type_constructor = None

    def __init__(self, name: str):
        self.name = name


Color._type_constructor = Color


# ── Register Showable for Temperature — but NOT for Color ───────────
class _TemperatureShowable(Showable, for_type=Temperature):
    def show(self, value) -> str:
        return f"{value.celsius}°C"


# No _ColorShowable registered!


# ── This function has a summon call that CANNOT resolve ─────────────
def display_color(c):
    """BUG: no Showable instance exists for Color."""
    S = summon(Showable, Color)
    return S.show(c)


def display_temperature(t):
    """This one is fine — Showable[Temperature] exists."""
    S = summon(Showable, Temperature)
    return S.show(t)


# ── Show both the runtime error and the static check ────────────────
if __name__ == "__main__":
    print("=== check_summon FAIL demo ===\n")

    print("Temperature (registered):")
    print(f"  display_temperature(Temperature(100)) = {display_temperature(Temperature(100))}")

    print("\nColor (NOT registered):")
    try:
        display_color(Color("red"))
    except TypeError as e:
        print(f"  Runtime error: {e}")

    print("\n--- Running check_summon on this file ---")
    from funstruct.check import check_summon

    result = check_summon(
        paths=["demos/17_check_summon_fail.py"],
        imports=["demos.17_check_summon_fail"],
    )
    print(result.report())
    assert not result.ok, "Expected check to fail!"
    print(f"\nCaught {len(result.errors)} unresolvable summon() call(s) — before runtime.")
