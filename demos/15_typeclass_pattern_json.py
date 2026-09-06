"""The typeclass pattern — explained with JSON serialization.

This is the canonical example of how typeclasses work:

    1. Define the typeclass (JSONWrite — the interface)
    2. Create instances for primitives (str, int, bool, None)
    3. Create COMPOSABLE instances (list — uses the element's instance)
    4. Create DERIVED instances (dataclass — uses field instances)
    5. Write a generic function (jsonify — works for ANY type with an instance)

The key insight: jsonify doesn't know about Person, or str, or list.
It just asks "does this type have a JSONWrite instance?" and uses it.
New types get JSON support by registering an instance — no modification
to jsonify or to the type itself.

Translated from Scala (scala-advanced-part-2/module09/05-type-classes.sc).

Usage:
    uv run python demos/15_typeclass_pattern_json.py
"""

from __future__ import annotations

import json
from abc import abstractmethod
from dataclasses import dataclass, fields

from funstruct.typeclasses import BaseTypeclass
from funstruct.typeclasses.utils.registry import register, summon


# ═══════════════════════════════════════════════════════════════════════
# Step 1: The typeclass — what it means to be JSON-writable
# ═══════════════════════════════════════════════════════════════════════


class JSONWrite(BaseTypeclass):
    """Typeclass: convert a value of type T to a JSON string.

    Extends BaseTypeclass so instances can use for_type= (auto-registration).
    Scala equivalent: trait JSONWrite[T] { def toJsonString(item: T): String }
    """

    @abstractmethod
    def to_json_string(self, item) -> str: ...


# ═══════════════════════════════════════════════════════════════════════
# Step 2: The generic function — works for ANY type with an instance
# ═══════════════════════════════════════════════════════════════════════


def jsonify(item) -> str:
    """Convert any value to a JSON string — if it has a JSONWrite instance.

    Scala equivalent:
        def jsonify[T: JSONWrite](item: T): String =
          implicitly[JSONWrite[T]].toJsonString(item)

    The [T: JSONWrite] is the trait bound. In Python, summon enforces it.
    """
    return summon(JSONWrite, type(item)).to_json_string(item)


# ═══════════════════════════════════════════════════════════════════════
# Step 3: Instances for primitives
# ═══════════════════════════════════════════════════════════════════════


class _StringJSONWrite(JSONWrite, for_type=str):
    """Scala: given JSONWrite[String] with ..."""
    def to_json_string(self, item: str) -> str:
        return json.dumps(item)

class _IntJSONWrite(JSONWrite, for_type=int):
    def to_json_string(self, item: int) -> str:
        return str(item)

class _FloatJSONWrite(JSONWrite, for_type=float):
    def to_json_string(self, item: float) -> str:
        return str(item)

class _BoolJSONWrite(JSONWrite, for_type=bool):
    def to_json_string(self, item: bool) -> str:
        return "true" if item else "false"

class _NoneJSONWrite(JSONWrite, for_type=type(None)):
    def to_json_string(self, item) -> str:
        return "null"


# ═══════════════════════════════════════════════════════════════════════
# Step 4: COMPOSABLE instance — list uses the element's instance
# ═══════════════════════════════════════════════════════════════════════


class _ListJSONWrite(JSONWrite, for_type=list):
    """List serializer — composes with the element type's JSONWrite.

    This is the power of typeclasses: the list instance SUMMONS the element
    instance. List[int] uses IntJSONWrite, List[str] uses StringJSONWrite.
    """
    def to_json_string(self, items: list) -> str:
        if not items:
            return "[]"
        elem_writer = summon(JSONWrite, type(items[0]))
        elements = ", ".join(elem_writer.to_json_string(item) for item in items)
        return f"[{elements}]"


# ═══════════════════════════════════════════════════════════════════════
# Step 5: DERIVED instance — dataclass uses field instances
# ═══════════════════════════════════════════════════════════════════════


class DataclassJSONWrite(JSONWrite):
    """Generic dataclass serializer — derives from field types.

    Walks the dataclass fields, summons JSONWrite for each field's type,
    and produces {"ClassName": {"field1": value1, "field2": value2}}.

    This is the Python equivalent of Scala's CaseClassJsonWriter.
    """

    def to_json_string(self, item) -> str:
        cls_name = type(item).__name__
        field_strings = []
        for f in fields(item):
            value = getattr(item, f.name)
            writer = summon(JSONWrite, type(value))
            field_strings.append(f'"{f.name}": {writer.to_json_string(value)}')
        all_fields = ", ".join(field_strings)
        return f'{{"{cls_name}": {{{all_fields}}}}}'


# ═══════════════════════════════════════════════════════════════════════
# Step 6: Your data types — plain dataclasses, no JSON knowledge
# ═══════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class Person:
    name: str
    age: int


@dataclass(frozen=True)
class Address:
    street: str
    city: str
    zip_code: str


@dataclass(frozen=True)
class Employee:
    person: Person
    address: Address
    salary: float


# Register them — one line each
register(JSONWrite, Person, DataclassJSONWrite())
register(JSONWrite, Address, DataclassJSONWrite())
register(JSONWrite, Employee, DataclassJSONWrite())


# ═══════════════════════════════════════════════════════════════════════
# Demo — jsonify works for everything
# ═══════════════════════════════════════════════════════════════════════


def main():
    print("=== The typeclass pattern: JSON serialization ===\n")

    # Primitives
    print("Primitives:")
    print(f'  jsonify("hello")  = {jsonify("hello")}')
    print(f"  jsonify(42)       = {jsonify(42)}")
    print(f"  jsonify(3.14)     = {jsonify(3.14)}")
    print(f"  jsonify(True)     = {jsonify(True)}")
    print(f"  jsonify(None)     = {jsonify(None)}")

    # Composed — list uses element instance
    print("\nComposed (list summons element instance):")
    print(f"  jsonify([1,2,3])         = {jsonify([1, 2, 3])}")
    print(f'  jsonify(["a","b","c"])   = {jsonify(["a", "b", "c"])}')

    # Derived — dataclass uses field instances
    person = Person("Alice", 30)
    print(f"\nDerived (dataclass uses field instances):")
    print(f"  jsonify(Person)    = {jsonify(person)}")

    address = Address("123 Main St", "NYC", "10001")
    print(f"  jsonify(Address)   = {jsonify(address)}")

    # Nested — Employee has Person AND Address fields
    emp = Employee(person, address, 120000.0)
    print(f"\nNested (Employee → Person + Address):")
    print(f"  jsonify(Employee)  = {jsonify(emp)}")

    # List of dataclasses — composition all the way down
    people = [Person("Alice", 30), Person("Bob", 25)]
    print(f"\nList of dataclasses:")
    print(f"  jsonify([Person])  = {jsonify(people)}")

    # Error — no instance
    print("\nTrait bound not met:")
    try:
        jsonify({"key": "value"})
    except TypeError as e:
        print(f"  jsonify(dict) → TypeError: {e}")

    print("\n=== How it works ===")
    print("  1. JSONWrite          = the typeclass (interface)")
    print("  2. _StringJSONWrite   = instance for str")
    print("  3. _ListJSONWrite     = COMPOSABLE instance (summons element instance)")
    print("  4. DataclassJSONWrite = DERIVED instance (summons field instances)")
    print("  5. jsonify(x)         = generic function (summons instance for type(x))")
    print("  6. Person             = plain dataclass (no JSON knowledge)")


if __name__ == "__main__":
    main()
