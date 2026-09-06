"""Alternative: skip transformers by using one monad type everywhere.

Instead of composing Future[Option[A]] with OptionT, make ALL functions
return the same type — AsyncResult[A]. Then composition is just .bind().

This is often simpler than transformers for real applications.

    get_user(name) -> AsyncResult[User]
    get_age(user)  -> AsyncResult[int]
    get_nick(user) -> AsyncResult[str]

    @AsyncResult.do
    def pipeline():
        user = yield get_user("me")
        age = yield get_age(user)
        nick = yield get_nick(user)
        return f"{nick}{age}"

No lifting, no transformers, no .run(). Just bind.
"""

import asyncio

from funstruct.monad.result import AsyncResult, Ok, Err, TryAsync
from funstruct.playground import User


@TryAsync
def get_user(name: str) -> User:
    users = {"me": User(name="me")}
    if not (user := users.get(name)):
        raise ValueError(f"user not found: {name}")
    return user


def get_age(user: User) -> AsyncResult[int]:
    return AsyncResult.pure(3000 if user.name == "me" else 0)


@TryAsync
def get_nick(user: User) -> str:
    nicks = {"me": "andrew"}
    return nicks[user.name]


@AsyncResult.do
def get_profile():
    """All functions return AsyncResult — composition is just yield."""
    user = yield get_user("me")
    age = yield get_age(user)
    nick = yield get_nick(user)
    return f"{nick}{age}"


def get_profile_bind() -> AsyncResult[str]:
    """Same thing with explicit bind chains."""
    return (
        get_user("me")
        .bind(lambda user: get_age(user)
        .bind(lambda age: get_nick(user)
        .map(lambda nick: f"{nick}{age}")))
    )


async def main():
    print("=== Alternative: one monad type everywhere ===\n")

    result = await get_profile()
    print(f"  @do style:   {result}")

    result = await get_profile_bind()
    print(f"  bind chains: {result}")

    result = await get_user("nobody")
    print(f"  missing user: {result}")

    print("\n  No transformers, no lifting, no .run().")
    print("  Tradeoff: every function must return AsyncResult.")
    print("  For most applications, this is simpler than transformers.")


if __name__ == "__main__":
    asyncio.run(main())
