"""Generate demoplayground/index.html from demos/*.py files.

Reads each demo script, extracts its docstring and code,
and produces an HTML page with PyScript editor blocks.

Usage:
    uv run python scripts/generate_playground.py
    # or: just playground-gen
"""

from __future__ import annotations

import ast
import os
from pathlib import Path

DEMOS_DIR = Path("demos")
TRANSFORMERS_DIR = DEMOS_DIR / "transformers"
OUTPUT = Path("demoplayground/index.html")


def extract_demo(path: Path) -> dict:
    """Extract docstring, title, and code from a demo .py file."""
    source = path.read_text()
    tree = ast.parse(source)

    docstring = ast.get_docstring(tree) or path.stem
    title = docstring.split("\n")[0].strip().rstrip(".")

    # Get the main() function body as the runnable code
    main_fn = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            main_fn = node
            break

    if main_fn:
        # Extract main() body source
        start = main_fn.body[0].lineno - 1
        end = main_fn.end_lineno
        lines = source.split("\n")
        code_lines = lines[start:end]
        # Dedent
        indent = len(code_lines[0]) - len(code_lines[0].lstrip())
        code = "\n".join(
            line[indent:] if len(line) > indent else line for line in code_lines
        )
    else:
        # No main() — use everything after imports
        lines = source.split("\n")
        code_start = 0
        for i, line in enumerate(lines):
            if line.startswith('"""') and i > 0:
                # End of docstring
                code_start = i + 1
                break
            if line.startswith("from ") or line.startswith("import "):
                code_start = i
        code = "\n".join(lines[code_start:]).strip()

    # Get imports from the top of the file
    imports = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(ast.get_source_segment(source, node))

    # Build the runnable block: imports + main() body
    import_block = "\n".join(
        i
        for i in imports
        if i and "typer" not in i and "asyncio" not in i and "sys" not in i
    )
    runnable = f"{import_block}\n\n{code}" if import_block else code

    # Flag if this demo has async code (can't run directly in Pyodide py-editor)
    has_async = "async " in runnable or "await " in runnable or "asyncio" in runnable

    return {
        "path": str(path),
        "title": title,
        "description": "\n".join(docstring.split("\n")[1:]).strip(),
        "code": runnable.strip(),
        "async": has_async,
    }


def generate_html(demos: list[dict]) -> str:
    lines = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        "    <title>funstruct playground</title>",
        '    <link rel="stylesheet" href="https://pyscript.net/releases/2024.11.1/core.css">',
        '    <script type="module" src="https://pyscript.net/releases/2024.11.1/core.js"></script>',
        "    <style>",
        "        body { font-family: -apple-system, sans-serif; max-width: 960px; margin: 0 auto; padding: 2rem; background: #000; color: #e0e2e4; }",
        "        h1 { color: #de1fcf; }",
        "        h2 { color: #93c763; margin-top: 2.5rem; border-bottom: 1px solid #222; padding-bottom: 0.5rem; }",
        "        h3 { color: #678cb1; margin-top: 1.5rem; }",
        "        p { color: #b0b2b4; line-height: 1.6; font-size: 0.95rem; }",
        "        a { color: #89ddff; }",
        "        code { background: #1a1a1a; padding: 2px 6px; border-radius: 3px; color: #e97600; }",
        "        #status { background: #111; padding: 0.75rem 1rem; border-radius: 6px; margin-bottom: 2rem; border: 1px solid #333; }",
        "        .todo { background: #1a1500; border-left: 3px solid #ffcd22; padding: 0.5rem 1rem; margin: 1rem 0; font-size: 0.85rem; color: #ffcd22; }",
        "        .demo-source { color: #606060; font-size: 0.8rem; margin-bottom: 0.25rem; }",
        "        py-editor { filter: invert(0.88) hue-rotate(180deg); border-radius: 6px; overflow: hidden; }",
        "    </style>",
        "</head>",
        "<body>",
        "",
        "<h1>funstruct playground</h1>",
        "<p>All demo scripts from the funstruct repo, runnable in the browser via Pyodide.</p>",
        '<div class="todo">Requires <code>funstruct >= 2.0.0</code> on PyPI.</div>',
        '<div id="status">⏳ Loading Python + funstruct...</div>',
    ]

    for demo in demos:
        lines.append(f"\n<h2>{demo['title']}</h2>")
        if demo["description"]:
            desc = demo["description"][:200].replace("\n", " ")
            lines.append(f"<p>{desc}</p>")
        lines.append(
            f'<div class="demo-source">source: <code>{demo["path"]}</code></div>'
        )
        if demo["async"]:
            lines.append(
                '<p style="color:#ffcd22;font-size:0.85rem;">⚠ This demo uses async — view-only in browser. Run locally: <code>uv run python '
                + demo["path"]
                + "</code></p>"
            )
        lines.append(
            f'<script type="py-editor" config=\'{{"packages":["funstruct"]}}\'>'
        )
        lines.append(demo["code"])
        lines.append("</script>")

    lines.extend(
        [
            "",
            '<script type="py" config=\'{"packages":["funstruct"]}\'>',
            "from pyscript import document",
            'el = document.getElementById("status")',
            'el.innerHTML = "✅ Ready! Click ▶ on any block to run."',
            'el.style.color = "#93c763"',
            "</script>",
            "",
            '<p style="margin-top:3rem; text-align:center; color:#404040; font-size:0.85rem;">',
            '    <a href="https://github.com/veyga/funstruct" style="color:#404040">github</a> ·',
            '    <a href="https://pypi.org/project/funstruct/" style="color:#404040">pypi</a>',
            "</p>",
            "",
            "<!-- Auto-generated by scripts/generate_playground.py -->",
            "</body>",
            "</html>",
        ]
    )

    return "\n".join(lines)


def main():
    demos = []

    # Main demos (numbered)
    for path in sorted(DEMOS_DIR.glob("*.py")):
        if path.name == "__init__.py":
            continue
        try:
            demos.append(extract_demo(path))
        except Exception as e:
            print(f"  Skipping {path}: {e}")

    # Transformer demos
    if TRANSFORMERS_DIR.exists():
        for path in sorted(TRANSFORMERS_DIR.glob("*.py")):
            try:
                demos.append(extract_demo(path))
            except Exception as e:
                print(f"  Skipping {path}: {e}")

    html = generate_html(demos)
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(html)
    print(f"Generated {OUTPUT} with {len(demos)} demos")
    print(f"Open with: open {OUTPUT}")


if __name__ == "__main__":
    main()
