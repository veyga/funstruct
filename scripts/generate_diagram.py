"""Generate the typeclass hierarchy SVG from the actual code.

Introspects the typeclass hierarchy, data types, and registered instances
to produce docs/typeclasses.svg automatically.

Usage:
    uv run python scripts/generate_diagram.py
    # or: just diagram-gen
"""

from __future__ import annotations

import importlib
import pkgutil

# Force all modules to load so instances register
import funstruct.monad.option
import funstruct.monad.either
import funstruct.monad.result
import funstruct.monad.state
import funstruct.monad.reader
import funstruct.monad.writer
import funstruct.monad.future
import funstruct.collections.cons
import funstruct.collections.tree
import funstruct.collections.frozendict
import funstruct.applicative.validated
import funstruct.applicative.ziplist

from funstruct.typeclasses.typeclass import BaseTypeclass
from funstruct.typeclasses.mixins.data_type import DataType
from funstruct.typeclasses.utils.registry import _registry


def discover_typeclasses() -> dict[type, list[type]]:
    """Walk the typeclass hierarchy. Returns {parent: [children]}."""
    tree: dict[type, list[type]] = {}

    def walk(cls):
        children = [
            c for c in cls.__subclasses__()
            if c.__module__.startswith("funstruct.typeclasses")
        ]
        if children:
            tree[cls] = children
        for child in children:
            walk(child)

    walk(BaseTypeclass)
    return tree


def discover_data_types() -> list[type]:
    """Find all data types (DataType subclasses with _type_constructor)."""
    seen = set()
    result = []

    def walk(cls):
        for sub in cls.__subclasses__():
            tc = getattr(sub, "_type_constructor", None)
            if tc and tc not in seen and tc is sub:
                seen.add(tc)
                result.append(tc)
            walk(sub)

    walk(DataType)
    return sorted(result, key=lambda c: c.__name__)


def discover_instances() -> list[tuple[str, str]]:
    """Get all registered (typeclass_name, data_type_name) pairs."""
    pairs = []
    for (tc, dt), inst in _registry.items():
        pairs.append((tc.__name__, dt.__name__))
    return sorted(set(pairs))


def classify_typeclass(cls) -> str:
    """Assign a group color based on the typeclass family."""
    name = cls.__name__
    if name in ("Semigroup", "Monoid"):
        return "algebraic"
    if name in ("Foldable", "Traversable", "Bifunctor"):
        return "structural"
    return "computational"


COLORS = {
    "algebraic": {"bg": "#fff0f5", "border": "#e8a0b8", "box": "#ff99ca", "text": "#fff", "label": "#c06080"},
    "structural": {"bg": "#f0f5ff", "border": "#a0b8e8", "box": "#77afff", "text": "#fff", "label": "#6080c0"},
    "computational": {"bg": "#f5fff0", "border": "#90c890", "box": "#7acc7a", "text": "#fff", "label": "#508050"},
}

SPECIAL_COLORS = {
    "MonadError": {"box": "#e8a050", "border": "#c08030"},
    "Alternative": {"box": "#a0dca0", "border": "#70b070"},
    "Bifunctor": {"box": "#cadfff", "border": "#90b0e0", "text": "#4060a0"},
}


def generate_svg() -> str:
    tree = discover_typeclasses()
    data_types = discover_data_types()
    instances = discover_instances()

    # Collect all typeclasses
    all_tcs = set()
    for parent, children in tree.items():
        all_tcs.add(parent)
        all_tcs.update(children)

    # Add Semigroup/Monoid (value-level typeclasses, not BaseTypeclass subclasses)
    from funstruct.typeclasses.semigroup import Semigroup
    from funstruct.typeclasses.monoid import Monoid
    all_tcs.add(Semigroup)
    all_tcs.add(Monoid)

    # Group typeclasses
    groups: dict[str, list[type]] = {"algebraic": [], "structural": [], "computational": []}
    for tc in all_tcs:
        if tc is BaseTypeclass:
            continue
        groups[classify_typeclass(tc)].append(tc)
    for g in groups.values():
        g.sort(key=lambda c: c.__name__)

    # Build hierarchy edges
    edges = []
    for parent, children in tree.items():
        for child in children:
            if parent is not BaseTypeclass:
                edges.append((parent.__name__, child.__name__))
    edges.append(("Semigroup", "Monoid"))

    lines = []
    lines.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 620" font-family="\'SF Mono\', monospace" font-size="13">')
    lines.append('  <defs>')
    lines.append('    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">')
    lines.append('      <path d="M 0 0 L 10 5 L 0 10 z" fill="#666"/>')
    lines.append('    </marker>')
    lines.append('    <filter id="shadow" x="-2%" y="-2%" width="104%" height="104%"><feDropShadow dx="1" dy="1" stdDeviation="2" flood-opacity="0.1"/></filter>')
    lines.append('  </defs>')
    lines.append('  <rect width="900" height="620" fill="#1a1a2e" rx="8"/>')
    lines.append(f'  <text x="450" y="35" text-anchor="middle" font-size="20" font-weight="bold" fill="#e0e2e4">funstruct — typeclass hierarchy</text>')
    lines.append(f'  <text x="450" y="52" text-anchor="middle" font-size="11" fill="#666">auto-generated from code • {len(all_tcs)-1} typeclasses • {len(data_types)} data types • {len(instances)} instances</text>')

    # Typeclass boxes — positioned manually per group for good layout
    tc_positions = {}
    # Algebraic
    for i, tc in enumerate(groups["algebraic"]):
        x, y = 65, 108 + i * 52
        tc_positions[tc.__name__] = (130, y + 17)
        c = SPECIAL_COLORS.get(tc.__name__, COLORS["algebraic"])
        lines.append(f'  <rect x="{x}" y="{y}" width="130" height="34" rx="6" fill="{c.get("box", COLORS["algebraic"]["box"])}" stroke="{c.get("border", COLORS["algebraic"]["border"])}"/>')
        lines.append(f'  <text x="{x+65}" y="{y+22}" text-anchor="middle" font-weight="bold" fill="{c.get("text", "#fff")}">{tc.__name__}</text>')

    # Structural
    for i, tc in enumerate(groups["structural"]):
        x, y = 295, 108 + i * 47
        tc_positions[tc.__name__] = (360, y + 17)
        c = SPECIAL_COLORS.get(tc.__name__, COLORS["structural"])
        lines.append(f'  <rect x="{x}" y="{y}" width="130" height="34" rx="6" fill="{c.get("box", COLORS["structural"]["box"])}" stroke="{c.get("border", COLORS["structural"]["border"])}"/>')
        lines.append(f'  <text x="{x+65}" y="{y+22}" text-anchor="middle" font-weight="bold" fill="{c.get("text", "#fff")}">{tc.__name__}</text>')

    # Computational
    comp_layout = {
        "Functor": (625, 108),
        "Applicative": (625, 160),
        "Alternative": (520, 212),
        "Monad": (685, 212),
        "MonadError": (685, 264),
    }
    for tc in groups["computational"]:
        pos = comp_layout.get(tc.__name__, (625, 160))
        x, y = pos
        tc_positions[tc.__name__] = (x + 65, y + 17)
        c = SPECIAL_COLORS.get(tc.__name__, COLORS["computational"])
        lines.append(f'  <rect x="{x}" y="{y}" width="130" height="34" rx="6" fill="{c.get("box", COLORS["computational"]["box"])}" stroke="{c.get("border", COLORS["computational"]["border"])}"/>')
        lines.append(f'  <text x="{x+65}" y="{y+22}" text-anchor="middle" font-weight="bold" fill="{c.get("text", "#fff")}">{tc.__name__}</text>')

    # Group backgrounds
    lines.insert(10, f'  <rect x="30" y="75" width="200" height="{52*len(groups["algebraic"])+60}" rx="8" fill="{COLORS["algebraic"]["bg"]}" stroke="{COLORS["algebraic"]["border"]}" filter="url(#shadow)"/>')
    lines.insert(11, f'  <text x="130" y="95" text-anchor="middle" font-size="10" fill="{COLORS["algebraic"]["label"]}" font-weight="bold">ALGEBRAIC</text>')
    lines.insert(12, f'  <rect x="260" y="75" width="200" height="{47*len(groups["structural"])+60}" rx="8" fill="{COLORS["structural"]["bg"]}" stroke="{COLORS["structural"]["border"]}" filter="url(#shadow)"/>')
    lines.insert(13, f'  <text x="360" y="95" text-anchor="middle" font-size="10" fill="{COLORS["structural"]["label"]}" font-weight="bold">STRUCTURAL</text>')
    lines.insert(14, f'  <rect x="490" y="75" width="380" height="230" rx="8" fill="{COLORS["computational"]["bg"]}" stroke="{COLORS["computational"]["border"]}" filter="url(#shadow)"/>')
    lines.insert(15, f'  <text x="680" y="95" text-anchor="middle" font-size="10" fill="{COLORS["computational"]["label"]}" font-weight="bold">COMPUTATIONAL</text>')

    # Edges
    for parent_name, child_name in edges:
        if parent_name in tc_positions and child_name in tc_positions:
            px, py = tc_positions[parent_name]
            cx, cy = tc_positions[child_name]
            lines.append(f'  <line x1="{px}" y1="{py+17}" x2="{cx}" y2="{cy-17}" stroke="#666" stroke-width="1.5" marker-end="url(#arrow)"/>')

    # Data types section
    lines.append(f'  <rect x="30" y="330" width="840" height="130" rx="8" fill="#2a2520" stroke="#d0b090" filter="url(#shadow)"/>')
    lines.append(f'  <text x="450" y="350" text-anchor="middle" font-size="10" fill="#c0a070" font-weight="bold">DATA TYPES</text>')

    col_width = 110
    cols = 7
    for i, dt in enumerate(data_types):
        row = i // cols
        col = i % cols
        x = 50 + col * col_width + (10 if col > 0 else 0)
        y = 362 + row * 36
        name = dt.__name__
        w = max(90, len(name) * 8 + 20)
        lines.append(f'  <rect x="{x}" y="{y}" width="{w}" height="28" rx="5" fill="#3d3020" stroke="#d0a070"/>')
        lines.append(f'  <text x="{x + w//2}" y="{y+19}" text-anchor="middle" font-size="11" fill="#e0c8a0">{name}</text>')

    # Instances section
    lines.append(f'  <rect x="30" y="475" width="840" height="130" rx="8" fill="#202025" stroke="#b0b0b0" filter="url(#shadow)"/>')
    lines.append(f'  <text x="450" y="495" text-anchor="middle" font-size="10" fill="#9090a0" font-weight="bold">INSTANCES ({len(instances)} registered)</text>')

    y_off = 518
    per_line = 6
    for i in range(0, len(instances), per_line):
        chunk = instances[i:i+per_line]
        text = "  ".join(f"{tc}[{dt}]" for tc, dt in chunk)
        lines.append(f'  <text x="55" y="{y_off}" font-size="11" fill="#9090a0">{text}</text>')
        y_off += 20

    lines.append(f'  <text x="780" y="600" text-anchor="end" font-size="9" fill="#aaa">funstruct v2 • auto-generated</text>')
    lines.append('</svg>')
    return '\n'.join(lines)


if __name__ == "__main__":
    svg = generate_svg()
    out = "docs/typeclasses.svg"
    with open(out, "w") as f:
        f.write(svg)
    print(f"Generated {out}")
    print(f"Open with: open {out}")
