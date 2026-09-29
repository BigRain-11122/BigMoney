# -*- coding: utf-8 -*-
"""_r445bmb_axislen_probe.py -- AST-scan the W12 draft for every dict
literal with an "axis" key; report list length + line number. Catches
all fourteen-tuple leftovers the surgery may have missed."""
import ast
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
src = open("results/_r445bmb_w12_runner_draft.py", encoding="utf-8").read()
tree = ast.parse(src)
bad = 0
for node in ast.walk(tree):
    if isinstance(node, ast.Dict):
        for k, v in zip(node.keys, node.values):
            if isinstance(k, ast.Constant) and k.value == "axis":
                if isinstance(v, ast.List):
                    n = len(v.elts)
                    tag = "OK " if n == 15 else "BAD"
                    if n != 15:
                        bad += 1
                    print(tag, "axis len", n, "line", v.lineno)
print("=== BAD count =", bad, "===")
