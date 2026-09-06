"""Demo: JSON encoder — typeclass composition and derivation.

Demonstrates the "implicit typeclass" pattern using a JSON encoder.
The architecture is the same as Scala's given/using or Haskell's typeclasses.

The key insight: generic functions with "trait bounds" that resolve
typeclass instances automatically. The caller doesn't pass encoders
around — summon finds them.

Three layers:
    1. Typeclass (interface)  — JsonEncoder: what it means to encode A as JSON
    2. Instances (per type)   — IntEncoder, StrEncoder, ListEncoder, etc.
    3. Generic functions      — to_json(value) summons the right encoder

This is NOT just "polymorphism via ABC". The ListEncoder *composes* —
it summons JsonEncoder for the element type, so List[User] works
if User has an encoder. That's typeclass derivation.

Usage:
    uv run python -m funstruct.playground.mt10
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, fields

from funstruct.typeclasses import register, summon


# ── Typeclass (the interface) ────────────────────────────────────────


class JsonEncoder(ABC):
    @abstractmethod
    def encode(self, value) -> object: ...


class JsonDecoder(ABC):
    @abstractmethod
    def decode(self, json_value) -> object: ...


# ── Instances (per type) ─────────────────────────────────────────────


class IntEncoder(JsonEncoder):
    def encode(self, value: int):
        return value


class FloatEncoder(JsonEncoder):
    def encode(self, value: float):
        return value


class StrEncoder(JsonEncoder):
    def encode(self, value: str):
        return value


class BoolEncoder(JsonEncoder):
    def encode(self, value: bool):
        return value


class NoneEncoder(JsonEncoder):
    def encode(self, value):
        return None


class ListEncoder(JsonEncoder):
    def encode(self, value: list):
        if not value:
            return []
        elem_encoder = summon(JsonEncoder, type(value[0]))
        return [elem_encoder.encode(item) for item in value]


class DictEncoder(JsonEncoder):
    def encode(self, value: dict):
        return {k: summon(JsonEncoder, type(v)).encode(v) for k, v in value.items()}


register(JsonEncoder, int, IntEncoder())
register(JsonEncoder, float, FloatEncoder())
register(JsonEncoder, str, StrEncoder())
register(JsonEncoder, bool, BoolEncoder())
register(JsonEncoder, type(None), NoneEncoder())
register(JsonEncoder, list, ListEncoder())
register(JsonEncoder, dict, DictEncoder())


# ── Dataclass encoder (derives from fields) ──────────────────────────


class DataclassEncoder(JsonEncoder):
    def encode(self, value):
        result = {}
        for f in fields(value):
            v = getattr(value, f.name)
            encoder = summon(JsonEncoder, type(v))
            result[f.name] = encoder.encode(v)
        return result


# ── Domain types ─────────────────────────────────────────────────────


@dataclass(frozen=True)
class Address:
    street: str
    city: str
    zip_code: str


@dataclass(frozen=True)
class User:
    name: str
    age: int
    email: str
    address: Address
    tags: list


@dataclass(frozen=True)
class Team:
    name: str
    members: list


register(JsonEncoder, Address, DataclassEncoder())
register(JsonEncoder, User, DataclassEncoder())
register(JsonEncoder, Team, DataclassEncoder())


# ── The generic function — this is the payoff ────────────────────────


def to_json(value) -> object:
    """Encode any value to JSON using its registered JsonEncoder.

    This function has an implicit "trait bound": it requires
    JsonEncoder[type(value)] to exist in the registry.

    The caller never passes an encoder — summon finds it.
    """
    encoder = summon(JsonEncoder, type(value))
    return encoder.encode(value)


# ── Demo ─────────────────────────────────────────────────────────────


def main():
    import json

    alice = User(
        name="Alice",
        age=30,
        email="alice@example.com",
        address=Address(street="123 Main St", city="NYC", zip_code="10001"),
        tags=["admin", "engineer"],
    )

    bob = User(
        name="Bob",
        age=25,
        email="bob@example.com",
        address=Address(street="456 Oak Ave", city="LA", zip_code="90001"),
        tags=["user"],
    )

    team = Team(name="Backend", members=[alice, bob])

    print("=== Primitive types ===")
    print(f"  to_json(42)       = {to_json(42)}")
    print(f"  to_json('hello')  = {to_json('hello')}")
    print(f"  to_json(True)     = {to_json(True)}")
    print(f"  to_json(None)     = {to_json(None)}")

    print("\n=== Composed types ===")
    print(f"  to_json([1,2,3])  = {to_json([1, 2, 3])}")

    print("\n=== Dataclass (derived from fields) ===")
    print(f"  to_json(alice)    = {json.dumps(to_json(alice), indent=2)}")

    print("\n=== Nested composition ===")
    print(f"  to_json(team)     = {json.dumps(to_json(team), indent=2)}")

    print("\n=== Why this matters ===")
    print("  1. to_json is GENERIC — it works for any type with a JsonEncoder")
    print("  2. ListEncoder COMPOSES — it summons JsonEncoder for elements")
    print("  3. DataclassEncoder DERIVES — it walks fields and summons per-field")
    print("  4. No encoders passed around — summon finds them (like Scala implicits)")
    print("  5. The dot syntax (Some(10).map(f)) is just sugar over this same pattern")


if __name__ == "__main__":
    main()
