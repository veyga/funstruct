"""AST-based do-notation — compiles yield statements into bind/map chains.

Transforms at decoration time (zero runtime overhead):

    @do_ast
    def pipeline():
        x = yield xs
        y = yield ys
        return (x, y)

Becomes:

    def pipeline():
        return xs.bind(lambda x: ys.map(lambda y: (x, y)))

Works for ALL monads including CList. No generators at runtime.
"""

from __future__ import annotations

import ast
import inspect
import textwrap
from collections.abc import Callable
from typing import Any


def do_ast(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Compile do-notation into bind/map chains via AST transformation."""
    source = textwrap.dedent(inspect.getsource(fn))
    tree = ast.parse(source)
    func: ast.FunctionDef = tree.body[0]  # type: ignore[assignment]

    func.decorator_list = []

    body_expr = _transform(func.body)
    func.body = [ast.Return(value=body_expr)]

    ast.fix_missing_locations(tree)
    code = compile(tree, f"<do:{fn.__name__}>", "exec")
    ns = {**fn.__globals__}
    if fn.__code__.co_freevars and fn.__closure__:
        for name, cell in zip(fn.__code__.co_freevars, fn.__closure__):
            ns[name] = cell.cell_contents
    exec(code, ns)  # noqa: S102
    return ns[fn.__name__]


def _transform(stmts: list[ast.stmt]) -> ast.expr:
    if not stmts:
        raise SyntaxError("Empty do block")

    first = stmts[0]
    rest = stmts[1:]

    if isinstance(first, ast.Return):
        return first.value or ast.Constant(value=None)

    # yield expr (no assignment) — guard
    if isinstance(first, ast.Expr) and isinstance(first.value, ast.Yield):
        monadic = first.value.value or ast.Constant(value=None)
        if not rest:
            raise SyntaxError("yield without return")
        inner = _transform(rest)
        is_last = len(rest) == 1 and isinstance(rest[0], ast.Return)
        return _call(monadic, "_", inner, is_last)

    # x = yield expr — bind
    if (
        isinstance(first, ast.Assign)
        and len(first.targets) == 1
        and isinstance(first.value, ast.Yield)
    ):
        monadic = first.value.value or ast.Constant(value=None)
        target = first.targets[0]
        var = target.id if isinstance(target, ast.Name) else "_"
        if not rest:
            raise SyntaxError("yield without return")
        inner = _transform(rest)
        is_last = len(rest) == 1 and isinstance(rest[0], ast.Return)
        return _call(monadic, var, inner, is_last)

    raise SyntaxError(
        f"Unsupported in do block (only yield/return allowed): "
        f"{ast.dump(first)}"
    )


def _call(monadic: ast.expr, var: str, body: ast.expr, is_last: bool) -> ast.expr:
    method = "map" if is_last else "bind"
    return ast.Call(
        func=ast.Attribute(value=monadic, attr=method, ctx=ast.Load()),
        args=[
            ast.Lambda(
                args=ast.arguments(
                    posonlyargs=[],
                    args=[ast.arg(arg=var)],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[],
                ),
                body=body,
            )
        ],
        keywords=[],
    )
