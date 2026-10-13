# -*- coding: utf-8 -*-
# dbg: probe why SUB extract fails on the on-disk W233 derive script
import ast, sys
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"results\_w233bmc_prereg_derive.py", encoding="utf-8-sig").read()
print("src bytes:", len(src.encode("utf-8")), "| BOM:", src.startswith("\ufeff"))
tree = ast.parse(src)
n = 0
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "SUB":
        n += 1
        print(f"SUB assign #{n}: value type = {type(node.value).__name__}")
        if isinstance(node.value, ast.Dict):
            d = node.value
            print("  dict entries:", len(d.keys))
            # try resolving each value element, report first failure
            for ki, (k, v) in enumerate(zip(d.keys, d.values)):
                if isinstance(v, ast.List):
                    for ei, elt in enumerate(v.elts):
                        if isinstance(elt, ast.Tuple) and len(elt.elts) == 2:
                            for side_i, side in enumerate(elt.elts):
                                stack = [side]
                                while stack:
                                    x = stack.pop()
                                    if isinstance(x, ast.BinOp):
                                        stack.extend([x.left, x.right])
                                    elif isinstance(x, ast.Name):
                                        print(f"  NAME in entry[{ki}][{ei}][{side_i}]: {x.id}")
print("total SUB assigns:", n)
