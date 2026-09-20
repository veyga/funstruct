"""Run funstruct's summon checker on this repo's own code."""

from __future__ import annotations

import funstruct.types.cons  # noqa: F401
import funstruct.types.either  # noqa: F401
import funstruct.types.frozendict  # noqa: F401
import funstruct.types.future  # noqa: F401

# Import all modules to trigger instance registration
import funstruct.types.option  # noqa: F401
import funstruct.types.reader  # noqa: F401
import funstruct.types.result  # noqa: F401
import funstruct.types.state  # noqa: F401
import funstruct.types.tree  # noqa: F401
import funstruct.types.validated  # noqa: F401
import funstruct.types.writer  # noqa: F401
import funstruct.types.ziplist  # noqa: F401
from funstruct.check import check_summon

result = check_summon(paths=["funstruct"])
result.exit()
