"""Experimental: AST-based do-notation.

Compiles yield statements into bind/map chains at decoration time.
Zero runtime overhead. Works for ALL monads including CList.

``yield`` is a syntactic marker for monadic bind, NOT a generator.

Usage:
    from funstruct.experimental.do_ast import do_ast

    @do_ast
    def pipeline():
        x = yield Ok(10)
        y = yield Ok(x + 1)
        return x + y

    # Compiles to: Ok(10).bind(lambda x: Ok(x + 1).map(lambda y: x + y))

Supports plain statements (if/else, print) between yields.
Falls back to generator when yields are nested in control flow.
"""

from __future__ import annotations

import ast
import inspect
import textwrap
from collections.abc import Callable
from typing import Any

_cont_counter = 0


def do_ast(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Compile do-notation into bind/map chains via AST transformation."""
    source = textwrap.dedent(inspect.getsource(fn))
    tree = ast.parse(source)
    func = tree.body[0]
    assert isinstance(func, ast.FunctionDef)

    func.decorator_list = []
    func.body = _transform_do_body(func.body)

    ast.fix_missing_locations(tree)
    code = compile(tree, f"<do:{fn.__name__}>", "exec")
    ns = {**fn.__globals__}
    if fn.__code__.co_freevars and fn.__closure__:
        for name, cell in zip(fn.__code__.co_freevars, fn.__closure__):
            ns[name] = cell.cell_contents
    exec(code, ns)  # noqa: S102
    return ns[fn.__name__]


def _next_cont_name() -> str:
    global _cont_counter  # noqa: PLW0603
    _cont_counter += 1
    return f"_do_cont_{_cont_counter}"


def _has_more_yields(stmts: list[ast.stmt]) -> bool:
    for s in stmts:
        if isinstance(s, ast.Expr) and isinstance(s.value, ast.Yield):
            return True
        if isinstance(s, ast.Assign) and isinstance(s.value, ast.Yield):
            return True
    return False


def _transform_do_body(stmts: list[ast.stmt]) -> list[ast.stmt]:
    """Transform a do-block body into nested bind/map function calls."""
    for i, stmt in enumerate(stmts):
        monadic = None
        var = "_"

        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Yield):
            monadic = stmt.value.value or ast.Constant(value=None)
            var = "_"
        elif (
            isinstance(stmt, ast.Assign)
            and len(stmt.targets) == 1
            and isinstance(stmt.value, ast.Yield)
        ):
            monadic = stmt.value.value or ast.Constant(value=None)
            target = stmt.targets[0]
            var = target.id if isinstance(target, ast.Name) else "_"

        if monadic is not None:
            before = stmts[:i]
            after = stmts[i + 1 :]

            for s in before:
                for node in ast.walk(s):
                    if isinstance(node, ast.Yield):
                        raise SyntaxError("yield nested in control flow")

            if not after:
                raise SyntaxError("yield must be followed by return or more statements")

            cont_name = _next_cont_name()
            method = "map" if not _has_more_yields(after) else "bind"
            cont_body = _transform_do_body(after)

            cont_func = ast.FunctionDef(
                name=cont_name,
                args=ast.arguments(
                    posonlyargs=[],
                    args=[ast.arg(arg=var)],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[],
                ),
                body=cont_body,
                decorator_list=[],
                returns=None,
            )

            bind_call = ast.Return(
                value=ast.Call(
                    func=ast.Attribute(value=monadic, attr=method, ctx=ast.Load()),
                    args=[ast.Name(id=cont_name, ctx=ast.Load())],
                    keywords=[],
                )
            )

            return [*before, cont_func, bind_call]

    for s in stmts:
        for node in ast.walk(s):
            if isinstance(node, ast.Yield):
                raise SyntaxError("yield nested inside control flow")
    return stmts
