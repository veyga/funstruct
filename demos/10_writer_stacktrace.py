"""Writer monad: accumulate a call trace alongside computation.

Writer[W, A] = (value: A, output: W) where W is a Monoid.

The Writer monad lets you accumulate output (logs, traces, metrics)
alongside a computation without passing a mutable log around.

This demo builds a call trace — each step in a pipeline logs where
it was called and what it did, producing a complete trace at the end.

    result = pipeline("alice")
    result.value   # "ALICE@EXAMPLE.COM"
    result.output  # ["lookup_user(alice)", "get_email(User(alice))", "normalize(alice@...)"]
"""

from funstruct.monad.writer import ListWriter
from funstruct.typeclasses import Monoid


list_monoid = Monoid(typ=list, combine=lambda a, b: a + b, empty=[])


class TraceWriter(ListWriter):
    _monoid = list_monoid


def lookup_user(name: str) -> TraceWriter:
    """Simulate user lookup, logging the call."""
    users = {"alice": "Alice", "bob": "Bob"}
    user = users.get(name, "Unknown")
    return TraceWriter(user, [f"lookup_user({name}) → {user}"])


def get_email(user: str) -> TraceWriter:
    """Simulate email lookup, logging the call."""
    email = f"{user.lower()}@example.com"
    return TraceWriter(email, [f"get_email({user}) → {email}"])


def normalize(email: str) -> TraceWriter:
    """Normalize email, logging the transformation."""
    result = email.upper()
    return TraceWriter(result, [f"normalize({email}) → {result}"])


def validate(email: str) -> TraceWriter:
    """Validate email format, logging the check."""
    is_valid = "@" in email
    return TraceWriter(
        email if is_valid else "INVALID",
        [f"validate({email}) → {'OK' if is_valid else 'INVALID'}"],
    )


@TraceWriter.do
def pipeline(name: str):
    """Full pipeline with accumulated trace."""
    user = yield lookup_user(name)
    email = yield get_email(user)
    normalized = yield normalize(email)
    validated = yield validate(normalized)
    return validated


def main():
    print("=== Writer monad: call trace accumulation ===\n")

    result = pipeline("alice")
    print(f"  Value:  {result.value}")
    print(f"  Trace:")
    for entry in result.output:
        print(f"    → {entry}")

    print()

    result = pipeline("nobody")
    print(f"  Value:  {result.value}")
    print(f"  Trace:")
    for entry in result.output:
        print(f"    → {entry}")

    print("\n  The trace accumulates automatically via the Monoid.")
    print("  No mutable state, no global logger, no context passing.")

    # You can also use bind chains
    print("\n=== Bind chain (equivalent) ===\n")
    result = lookup_user("bob").bind(get_email).bind(normalize).bind(validate)
    print(f"  Value:  {result.value}")
    print(f"  Trace:  {result.output}")


if __name__ == "__main__":
    main()
