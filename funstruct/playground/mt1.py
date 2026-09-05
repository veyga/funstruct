import asyncio
import sys

from dataclasses import dataclass

from funstruct.monad.future import Future


@dataclass
class User:
    name: str


@dataclass
class Address:
    street: str


def get_user(name: str) -> Future[User]:
    match name:
        case "me":
            return Future.pure(User(name="me"))
        case _:
            return Future.pure(User(name="DNE"))


def get_address(user: User) -> Future[Address]:
    match user.name:
        case "me":
            return Future.pure(Address(street="avalon"))
        case _:
            return Future.pure(Address(street="DNE"))


def pipeline(username: str) -> Future[str]:
    @Future.do
    def _run():
        user = yield get_user(username)
        address = yield get_address(user)
        return address.street

    return _run


def __city(uname: str):
    user = yield get_user(uname)
    address = yield get_address(user)
    return address.street


city: Future[str] = Future.do(__city)

# @Future.do
# def city():
#     user = yield get_user(username)
#     address = yield get_address(user)
#     return address.street


async def main(username: str):
    rax = await pipeline(username)
    print(f"{rax = }")
    rdx = await city
    print(f"{rdx = }")


if __name__ == "__main__":
    username = sys.argv[1]
    print(f"getting user {username}")
    asyncio.run(main(username))
