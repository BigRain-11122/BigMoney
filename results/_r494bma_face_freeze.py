# -*- coding: utf-8 -*-
# r494bma: freeze-face count for P2 prereg -- registered factor defs in M4, M5 demo set.
import os, re, sys

REPOS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "toolstack", "repos"))
M4_FEATURES = os.path.join(REPOS, "ml-quant-trading", "src", "mlquant", "features")
M5_FACTORS = os.path.join(REPOS, "Machine_Learning-Quant-Stock-Selection", "multifactor_demo", "factors.py")

out = []
total = 0
reg_pat = re.compile(r"@register_[a-z_]+\(\s*['\"]([a-zA-Z0-9_]+)['\"]")
for fn in sorted(os.listdir(M4_FEATURES)):
    if not fn.endswith(".py") or fn in ("__init__.py",):
        continue
    src = open(os.path.join(M4_FEATURES, fn), encoding="utf-8", errors="replace").read()
    names = reg_pat.findall(src)
    if names:
        total += len(names)
        out.append(f"{fn}: {len(names)} registered [{names[0]}..{names[-1]}]")
out.append(f"M4 registered total: {total}")

m5 = open(M5_FACTORS, encoding="utf-8", errors="replace").read()
demo = re.search(r"DEMO_FACTORS\s*=\s*\(([^)]*)\)", m5, re.S)
names5 = re.findall(r"['\"](alpha_\d+)['\"]", demo.group(1)) if demo else []
out.append(f"M5 DEMO_FACTORS: {len(names5)} -> {names5[:4]}..{names5[-2:]}")
alphas5 = re.findall(r"def (alpha_\d+)\(", m5)
out.append(f"M5 alpha methods: {len(alphas5)}")
out.append(f"M5 demo==methods set equal: {sorted(set(names5)) == sorted(set(alphas5))}")

sys.stdout.buffer.write("\n".join(out).encode("utf-8"))
