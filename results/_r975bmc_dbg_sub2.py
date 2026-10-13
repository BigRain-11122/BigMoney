# -*- coding: utf-8 -*-
# dbg2: precise resolution attempt on the on-disk W233 SUB dict
import ast, sys, traceback
sys.stdout.reconfigure(encoding="utf-8")
VARS = {"WIN_LABEL_232": "2026-10-13 13:5x·", "WIN_LABEL": "2026-10-13 18:4x·",
        "RAM_FACE_232": "~6.0", "RAM_GB": "~1.1"}

def resolve_node(node, vars):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.List):
        return [resolve_node(x, vars) for x in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(resolve_node(x, vars) for x in node.elts)
    if isinstance(node, ast.Dict):
        return {resolve_node(k, vars): resolve_node(v, vars) for k, v in zip(node.keys, node.values)}
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return resolve_node(node.left, vars) + resolve_node(node.right, vars)
    if isinstance(node, ast.Name) and node.id in vars:
        return vars[node.id]
    raise AssertionError(f"unresolvable AST node: {ast.dump(node)[:120]}")

src = open(r"results\_w233bmc_prereg_derive.py", encoding="utf-8").read()
for node in ast.walk(ast.parse(src)):
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "SUB":
        # collect distinct value-side node classes
        kinds = set()
        for sub in ast.walk(node.value):
            if not isinstance(sub, (ast.Constant,)):
                kinds.add(type(sub).__name__)
        print("value-side node kinds:", sorted(kinds))
        try:
            d = resolve_node(node.value, VARS)
            print("RESOLVED OK | entries:", len(d))
        except AssertionError as e:
            print("RESOLVE FAIL:", e)
            traceback.print_exc()
        # check dict value shapes entry by entry
        dd = node.value
        for ki, v in enumerate(dd.values):
            if not isinstance(v, ast.List):
                print(f"  entry[{ki}] value NOT List: {type(v).__name__}")
            else:
                for ei, elt in enumerate(v.elts):
                    if not (isinstance(elt, ast.Tuple) and len(elt.elts) == 2):
                        print(f"  entry[{ki}][{ei}] elt not pair-tuple: {ast.dump(elt)[:80]}")
        print("shape scan done")
        break
