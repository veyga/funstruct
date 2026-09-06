"""Demo: tagless final — write once, swap effects.

Tagless final abstracts over the effect type via a Protocol (algebra).
The program is written once against the protocol. Swap the interpreter
to change the effect — AsyncResult in prod, plain Result in tests.

When tagless final is worth it:
    - Swapping infrastructure (DB, cache, HTTP) without touching logic
    - Testing without mocking — hand in a pure interpreter
    - Deferring the effect choice to the caller

When it's NOT worth it:
    - Small services with one effect type (just use AsyncResult + @do)
    - When the algebra has one implementation and always will

Run: uv run python demos/03_tagless_final_intro.py
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from funstruct.monad.result import AsyncResult, Err, Ok, Result, TryAsync


@dataclass
class User:
    name: str


# ── Algebra (the interface) ──────────────────────────────────────────


@runtime_checkable
class UserRepo[F](Protocol):
    def get_user(self, name: str) -> F[User]: ...
    def get_age(self, user: User) -> F[int]: ...
    def get_nickname(self, user: User) -> F[str]: ...


# ── Program (generic in F) ───────────────────────────────────────────


def get_profile[F](repo: UserRepo[F], F: type[F], username: str) -> F[str]:
    @F.do
    def run():
        user = yield repo.get_user(username)
        age = yield repo.get_age(user)
        nickname = yield repo.get_nickname(user)
        return f"{nickname} (age {age})"

    return run()


# ── Interpreter 1: AsyncResult (production) ──────────────────────────


class AsyncResultUserRepo:
    @TryAsync
    def get_user(self, name: str) -> User:
        users = {"alice": User(name="alice"), "bob": User(name="bob")}
        if not (user := users.get(name)):
            raise ValueError(f"unknown user: {name}")
        return user

    def get_age(self, user: User) -> AsyncResult[int]:
        return AsyncResult.pure(30 if user.name == "alice" else 25)

    @TryAsync
    def get_nickname(self, user: User) -> str:
        return {"alice": "ally", "bob": "bobby"}[user.name]


# ── Interpreter 2: Result (testing) ──────────────────────────────────


class ResultUserRepo:
    def get_user(self, name: str) -> Result[User]:
        return Ok(User(name=name))

    def get_age(self, user: User) -> Result[int]:
        return Ok(99)

    def get_nickname(self, user: User) -> Result[str]:
        return Ok("test_nick")


def main():
    print("=== Production (AsyncResult) ===")
    repo = AsyncResultUserRepo()

    async def run_async():
        print(f"  alice: {await get_profile(repo, AsyncResult, 'alice')}")
        print(f"  bob:   {await get_profile(repo, AsyncResult, 'bob')}")
        print(f"  nobody: {await get_profile(repo, AsyncResult, 'nobody')}")

    asyncio.run(run_async())

    print("\n=== Testing (Result, sync, no IO) ===")
    test_repo = ResultUserRepo()
    print(f"  alice: {get_profile(test_repo, Result, 'alice')}")
    print(f"  bob:   {get_profile(test_repo, Result, 'bob')}")


if __name__ == "__main__":
    main()
