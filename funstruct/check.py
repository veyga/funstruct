"""Static verification that summon() calls can resolve.

Imports the caller's modules (triggering instance registration), then
scans source files for ``summon(X, Y)`` call sites and verifies each
``(X, Y)`` pair exists in the registry.

Usage from the command line::

    funstruct-check --import myapp.instances src/

Usage from Python::

    from funstruct.check import check_summon

    result = check_summon(
        paths=["src/"],
        imports=["myapp.instances"],
    )
    result.exit()   # sys.exit(1) if failures found

Or as a pytest fixture::

    def test_summon_resolution():
        result = check_summon(paths=["src/"], imports=["myapp.instances"])
        assert result.ok, result.report()
"""

from __future__ import annotations

import ast
import importlib
import sys
from dataclasses import dataclass, field
from pathlib import Path

from funstruct.typeclasses.utils.registry import _registry


@dataclass
class CheckResult:
    """Result of a summon resolution check."""

    errors: list[tuple[Path, int, str, str]] = field(default_factory=list)
    registered_count: int = 0

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    def report(self) -> str:
        if self.ok:
            return f"All summon() calls resolve. ({self.registered_count} instances registered)"
        lines = [f"Found {len(self.errors)} unresolvable summon() calls:\n"]
        for path, line, tc, typ in self.errors:
            lines.append(
                f"  {path}:{line}: summon({tc}, {typ}) — no instance registered"
            )
        return "\n".join(lines)

    def exit(self) -> None:
        print(self.report())
        sys.exit(0 if self.ok else 1)


def _get_registered_pairs() -> set[tuple[str, str]]:
    pairs = set()
    for tc, t in _registry:
        pairs.add((tc.__name__, t.__name__))
        for base in tc.__mro__[1:]:
            if hasattr(base, "__abstractmethods__"):
                pairs.add((base.__name__, t.__name__))
    return pairs


def _lines_inside_pytest_raises(tree: ast.Module) -> set[int]:
    suppressed = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.With):
            continue
        for item in node.items:
            ctx = item.context_expr
            if (
                isinstance(ctx, ast.Call)
                and isinstance(ctx.func, ast.Attribute)
                and ctx.func.attr == "raises"
            ):
                for child in ast.walk(node):
                    if hasattr(child, "lineno"):
                        suppressed.add(child.lineno)
    return suppressed


def _collect_concrete_types(tree: ast.Module) -> set[str]:
    """Names that are concrete types: class definitions and imports."""
    types = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            types.add(node.name)
        elif isinstance(node, ast.ImportFrom) and node.names:
            for alias in node.names:
                types.add(alias.asname or alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name
                types.add(name.split(".")[-1])
    return types


def _find_summon_calls(path: Path) -> list[tuple[int, str, str, set[str]]]:
    """Find summon(X, Y) calls. Returns [(line, tc, type, concrete_types)]."""
    try:
        source = path.read_text()
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError):
        return []

    suppressed = _lines_inside_pytest_raises(tree)
    concrete = _collect_concrete_types(tree)

    calls = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "summon"
            and len(node.args) >= 2
        ):
            if node.lineno in suppressed:
                continue
            tc_arg = node.args[0]
            type_arg = node.args[1]
            if isinstance(tc_arg, ast.Name) and isinstance(type_arg, ast.Name):
                calls.append((node.lineno, tc_arg.id, type_arg.id, concrete))
    return calls


def check_summon(
    paths: list[str | Path],
    imports: list[str] | None = None,
) -> CheckResult:
    """Check that all summon() calls in the given paths can resolve.

    Args:
        paths: Directories or files to scan for summon() calls.
        imports: Module names to import before checking. Importing your
                 instance modules triggers their ``for_type=`` registration.
                 If None, only funstruct's built-in instances are available.

    Returns:
        CheckResult with errors (if any) and the registered instance count.
    """
    for mod_name in imports or []:
        importlib.import_module(mod_name)

    registered = _get_registered_pairs()
    registered_tcs = {tc for tc, _ in registered}

    errors = []
    for p in paths:
        root = Path(p)
        py_files = root.rglob("*.py") if root.is_dir() else [root]
        for path in py_files:
            if "__pycache__" in str(path):
                continue
            for line, tc, typ, concrete in _find_summon_calls(path):
                if tc not in registered_tcs and tc not in concrete:
                    continue
                if typ not in concrete:
                    continue
                if (tc, typ) not in registered:
                    errors.append((path, line, tc, typ))

    return CheckResult(errors=errors, registered_count=len(registered))


def main():
    """CLI entry point: ``funstruct-check [--import mod] path [path ...]``."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="funstruct-check",
        description="Verify all summon() calls can resolve against the typeclass registry.",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="Directories or files to scan for summon() calls",
    )
    parser.add_argument(
        "--import",
        "-i",
        dest="imports",
        action="append",
        default=[],
        help="Module to import before checking (triggers instance registration). Repeatable.",
    )
    args = parser.parse_args()
    result = check_summon(paths=args.paths, imports=args.imports)
    result.exit()


if __name__ == "__main__":
    main()
