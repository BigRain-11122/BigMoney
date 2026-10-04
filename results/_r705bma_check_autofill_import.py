"""r705 bm-a: inspect autofill.py module-level executable statements
(import-safety check before reusing _claim_shard for the N2-W15 judge-prep
session claim; anti-rebuild law = reuse the canonically-tested claim path)."""
import ast

src = open("Tools/autofill.py", encoding="utf-8", errors="replace").read()
tree = ast.parse(src)
exe = []
for node in tree.body:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
                          ast.Import, ast.ImportFrom)):
        continue
    if isinstance(node, ast.Assign):
        has_call = any(isinstance(n, ast.Call) for n in ast.walk(node))
        if not has_call:
            continue
    exe.append((node.lineno, type(node).__name__))
print("module-level executable-with-call statements:")
for ln, t in exe:
    print(" ", ln, t)
print("has __main__ guard:", src.find('__name__ == "__main__"') >= 0)
