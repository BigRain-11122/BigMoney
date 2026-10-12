# -*- coding: utf-8 -*-
# Debug probe: why does SUB extraction from _w217bmc_prereg_derive.py fail?
import ast, sys
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"results\_w217bmc_prereg_derive.py", encoding="utf-8").read()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "SUB":
        print("found SUB assign at line", node.lineno, "| value type:", type(node.value).__name__)
        # collect Name refs
        names = sorted({n.id for n in ast.walk(node.value) if isinstance(n, ast.Name)})
        print("  Name refs:", names)
        # count entries
        if isinstance(node.value, ast.Dict):
            print("  dict keys:", len(node.value.keys))
