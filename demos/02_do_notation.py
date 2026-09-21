"""Demo: do-notation — generator-based monadic sequencing.

@do turns a generator function into a monadic pipeline.
yield extracts the value from each monadic step

Key rules:
    - @Result.do / @Option.do uses generators (def + yield), NOT async/await
    - You cannot decorate an async def with @do
    - @AsyncResult.do handles async values (awaits internally)
    - To mix sync values into @AsyncResult.do, use AsyncResult.pure()

Equivalent styles:
    @AsyncResult.do         — decorator style (recommended)
    AsyncResult.do(gen_fn)  — manual style (returns thunk)

Run: uv run python demos/02_do_notation.py
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from demos._util import header
from funstruct.types.result import AsyncResult, Ok, Result, TryAsync


@dataclass
class User:
    name: str


@TryAsync
def get_user(name: str) -> User:
    users = {"alice": User(name="alice")}
    if not (user := users.get(name)):
        raise ValueError(f"unknown user: {name}")
    return user


def get_age(user: User) -> AsyncResult[int]:
    return AsyncResult.pure(30 if user.name == "alice" else 0)



@TryAsync
def get_nickname(user: User) -> str:
    nicknames = {"alice": "ally"}
    return nicknames[user.name]


# ── Style 1: @AsyncResult.do decorator (recommended) ────────────────


@AsyncResult.do
def get_profile_decorated():
    user = yield get_user("alice")
    age = yield get_age(user)
    nickname = yield get_nickname(user)
    return f"{nickname} (age {age})"


# ── Style 2: @do with arguments ─────────────────────────────────────


@AsyncResult.do
def get_profile_for(username: str):
    user = yield get_user(username)
    age = yield get_age(user)
    nickname = yield get_nickname(user)
    return f"{nickname} (age {age})"


# ── Style 3: manual do (pass generator function) ────────────────────


def _profile_gen():
    user = yield get_user("alice")
    age = yield get_age(user)
    nickname = yield get_nickname(user)
    return f"{nickname} (age {age})"


get_profile_manual = AsyncResult.do(_profile_gen)


# ── Style 4: sync do-notation with Result ────────────────────────────


@Result.do
def sync_pipeline():
    x = yield Ok(10)
    y = yield Ok(x + 1)
    z = yield Ok(y * 2)
    return z


# ── Short-circuit on error ───────────────────────────────────────────


@AsyncResult.do
def failing_pipeline():
    user = yield get_user("nobody")  # fails here
    age = yield get_age(user)  # never reached
    return f"age: {age}"


# ── Style 5: CList do-notation (list comprehension) ────────────────

from dataclasses import dataclass as dc

from funstruct.types.cons import CList


@dc(frozen=True)
class UserRow:
    id: int
    name: str


@dc(frozen=True)
class OrderRow:
    user_id: int
    total: float


users = CList.from_iterable([UserRow(1, "Alice"), UserRow(2, "Bob")])
orders = CList.from_iterable([
    OrderRow(1, 49.99), OrderRow(1, 12.00), OrderRow(2, 99.99),
])


@CList.do
def user_orders():
    user = yield users
    order = yield orders
    yield CList.from_iterable([()] if order.user_id == user.id else [])
    return f"{user.name}: ${order.total:.2f}"


def main():
    async def run():
        header("@AsyncResult.do (decorator)")
        print(f"  {await get_profile_decorated()}")

        header("@AsyncResult.do with args")
        print(f"  alice:  {await get_profile_for('alice')}")
        print(f"  nobody: {await get_profile_for('nobody')}")

        header("AsyncResult.do(gen_fn) (manual)")
        print(f"  {await get_profile_manual()}")

        header("@Result.do (sync)")
        print(f"  {sync_pipeline()}")

        header("Short-circuit on error")
        print(f"  {await failing_pipeline()}")

    asyncio.run(run())

    header("CList.do (list comprehension / join)")
    for row in user_orders():
        print(f"  {row}")


if __name__ == "__main__":
    main()
