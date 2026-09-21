"""Representable instance for Result and AsyncResult."""

from __future__ import annotations

from funstruct.typeclasses.representable import Representable
from funstruct.types.result import AsyncResult, Err, Ok, Result


class _ResultRepresentable(Representable, for_type=Result):
    def represent(self, a) -> str:
        match a:
            case Ok(v):
                return f"Ok({repr(v)})"
            case Err(e):
                return f"Err({repr(e)})"
            case _:
                return f"Result({a})"


class _AsyncResultRepresentable(Representable, for_type=AsyncResult):
    def represent(self, a) -> str:
        return f"AsyncResult({a._coro})"
