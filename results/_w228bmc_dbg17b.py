# -*- coding: utf-8 -*-
# Debug probe 2: resolve W217 SUB with empty vars, surface the exact failure.
import ast, sys
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"results\_w217bmc_prereg_derive.py", encoding="utf-8").read()

def resolve_node(node, vars, depth=0):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.List):
        return [resolve_node(x, vars) for x in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(resolve_node(x, vars) for x in node.elts)
    if isinstance(node, ast.Dict):
        return {resolve_node(k, vars): resolve_node(v, vars) for k, v in zip(node.keys(), node.values)}
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return resolve_node(node.left, vars) + resolve_node(node.right, vars)
    if isinstance(node, ast.Name) and node.id in vars:
        return vars[node.id]
    raise AssertionError(f"unresolvable node {type(node).__name__} @depth{depth}: {ast.dump(node)[:160]}")

for node in ast.walk(ast.parse(src)):
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "SUB":
        try:
            v = resolve_node(node.value, {})
            print("resolved OK, len =", len(v))
        except Exception as e:
            print("RESOLVE FAIL:", e)
