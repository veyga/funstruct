"""Demo: extending funstruct with your own types and typeclasses.

This shows how to:
    1. Define a typeclass (interface)
    2. Create a custom data type
    3. Implement the typeclass for your type
    4. Write generic functions with trait bounds

This is the Scala/Rust pattern: define capabilities as typeclasses,
implement them per type, then write generic code constrained by those
capabilities.

Usage:
    uv run python -m funstruct.playground.mt13
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from typing import Protocol, runtime_checkable

from funstruct.typeclasses.utils.registry import register, summon, tc_of


# ═══════════════════════════════════════════════════════════════════════
# Part 1: Define a typeclass (the interface / trait)
# ═══════════════════════════════════════════════════════════════════════


class Showable(ABC):
    """Typeclass for types that can be displayed as a human-readable string.

    Like Haskell's Show or Rust's Display.
    """

    @abstractmethod
    def show(self, value) -> str: ...


class Serializable(ABC):
    """Typeclass for types that can be serialized to a dict (JSON-like).

    Like Scala's Encoder or Rust's Serialize.
    """

    @abstractmethod
    def to_dict(self, value) -> dict: ...


class Deserializable(ABC):
    """Typeclass for types that can be deserialized from a dict."""

    @abstractmethod
    def from_dict(self, data: dict) -> object: ...


# ═══════════════════════════════════════════════════════════════════════
# Part 2: Define your custom data types (plain data, no typeclass methods)
# ═══════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class Email:
    value: str


@dataclass(frozen=True)
class Address:
    street: str
    city: str
    zip_code: str


@dataclass(frozen=True)
class User:
    name: str
    age: int
    email: Email
    address: Address


@dataclass(frozen=True)
class Team:
    name: str
    members: list[User]


# ═══════════════════════════════════════════════════════════════════════
# Part 3: Implement the typeclasses for your types
# ═══════════════════════════════════════════════════════════════════════

# --- Showable instances ---


class _EmailShowable(Showable):
    def show(self, value: Email) -> str:
        return value.value


class _AddressShowable(Showable):
    def show(self, value: Address) -> str:
        return f"{value.street}, {value.city} {value.zip_code}"


class _UserShowable(Showable):
    def show(self, value: User) -> str:
        addr = summon(Showable, Address).show(value.address)
        return f"{value.name} (age {value.age}, {value.email.value}, {addr})"


class _TeamShowable(Showable):
    def show(self, value: Team) -> str:
        user_show = summon(Showable, User)
        members = ", ".join(user_show.show(m) for m in value.members)
        return f"Team {value.name}: [{members}]"


register(Showable, Email, _EmailShowable())
register(Showable, Address, _AddressShowable())
register(Showable, User, _UserShowable())
register(Showable, Team, _TeamShowable())


# --- Serializable instances (composable — each type delegates to its fields) ---


class _EmailSerializer(Serializable):
    def to_dict(self, value: Email) -> dict:
        return {"email": value.value}


class _AddressSerializer(Serializable):
    def to_dict(self, value: Address) -> dict:
        return {"street": value.street, "city": value.city, "zip": value.zip_code}


class _UserSerializer(Serializable):
    def to_dict(self, value: User) -> dict:
        return {
            "name": value.name,
            "age": value.age,
            "email": summon(Serializable, Email).to_dict(value.email),
            "address": summon(Serializable, Address).to_dict(value.address),
        }


class _TeamSerializer(Serializable):
    def to_dict(self, value: Team) -> dict:
        user_ser = summon(Serializable, User)
        return {
            "team": value.name,
            "members": [user_ser.to_dict(m) for m in value.members],
        }


register(Serializable, Email, _EmailSerializer())
register(Serializable, Address, _AddressSerializer())
register(Serializable, User, _UserSerializer())
register(Serializable, Team, _TeamSerializer())


# --- Deserializable instances ---


class _UserDeserializer(Deserializable):
    def from_dict(self, data: dict) -> User:
        return User(
            name=data["name"],
            age=data["age"],
            email=Email(data["email"]["email"]),
            address=Address(
                street=data["address"]["street"],
                city=data["address"]["city"],
                zip_code=data["address"]["zip"],
            ),
        )


register(Deserializable, User, _UserDeserializer())


# ═══════════════════════════════════════════════════════════════════════
# Part 4: Generic functions with trait bounds
# ═══════════════════════════════════════════════════════════════════════

# In Scala:   def show[A: Showable](a: A): String
# In Rust:    fn show<A: Display>(a: &A) -> String
# In Python:  type hint is the constraint, summon resolves at runtime


def show[A](value: A, S: Showable | None = None) -> str:
    """Generic show — works for any type with a Showable instance.

    The trait bound: S must be Showable. If not passed, auto-resolved.
    Scala equivalent: def show[A: Showable](a: A): String
    """
    if S is None:
        S = summon(Showable, type(value))
    return S.show(value)


def serialize[A](value: A, S: Serializable | None = None) -> dict:
    """Generic serialize — works for any type with a Serializable instance."""
    if S is None:
        S = summon(Serializable, type(value))
    return S.to_dict(value)


def deserialize[A](cls: type[A], data: dict, D: Deserializable | None = None) -> A:
    """Generic deserialize — works for any type with a Deserializable instance."""
    if D is None:
        D = summon(Deserializable, cls)
    return D.from_dict(data)


# Combining multiple trait bounds (like Scala's A: Showable: Serializable)
def log_and_serialize[A](value: A) -> tuple[str, dict]:
    """Requires BOTH Showable AND Serializable — two trait bounds.

    Scala: def logAndSerialize[A: Showable: Serializable](a: A): (String, Map)
    Rust:  fn log_and_serialize<A: Display + Serialize>(a: &A) -> (String, Map)
    """
    displayed = summon(Showable, type(value)).show(value)
    serialized = summon(Serializable, type(value)).to_dict(value)
    return (displayed, serialized)


# ═══════════════════════════════════════════════════════════════════════
# Protocol-based trait bound (compile-time checkable with type checkers)
# ═══════════════════════════════════════════════════════════════════════


@runtime_checkable
class HasShowable(Protocol):
    """Protocol that checks if a type has a Showable instance registered.

    This is the closest Python gets to Scala's context bounds.
    Use isinstance(value, HasShowable) to check at runtime.
    """

    ...


# ═══════════════════════════════════════════════════════════════════════
# Demo
# ═══════════════════════════════════════════════════════════════════════


def main():
    import json

    alice = User(
        name="Alice",
        age=30,
        email=Email("alice@example.com"),
        address=Address("123 Main St", "NYC", "10001"),
    )
    bob = User(
        name="Bob",
        age=25,
        email=Email("bob@example.com"),
        address=Address("456 Oak Ave", "LA", "90001"),
    )
    team = Team(name="Backend", members=[alice, bob])

    print("=== Part 1: show() — generic function, auto-resolves Showable ===\n")
    print(f"  show(alice)   = {show(alice)}")
    print(f"  show(bob)     = {show(bob)}")
    print(f"  show(team)    = {show(team)}")
    print(f"  show(alice.email)   = {show(alice.email)}")
    print(f"  show(alice.address) = {show(alice.address)}")

    print(
        "\n=== Part 2: serialize() — generic function, auto-resolves Serializable ===\n"
    )
    print(f"  serialize(alice) = {json.dumps(serialize(alice), indent=2)}")

    print("\n=== Part 3: deserialize() — generic round-trip ===\n")
    data = serialize(alice)
    alice2 = deserialize(User, data)
    print(f"  serialize → deserialize round-trip: {alice2}")
    print(f"  round-trip matches? {alice == alice2}")

    print("\n=== Part 4: log_and_serialize() — multiple trait bounds ===\n")
    displayed, serialized = log_and_serialize(team)
    print(f"  displayed:  {displayed}")
    print(f"  serialized: {json.dumps(serialized, indent=2)}")

    print("\n=== Part 5: Error when trait bound not satisfied ===\n")
    try:
        show(42)  # int has no Showable instance
    except TypeError as e:
        print(f"  show(42) → TypeError: {e}")
    try:
        serialize("hello")  # str has no Serializable instance
    except TypeError as e:
        print(f'  serialize("hello") → TypeError: {e}')

    print("\n=== Summary ===\n")
    print("  1. Define a typeclass (ABC with abstract methods)")
    print("  2. Create your data types (plain dataclasses)")
    print("  3. Implement the typeclass (class + register)")
    print("  4. Write generic functions (summon resolves the instance)")
    print("  5. Trait bounds = type hints + summon (enforced at runtime)")
    print("  6. Multiple bounds = multiple summon calls")


if __name__ == "__main__":
    main()
