"""StateT — state monad transformer over any monad.

Examples:
    >>> from funstruct.monadtransformer import StateT
    >>> from funstruct.monad.either import Either, Right, Left
    >>> inc = StateT(lambda s: Right((s + 1, s)))
    >>> inc.run(0)
    Right((1, 0))
    >>> StateT.pure(42, Either).run(0)
    Right((0, 42))
    >>> inc.then(inc).run(0)
    Right((2, 1))
"""

from _funstruct._state_t import StateT as StateT
