"""The problem: nested monads are painful to compose.

When your functions return different monadic types, you end up with
nested pattern matching at every step.

    get_user(name) -> Future[Option[User]]   # might not exist, async
    get_age(user)  -> Future[int]            # always succeeds, async
    get_nick(user) -> Option[str]            # might not exist, sync

Composing these requires unwrapping at every layer:

    result = await get_user("me")   # Future[Option[User]]
    match result:
        case Some(user):
            age = await get_age(user)    # Future[int] — different shape!
            match get_nick(user):        # Option[str] — yet another shape!
                case Some(nick): ...
                case Nothing(): ...
        case Nothing(): ...

Three functions, three layers of nesting. This doesn't scale.
"""

import asyncio

from funstruct.monad.option import Option, Some, Nothing
from funstruct.monad.future import Future
from funstruct.playground import User


def get_user(name: str) -> Future[Option[User]]:
    users = {"me": User(name="me")}
    return Future.pure(Option.from_optional(users.get(name)))


def get_age(user: User) -> Future[int]:
    return Future.pure(3000 if user.name == "me" else 0)


def get_nick(user: User) -> Option[str]:
    nicks = {"me": "andrew"}
    return Option.from_optional(nicks.get(user.name))


async def main():
    print("=== The nested monad problem ===\n")

    # Composing these is painful — nested pattern matching at every step
    user_opt = await get_user("me")
    match user_opt:
        case Some(user):
            age = await get_age(user)
            match get_nick(user):
                case Some(nick):
                    print(f"  Found: {nick}{age}")
                case Nothing():
                    print("  No nickname")
        case Nothing():
            print("  User not found")

    # Now try with a missing user — same nesting
    user_opt = await get_user("nobody")
    match user_opt:
        case Some(user):
            print(f"  Found: {user}")
        case Nothing():
            print("  User 'nobody' not found (expected)")

    print("\n  Problem: 3 functions, 3 layers of nesting.")
    print("  Solution: monad transformers (see 03_option_t.py)")
    print("  Alternative: use one monad type everywhere (see 04_alternative.py)")


if __name__ == "__main__":
    asyncio.run(main())
