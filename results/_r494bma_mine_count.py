# -*- coding: utf-8 -*-
# r494bma: honest count of M4/M5 installed factor faces (by definition, not claim).
import ast, os, re, sys

REPOS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "toolstack", "repos"))
M4_FEATURES = os.path.join(REPOS, "ml-quant-trading", "src", "mlquant", "features")
M5_FACTORS = os.path.join(REPOS, "Machine_Learning-Quant-Stock-Selection", "multifactor_demo", "factors.py")

def count_defs(path, pat):
    """Count top-level or method defs matching regex; return (n, names sample)."""
    names = []
    src = open(path, encoding="utf-8", errors="replace").read()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        for m in re.finditer(pat, src):
            names.append(m.group(1))
        return len(names), names[:6]
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if re.fullmatch(pat, node.name):
                names.append(node.name)
    return len(names), sorted(names)[:6]

out = []
# M4: all feature files, alpha-ish / factor-ish defs
m4_total = 0
for fn in sorted(os.listdir(M4_FEATURES)):
    if not fn.endswith(".py") or fn == "__init__.py":
        continue
    p = os.path.join(M4_FEATURES, fn)
    n_alpha, s_alpha = count_defs(p, r"alpha_?\d+")
    n_other, _ = count_defs(p, r"[a-z][a-z0-9_]+")
    m4_total += n_alpha
    out.append(f"M4 {fn}: alpha-numbered={n_alpha} total-defs={n_other} {s_alpha}")
out.append(f"M4 alpha-numbered total: {m4_total}")

# M5: alpha_NNN methods in factors.py
n5, s5 = count_defs(M5_FACTORS, r"alpha_\d+")
out.append(f"M5 factors.py alpha_NNN: {n5} sample={s5}")
n5_all, _ = count_defs(M5_FACTORS, r"[a-z][a-z0-9_]+")
out.append(f"M5 factors.py total defs: {n5_all}")

sys.stdout.buffer.write("\n".join(out).encode("utf-8"))
