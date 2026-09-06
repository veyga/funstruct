"""Demo: do-notation — generator-based monadic sequencing.

@do turns a generator function into a monadic pipeline.
yield extracts the value from each monadic step; short-circuits on failure.

Key rules:
    - @Result.do / @Option.do uses generators (def + yield), NOT async/await
    - You cannot decorate an async def with @do
    - @AsyncResult.do handles async values (awaits internally)
    - To mix sync Result into @AsyncResult.do, use AsyncResult.from_result()

Equivalent styles:
    @AsyncResult.do         — decorator style (recommended)
    AsyncResult.do(gen_fn)  — manual style (returns thunk)

Run: uv run python demos/02_do_notation.py
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from funstruct.monad.result import AsyncResult, Ok, Err, Result, Try, TryAsync


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


@Try
def get_age_sync(user: User) -> int:
    return 30 if user.name == "alice" else 0


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


# ── Style 2: manual do (pass generator function) ────────────────────


def _profile_gen():
    user = yield get_user("alice")
    age = yield get_age(user)
    nickname = yield get_nickname(user)
    return f"{nickname} (age {age})"


get_profile_manual = AsyncResult.do(_profile_gen)


# ── Style 3: sync do-notation with Result ────────────────────────────


@Result.do
def sync_pipeline():
    x = yield Ok(10)
    y = yield Ok(x + 1)
    z = yield Ok(y * 2)
    return z


# ── Style 4: mixing sync Result into async do ───────────────────────


@AsyncResult.do
def mixed_pipeline():
    user = yield get_user("alice")
    age = yield AsyncResult.from_result(get_age_sync(user))  # lift sync → async
    nickname = yield get_nickname(user)
    return f"{nickname} (age {age})"


# ── Short-circuit on error ───────────────────────────────────────────


@AsyncResult.do
def failing_pipeline():
    user = yield get_user("nobody")  # fails here
    age = yield get_age(user)  # never reached
    return f"age: {age}"


def main():
    async def run():
        print("=== @AsyncResult.do (decorator) ===")
        print(f"  {await get_profile_decorated()}")

        print("\n=== AsyncResult.do(gen_fn) (manual) ===")
        print(f"  {await get_profile_manual()}")

        print("\n=== @Result.do (sync) ===")
        print(f"  {sync_pipeline()}")

        print("\n=== Mixed sync/async ===")
        print(f"  {await mixed_pipeline()}")

        print("\n=== Short-circuit on error ===")
        print(f"  {await failing_pipeline()}")

    asyncio.run(run())


if __name__ == "__main__":
    main()
