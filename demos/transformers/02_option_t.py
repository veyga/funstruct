"""OptionT flattens nested Future[Option[A]] into a single pipeline.

Instead of nested pattern matching, OptionT lets you write a flat
pipeline that short-circuits on Nothing and awaits Futures automatically.

The key operations:
    OptionT(future_option)     — wrap a Future[Option[A]]
    OptionT.lift_f(future)     — lift a Future[A] → OptionT[Future, A]
    OptionT.from_option(opt, F) — lift an Option[A] → OptionT[F, A]
    .run()                     — unwrap back to Future[Option[A]]
"""

import asyncio

from funstruct.monad.option import Option, Some, Nothing
from funstruct.monad.future import Future
from funstruct.experimental.monadtransformer.option_t import OptionT
from funstruct.playground import User


def get_user(name: str) -> Future[Option[User]]:
    """Returns Future[Option[User]] — the messy nested type."""
    users = {"me": User(name="me")}
    return Future.pure(Option.from_optional(users.get(name)))


def get_age(user: User) -> Future[int]:
    """Returns Future[int] — no Option wrapper."""
    return Future.pure(3000 if user.name == "me" else 0)


def get_nick(user: User) -> Option[str]:
    """Returns Option[str] — no Future wrapper."""
    nicks = {"me": "andrew"}
    return Option.from_optional(nicks.get(user.name))


@OptionT.do
def get_profile() -> OptionT[Future, str]:
    """One flat pipeline — no nested pattern matching.

    OptionT handles the lifting between layers:
        OptionT(...)           for Future[Option[A]]
        OptionT.lift_f(...)    for Future[A]    (missing the Option)
        OptionT.from_option(., Future)  for Option[A]  (missing the Future)
    """
    user = yield OptionT(get_user("me"))
    age = yield OptionT.lift_f(get_age(user))
    nick = yield OptionT.from_option(get_nick(user), Future)
    return f"{nick}{age}"


@OptionT.do
def get_profile_missing() -> OptionT[Future, str]:
    """Short-circuits on Nothing — no explicit error handling needed."""
    user = yield OptionT(get_user("nobody"))
    age = yield OptionT.lift_f(get_age(user))
    nick = yield OptionT.from_option(get_nick(user), Future)
    return f"{nick}{age}"


async def main():
    print("=== OptionT: flat pipeline over Future[Option[A]] ===\n")

    result = await get_profile().run()
    print(f"  get_profile()         = {result}")

    result = await get_profile_missing().run()
    print(f"  get_profile_missing() = {result}")

    print("\n  No nested pattern matching!")
    print("  OptionT handles the lifting between layers.")
    print("  .run() unwraps back to Future[Option[A]] at the boundary.")


if __name__ == "__main__":
    asyncio.run(main())
