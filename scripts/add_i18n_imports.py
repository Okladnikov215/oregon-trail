"""Add 'from i18n import _' to modules that actually call _()."""
import ast
import sys
from pathlib import Path

SKIP = {".venv", "__pycache__", ".git", "scripts", "i18n", "node_modules"}


def calls_underscore(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "_":
                return True
    return False


def already_imported(tree):
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "i18n":
            if any(alias.name == "_" for alias in node.names):
                return True
    return False


def insertion_line(tree, lines):
    # __future__ обязан оставаться самым первым импортом
    futures = [n for n in tree.body
               if isinstance(n, ast.ImportFrom) and n.module == "__future__"]
    if futures:
        return max(n.end_lineno for n in futures)

    # После последнего顶层-импорта
    imports = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
    if imports:
        return max(n.end_lineno for n in imports)

    # После module docstring
    if tree.body:
        first = tree.body[0]
        if (isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)):
            return first.end_lineno

    # После shebang / coding / начальных комментариев
    idx = 0
    for line in lines:
        s = line.strip()
        if not s or s.startswith("#"):
            idx += 1
        else:
            break
    return idx


def process(path):
    raw = path.read_bytes().decode("utf-8-sig")

    try:
        tree = ast.parse(raw)
    except SyntaxError as exc:
        return "SKIP-SYNTAX", str(exc)

    if not calls_underscore(tree):
        return "SKIP-NO-CALLS", ""

    if already_imported(tree):
        return "SKIP-ALREADY", ""

    newline = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.splitlines(keepends=True)
    pos = insertion_line(tree, lines)

    updated = lines[:pos] + ["from i18n import _" + newline] + lines[pos:]
    source = "".join(updated)

    # Не записываем файл, если получился невалидный Python
    try:
        compile(source, str(path), "exec")
    except SyntaxError as exc:
        return "ERROR", str(exc)

    path.write_bytes(source.encode("utf-8"))
    return "OK", f"line {pos + 1}"


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    changed = []

    for path in sorted(root.rglob("*.py")):
        if set(path.parts) & SKIP:
            continue
        status, detail = process(path)
        print(f"{status:16} {path} {detail}")
        if status == "OK":
            changed.append(path)

    print(f"\nUpdated {len(changed)} files")


if __name__ == "__main__":
    main()