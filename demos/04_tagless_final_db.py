"""Demo: tagless final — swapping database backends.

The real payoff: business logic (place_order) doesn't know or care
whether it's talking to Postgres, an in-memory dict, or a test stub.

Three interpreters, same program:
    PostgresOrderRepo  — "real" async DB (simulated with sleep)
    InMemoryOrderRepo  — sync, no IO — for unit tests
    FailingOrderRepo   — always fails — for error-path tests

Run: uv run python demos/04_tagless_final_db.py
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Protocol

from funstruct.monad.result import AsyncResult, Err, Ok, Result, TryAsync


# ── Domain ───────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Customer:
    id: str
    name: str
    credit: float


@dataclass(frozen=True)
class Product:
    id: str
    name: str
    price: float


@dataclass(frozen=True)
class Order:
    customer: Customer
    product: Product
    total: float


# ── Algebra ──────────────────────────────────────────────────────────


class OrderRepo[F](Protocol):
    def find_customer(self, customer_id: str) -> F[Customer]: ...
    def find_product(self, product_id: str) -> F[Product]: ...
    def save_order(self, order: Order) -> F[Order]: ...


# ── Program (generic in F) ───────────────────────────────────────────


def place_order[F](
    repo: OrderRepo[F], F: type[F], customer_id: str, product_id: str
) -> F[Order]:
    @F.do
    def run():
        customer = yield repo.find_customer(customer_id)
        product = yield repo.find_product(product_id)
        if customer.credit < product.price:
            yield F.raise_error(
                ValueError(
                    f"{customer.name} has ${customer.credit:.2f}, needs ${product.price:.2f}"
                )
            )
        order = Order(customer=customer, product=product, total=product.price)
        saved = yield repo.save_order(order)
        return saved

    return run()


# ── Interpreter 1: "Postgres" (async) ────────────────────────────────


class PostgresOrderRepo:
    _customers = {
        "alice": Customer(id="alice", name="Alice", credit=500.0),
        "bob": Customer(id="bob", name="Bob", credit=5.0),
    }
    _products = {
        "widget": Product(id="widget", name="Widget Pro", price=49.99),
        "laptop": Product(id="laptop", name="Laptop Ultra", price=2999.0),
    }

    @TryAsync
    async def find_customer(self, customer_id: str) -> Customer:
        await asyncio.sleep(0.01)
        if customer_id not in self._customers:
            raise KeyError(f"customer not found: {customer_id}")
        return self._customers[customer_id]

    @TryAsync
    async def find_product(self, product_id: str) -> Product:
        await asyncio.sleep(0.01)
        if product_id not in self._products:
            raise KeyError(f"product not found: {product_id}")
        return self._products[product_id]

    @TryAsync
    async def save_order(self, order: Order) -> Order:
        await asyncio.sleep(0.01)
        return order


# ── Interpreter 2: In-memory (sync) ──────────────────────────────────


class InMemoryOrderRepo:
    def __init__(self):
        self.orders: list[Order] = []

    def find_customer(self, customer_id: str) -> Result[Customer]:
        customers = {"alice": Customer(id="alice", name="Alice", credit=500.0)}
        if customer_id not in customers:
            return Err(KeyError(f"customer not found: {customer_id}"))
        return Ok(customers[customer_id])

    def find_product(self, product_id: str) -> Result[Product]:
        products = {"widget": Product(id="widget", name="Widget Pro", price=49.99)}
        if product_id not in products:
            return Err(KeyError(f"product not found: {product_id}"))
        return Ok(products[product_id])

    def save_order(self, order: Order) -> Result[Order]:
        self.orders.append(order)
        return Ok(order)


# ── Interpreter 3: Always fails ──────────────────────────────────────


class FailingOrderRepo:
    def find_customer(self, customer_id: str) -> Result[Customer]:
        return Err(ConnectionError("database is down"))

    def find_product(self, product_id: str) -> Result[Product]:
        return Err(ConnectionError("database is down"))

    def save_order(self, order: Order) -> Result[Order]:
        return Err(ConnectionError("database is down"))


def main():
    print("=== Async 'Postgres' ===")

    async def run_async():
        repo = PostgresOrderRepo()
        print(
            f"  alice+widget: {await place_order(repo, AsyncResult, 'alice', 'widget')}"
        )
        print(
            f"  bob+laptop:   {await place_order(repo, AsyncResult, 'bob', 'laptop')}"
        )
        print(
            f"  nobody+widget: {await place_order(repo, AsyncResult, 'nobody', 'widget')}"
        )

    asyncio.run(run_async())

    print("\n=== Sync in-memory ===")
    repo = InMemoryOrderRepo()
    print(f"  alice+widget: {place_order(repo, Result, 'alice', 'widget')}")
    print(f"  nobody+widget: {place_order(repo, Result, 'nobody', 'widget')}")
    print(f"  saved orders: {len(repo.orders)}")

    print("\n=== Failing (DB down) ===")
    print(
        f"  alice+widget: {place_order(FailingOrderRepo(), Result, 'alice', 'widget')}"
    )


if __name__ == "__main__":
    main()
