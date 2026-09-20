"""Run funstruct's summon checker on this repo's own code."""

from __future__ import annotations

import funstruct.applicative.validated  # noqa: F401
import funstruct.applicative.ziplist  # noqa: F401
import funstruct.collections.cons  # noqa: F401
import funstruct.collections.frozendict  # noqa: F401
import funstruct.collections.tree  # noqa: F401
import funstruct.monad.either  # noqa: F401
import funstruct.monad.future  # noqa: F401

# Import all modules to trigger instance registration
import funstruct.monad.option  # noqa: F401
import funstruct.monad.reader  # noqa: F401
import funstruct.monad.result  # noqa: F401
import funstruct.monad.state  # noqa: F401
import funstruct.monad.writer  # noqa: F401
from funstruct.check import check_summon

result = check_summon(paths=["funstruct"])
result.exit()
