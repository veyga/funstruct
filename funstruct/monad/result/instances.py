"""Typeclass instances for Result and AsyncResult."""

from __future__ import annotations

from funstruct.typeclasses._registry import register
from funstruct.typeclasses._typeclasses import Bifunctor, MonadError
from funstruct.monad.result import AsyncResult, Err, Ok, Result


class ResultMonadError(MonadError):

    def pure(self, value):
        return Ok(value)

    def bind(self, fa, f):
        match fa:
            case Ok(value):
                return f(value)
            case Err():
                return fa
            case _:
                raise TypeError(f"Expected Result, got {type(fa)}")

    def raise_error(self, error):
        return Err(error)

    def handle_error_with(self, fa, f):
        match fa:
            case Err(error):
                return f(error)
            case _:
                return fa


class ResultBifunctor(Bifunctor):

    def bimap(self, fa, f, g):
        match fa:
            case Ok(value):
                return Ok(g(value))
            case Err(error):
                return Err(f(error))


class AsyncResultMonadError(MonadError):

    def pure(self, value):
        return AsyncResult.pure(value)

    def bind(self, fa, f):
        return fa.bind(f)

    def raise_error(self, error):
        return AsyncResult.raise_error(error)

    def handle_error_with(self, fa, f):
        return fa.handle_error_with(f)


register(MonadError, Result, ResultMonadError())
register(Bifunctor, Result, ResultBifunctor())
register(MonadError, AsyncResult, AsyncResultMonadError())


__all__ = ["ResultMonadError", "ResultBifunctor", "AsyncResultMonadError"]
