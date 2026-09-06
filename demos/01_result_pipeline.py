"""Demo: AsyncResult pipeline — composing async operations that can fail.

Shows two equivalent ways to build a pipeline:
    1. Bind chains: .bind(lambda x: ...).map(lambda x: ...)
    2. >> operator: pipeline >> next_step

Both short-circuit on the first Err.

Run: uv run python demos/01_result_pipeline.py
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from funstruct.monad.result import AsyncResult, Err, Ok, TryAsync


@dataclass
class User:
    name: str


@TryAsync
def get_user(name: str) -> User:
    users = {"alice": User(name="alice"), "bob": User(name="bob")}
    if not (user := users.get(name)):
        raise ValueError(f"unknown user: {name}")
    return user


def get_age(user: User) -> AsyncResult[int]:
    ages = {"alice": 30, "bob": 25}
    return AsyncResult.pure(ages.get(user.name, 0))


@TryAsync
def get_nickname(user: User) -> str:
    nicknames = {"alice": "ally", "bob": "bobby"}
    return nicknames[user.name]


# Style 1: bind chain
def get_profile_bind(username: str) -> AsyncResult[str]:
    return get_user(username).bind(
        lambda user: get_age(user).bind(
            lambda age: get_nickname(user).map(lambda nick: f"{nick} (age {age})")
        )
    )


# Style 2: >> operator
def get_age_only(username: str) -> AsyncResult[int]:
    return get_user(username) >> get_age


def main():
    async def run():
        print("=== Bind chain ===")
        print(f"  alice: {await get_profile_bind('alice')}")
        print(f"  bob:   {await get_profile_bind('bob')}")
        print(f"  nobody: {await get_profile_bind('nobody')}")

        print("\n=== >> operator ===")
        print(f"  alice age: {await get_age_only('alice')}")

    asyncio.run(run())


if __name__ == "__main__":
    main()
