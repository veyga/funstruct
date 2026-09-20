"""Demo: static summon verification — all calls resolve.

This demonstrates how a downstream project uses ``funstruct-check``
to verify that every ``summon()`` call in their codebase has a
matching registered instance. All instances here are properly registered,
so the check passes.

Run the check::

    funstruct-check --import demos.16_check_summon_pass demos/16_check_summon_pass.py

Or from Python::

    from funstruct.check import check_summon
    result = check_summon(
        paths=["demos/16_check_summon_pass.py"],
        imports=["demos.16_check_summon_pass"],
    )
    assert result.ok, result.report()
"""

from funstruct.typeclasses import (
    BaseTypeclass,
    DataType,
    Monad,
    MonadError,
    summon,
    typeclass_of,
)
from funstruct.monad.option import Nothing, Option, Some
from funstruct.monad.result import Err, Ok, Result


# ── Custom typeclass ────────────────────────────────────────────────
class Showable(BaseTypeclass):
    def show(self, value: object) -> str: ...


# ── Custom data type ────────────────────────────────────────────────
class Temperature(DataType):
    def __init__(self, celsius: float) -> None:
        self.celsius = celsius

    def __repr__(self) -> str:
        return f"Temperature({self.celsius})"


# ── Register instances ──────────────────────────────────────────────
class _TemperatureShowable(Showable, for_type=Temperature):
    def show(self, value: Temperature) -> str:
        return f"{value.celsius}°C"


# ── Functions that use summon ───────────────────────────────────────
def display[T](value: T) -> str:
    """Summon Showable for any registered type."""
    S: Showable = summon(Showable, type(value))
    return S.show(value)


def double_monadic[F](fa: F) -> F:
    """Summon Monad by resolving the type constructor from the value."""
    M: Monad = summon(Monad, typeclass_of(fa))
    return M.map(fa, lambda x: x * 2)


def safe_divide(a: float, b: float) -> Result[float]:
    """Use MonadError to handle division errors."""
    ME: MonadError = summon(MonadError, Result)
    if b == 0:
        return ME.raise_error(ZeroDivisionError("division by zero"))
    return Ok(a / b)


# ── All summon calls resolve ────────────────────────────────────────
if __name__ == "__main__":
    print("=== check_summon PASS demo ===\n")

    print("Custom typeclass:")
    print(f"  display(Temperature(100)) = {display(Temperature(100))}")

    print("\nBuilt-in typeclasses:")
    print(f"  double_monadic(Some(21))  = {double_monadic(Some(21))}")
    print(f"  double_monadic(Ok(21))    = {double_monadic(Ok(21))}")
    print(f"  safe_divide(10, 3)        = {safe_divide(10, 3)}")
    print(f"  safe_divide(10, 0)        = {safe_divide(10, 0)}")

    print("\n--- Running check_summon on this file ---")
    from funstruct.check import check_summon

    result = check_summon(
        paths=["demos/16_check_summon_pass.py"],
        imports=["demos.16_check_summon_pass"],
    )
    print(result.report())
    assert result.ok
    print("\nAll summon() calls verified.")
