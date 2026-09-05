import asyncio
from funstruct.monad.option import Option, Nothing, Some
from funstruct.monad.future import Future
from dataclasses import dataclass


@dataclass
class User:
    name: str


@dataclass
class Address:
    street: str


def get_user(name: str) -> Future[Option[User]]:
    match name:
        case "me":
            return Future.pure(Some(User(name="me")))
        case _:
            return Future.pure(Nothing())


def get_address(user: User) -> Future[Option[Address]]:
    match user.name:
        case "me":
            return Future.pure(Some(Address(street="avalon")))
        case _:
            return Future.pure(Nothing())


@Future.do
def pipeline():
    user = yield get_user("me")
    address = yield get_address(user)
    return address.street


async def main():
    rax = await pipeline
    print(rax)


if __name__ == "__main__":
    asyncio.run(main())
