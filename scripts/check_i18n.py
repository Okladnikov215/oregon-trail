"""Audit the i18n refactor: find broken and missed translations."""
import ast
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
SKIP = {".venv", "__pycache__", ".git", "scripts", "i18n", "node_modules"}

en_file = ROOT / "i18n" / "en.json"
en = json.loads(en_file.read_text(encoding="utf-8-sig")) if en_file.exists() else {}

problems = []
remaining = []
wrapped = 0


def is_text_arg(node):
    return (isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and len(node.value) > 2
            and not node.value.isspace())


for path in sorted(ROOT.rglob("*.py")):
    if set(path.parts) & SKIP:
        continue

    try:
        tree = ast.parse(path.read_bytes().decode("utf-8-sig"))
    except SyntaxError as exc:
        problems.append(f"SYNTAX  {path}:{exc.lineno}: {exc.msg}")
        continue

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        # Что находится внутри _()
        if isinstance(node.func, ast.Name) and node.func.id == "_":
            if len(node.args) == 1 and is_text_arg(node.args[0]):
                wrapped += 1
                text = node.args[0].value
                if text not in en:
                    problems.append(f"NO KEY  {path}:{node.lineno}: {text!r}")
            else:
                problems.append(
                    f"BAD _() {path}:{node.lineno}: {ast.unparse(node)}"
                )

        # Что осталось захардкоженным в print/input
        if isinstance(node.func, ast.Name) and node.func.id in ("print", "input"):
            if not node.args:
                continue
            arg = node.args[0]
            if is_text_arg(arg):
                remaining.append(f"{path}:{node.lineno}: {arg.value!r}")
            elif isinstance(arg, ast.JoinedStr):
                remaining.append(f"{path}:{node.lineno}: F-STRING {ast.unparse(arg)}")

print(f"Wrapped literal strings : {wrapped}")
print(f"Keys in en.json         : {len(en)}")

print(f"\nPROBLEMS ({len(problems)}) - must be fixed:")
for item in problems:
    print("  " + item)

print(f"\nSTILL HARDCODED ({len(remaining)}) - not translated yet:")
for item in remaining:
    print("  " + item)

backups = list(ROOT.rglob("*.py.backup"))
print(f"\nBackup files: {len(backups)}")