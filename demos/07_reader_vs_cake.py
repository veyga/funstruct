"""Demo: Reader monad vs Cake pattern for dependency injection.

Both solve the same problem: threading dependencies through a pipeline
without passing them explicitly at every call site.

Reader monad:  runtime DI — context threaded monadically
Cake pattern:  definition-time DI — dependencies composed via mixins

Usage:
    uv run python -m funstruct.playground.mt12
"""

from __future__ import annotations

from dataclasses import dataclass


# ── Shared domain ────────────────────────────────────────────────────


@dataclass(frozen=True)
class User:
    id: int
    name: str
    email: str


@dataclass(frozen=True)
class Order:
    id: int
    user_id: int
    total: float


# ══════════════════════════════════════════════════════════════════════
# Approach 1: Reader monad
# ══════════════════════════════════════════════════════════════════════

from funstruct.monad.reader import Reader


@dataclass(frozen=True)
class AppContext:
    """The shared environment — everything the pipeline needs."""

    db: dict
    email_service: str


def get_user(user_id: int) -> Reader[AppContext, User]:
    return Reader(lambda ctx: ctx.db["users"][user_id])


def get_orders(user: User) -> Reader[AppContext, list[Order]]:
    return Reader(lambda ctx: [o for o in ctx.db["orders"] if o.user_id == user.id])


def send_summary(user: User, orders: list[Order]) -> Reader[AppContext, str]:
    return Reader(
        lambda ctx: (
            f"[{ctx.email_service}] Sent {len(orders)} orders "
            f"(${sum(o.total for o in orders):.2f}) to {user.email}"
        )
    )


@Reader.do
def reader_pipeline(user_id: int):
    """Build a pipeline that reads from AppContext.

    Returns a Reader — nothing runs until .run(ctx) is called:
        ctx = AppContext(db=..., email_service="SendGrid")
        reader_pipeline(1).run(ctx)  # "[SendGrid] Sent 2 orders..."
    """
    user = yield get_user(user_id)
    orders = yield get_orders(user)
    result = yield send_summary(user, orders)
    return result


# ══════════════════════════════════════════════════════════════════════
# Approach 2: Cake pattern (mixin-based DI)
# ══════════════════════════════════════════════════════════════════════

from abc import ABC, abstractmethod


class UserRepoComponent(ABC):
    @abstractmethod
    def get_user(self, user_id: int) -> User: ...


class OrderRepoComponent(ABC):
    @abstractmethod
    def get_orders(self, user: User) -> list[Order]: ...


class EmailComponent(ABC):
    @abstractmethod
    def send_summary(self, user: User, orders: list[Order]) -> str: ...


class OrderSummaryService(UserRepoComponent, OrderRepoComponent, EmailComponent):
    """Business logic — declares dependencies via inheritance.

    This class doesn't know WHERE users come from or HOW emails are sent.
    It just declares what it needs (the component ABCs) and uses them.
    """

    def run(self, user_id: int) -> str:
        user = self.get_user(user_id)
        orders = self.get_orders(user)
        return self.send_summary(user, orders)


class ProductionApp(OrderSummaryService):
    """'Bake the cake' — provide all the real implementations."""

    def __init__(self, db: dict, email_service: str):
        self._db = db
        self._email_service = email_service

    def get_user(self, user_id: int) -> User:
        return self._db["users"][user_id]

    def get_orders(self, user: User) -> list[Order]:
        return [o for o in self._db["orders"] if o.user_id == user.id]

    def send_summary(self, user: User, orders: list[Order]) -> str:
        return (
            f"[{self._email_service}] Sent {len(orders)} orders "
            f"(${sum(o.total for o in orders):.2f}) to {user.email}"
        )


class TestApp(OrderSummaryService):
    """Test 'cake' — swap implementations without changing business logic."""

    def get_user(self, user_id: int) -> User:
        return User(id=user_id, name="TestUser", email="test@test.com")

    def get_orders(self, user: User) -> list[Order]:
        return [Order(id=1, user_id=user.id, total=99.99)]

    def send_summary(self, user: User, orders: list[Order]) -> str:
        return f"[TEST] Would send {len(orders)} orders to {user.email}"


# ══════════════════════════════════════════════════════════════════════
# Demo
# ══════════════════════════════════════════════════════════════════════


def main():
    db = {
        "users": {
            1: User(id=1, name="Alice", email="alice@example.com"),
            2: User(id=2, name="Bob", email="bob@example.com"),
        },
        "orders": [
            Order(id=101, user_id=1, total=49.99),
            Order(id=102, user_id=1, total=129.00),
            Order(id=103, user_id=2, total=9.99),
        ],
    }

    ctx = AppContext(db=db, email_service="SendGrid")

    print("=== Reader monad ===\n")
    print(f"  {reader_pipeline(1).run(ctx)}")
    print(f"  {reader_pipeline(2).run(ctx)}")

    print("\n=== Cake pattern (production) ===\n")
    prod = ProductionApp(db=db, email_service="SendGrid")
    print(f"  {prod.run(1)}")
    print(f"  {prod.run(2)}")

    print("\n=== Cake pattern (test — swapped implementations) ===\n")
    test = TestApp()
    print(f"  {test.run(1)}")
    print(f"  {test.run(2)}")

    print("\n=== Comparison ===\n")
    print("  Reader monad:")
    print("    + Composable (bind/map/do-notation)")
    print("    + Context is a value — easy to modify mid-pipeline")
    print("    + Lazy — pipeline is a description, run() executes it")
    print("    - Requires .run(ctx) at the boundary")
    print("    - Context is untyped (one big AppContext)")
    print()
    print("  Cake pattern:")
    print("    + Dependencies are typed (each ABC is explicit)")
    print("    + No .run() — just call methods directly")
    print("    + Very natural Python (mixins, ABCs)")
    print("    + Easy to test (swap the 'cake')")
    print("    - Not composable with bind/map")
    print("    - Dependencies resolved at class definition, not runtime")


if __name__ == "__main__":
    main()
# uv run python -m funstruct.playground.mt12
