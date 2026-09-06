"""Creation-site capture for error types.

In railway-oriented programming, errors are values (``Err(exception)``)
rather than raised exceptions. Python's traceback machinery only works
for raised exceptions — value-errors carry no stack trace. This makes
debugging monadic pipelines notoriously difficult: when an error surfaces,
you know *what* failed but not *where* it was created.

This module provides ``CapturesCreationSiteMixin`` — a mixin for frozen
dataclasses that captures lightweight metadata (filename, line number,
function name) at construction time. No ``import traceback``, no stack
walking — just ``sys._getframe()``, which is a single pointer lookup.

``Err`` and ``Left`` use this mixin automatically. Every error value
knows where it was created::

    from funstruct.monad.result import Err

    def validate_auth(req):
        if not req.valid:
            return Err(AuthError("invalid credentials"))

    err = validate_auth(bad_req)
    err.created_at
    # CreatedAt(filename='auth.py', lineno=4, funcname='validate_auth')
    str(err.created_at)
    # 'auth.py:4 in validate_auth'

Use in error handlers to log the error origin instead of the handler's
location::

    match result:
        case Err(e):
            LOG.error(
                f"{type(e).__qualname__}: {e}",
                filename=os.path.basename(result.created_at.filename),
                func_name=result.created_at.funcname,
                lineno=result.created_at.lineno,
            )

Add the mixin to your own frozen dataclasses::

    @dataclass(frozen=True)
    class MyError(CapturesCreationSiteMixin):
        message: str

    err = MyError("something broke")
    err.created_at  # CreatedAt(filename=..., lineno=..., funcname=...)
"""

import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class CreatedAt:
    """Where a value was constructed: filename, line number, function name."""

    filename: str
    lineno: int
    funcname: str

    def __str__(self) -> str:
        return f"{self.filename}:{self.lineno} in {self.funcname}"


def capture_created_at(depth: int = 3) -> CreatedAt:
    """Capture the creation site from the call stack.

    depth=3: capture_created_at → __post_init__ → __init__ → caller
    """
    frame = sys._getframe(depth)
    return CreatedAt(
        filename=frame.f_code.co_filename,
        lineno=frame.f_lineno,
        funcname=frame.f_code.co_name,
    )


class CapturesCreationSiteMixin:
    """Mixin for frozen dataclasses that captures where they were constructed.

    Add to any ``@dataclass(frozen=True)`` error type to automatically
    track its creation site. Access via ``instance.created_at``.

    Requires ``@dataclass`` — the capture relies on the dataclass-generated
    ``__init__`` calling ``__post_init__`` at a known stack depth.

    Used by ``Err`` and ``Left`` — every error value automatically knows
    where it was created, with negligible overhead.
    """

    def __post_init__(self):
        object.__setattr__(self, "_created_at", capture_created_at())

    @property
    def created_at(self) -> CreatedAt:
        """Where this instance was constructed."""
        return self._created_at


__all__ = ["CreatedAt", "CapturesCreationSiteMixin", "capture_created_at"]
