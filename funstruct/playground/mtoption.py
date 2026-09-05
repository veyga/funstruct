import asyncio
import sys
from funstruct.monad.option import Option, Nothing, Some
from funstruct.monad.future import Future
from dataclasses import dataclass


@dataclass
class User:
    name: str


@dataclass
class Address:
    street: str


def __get_user(name: str) -> Future[Option[User]]:
    users = {"me": User(name="me")}
    return Future.pure(Option.from_optional(users.get(name)))


def __get_address(user: User) -> Future[Option[Address]]:
    match user.name:
        case "me":
            return Future.pure(Some(Address(street="avalon")))
        case _:
            return Future.pure(Nothing())


def pipeline(username: str) -> Future[Option[str]]:
    @Future.do
    def _run():
        user = yield __get_user(username)
        address = yield __get_address(user)
        return address.street

    return _run


# OR can write it this way
def __city():
    user = yield __get_user(username)
    address = yield __get_address(user)
    return address.street


city: Future[Option[str]] = Future.do(__city)


async def main(username: str):
    rax = await pipeline(username)
    print(rax)


if __name__ == "__main__":
    username = sys.argv[1]
    # printf"getting user {username}")
    asyncio.run(main(username))
