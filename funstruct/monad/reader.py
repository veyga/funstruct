"""Reader monad — computations that read from an environment.

>>> from funstruct.monad.reader import Reader
>>> greet = Reader(lambda name: f"hello {name}")
>>> greet.run("Alice")
'hello Alice'
>>> Reader.ask().map(lambda ctx: ctx.upper()).run("world")
'WORLD'
>>> Reader.pure(42).run("ignored")
42
"""

from _funstruct._reader import *  # noqa F403
