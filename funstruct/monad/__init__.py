"""Monad types."""

from _funstruct._either import Either as Either
from _funstruct._either import Left as Left
from _funstruct._either import Right as Right
from _funstruct._option import Nothing as Nothing
from _funstruct._option import Option as Option
from _funstruct._option import Some as Some
from _funstruct._reader import Reader as Reader

# Re-export transformers for convenience (canonical home: funstruct.monadtransformer)
from _funstruct._reader_t import ReaderT as ReaderT
from _funstruct._result import Err as Err
from _funstruct._result import Ok as Ok
from _funstruct._result import Result as Result
from _funstruct._result import Try as Try
from _funstruct._state import State as State
from _funstruct._state_t import StateT as StateT
from _funstruct._writer import Writer as Writer
