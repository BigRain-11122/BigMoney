# -*- coding: utf-8 -*-
"""r926 bm-a: AST-extract r922 W201 buildgen BACK dict (40 tokens) to a
JSON sidecar for the W202 one-generation roll (zero transcription r587)."""
import ast, io, json

SRC = "results/_r922bma_w201_prereg_build.py"
tree = ast.parse(io.open(SRC, encoding="utf-8").read())
BACK = None
for node in ast.walk(tree):
    if (isinstance(node, ast.Assign) and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "BACK"
            and isinstance(node.value, ast.Dict)):
        BACK = {}
        for k, v in zip(node.value.keys, node.value.values):
            key = ast.literal_eval(k)
            if isinstance(v, ast.Constant):
                BACK[key] = ast.literal_eval(v)
            else:
                BACK[key] = None  # '@CHAIN@': CHAIN_NEW Name
        break
assert BACK and len(BACK) == 40, len(BACK) if BACK else 0
# resolve CHAIN_NEW the way the r922 tool does (r914 literal + appends)
_r921 = io.open("results/_r921bma_w200_prereg_build.py", encoding="utf-8").read()
_r919 = io.open("results/_r919bma_w199_prereg_build.py", encoding="utf-8").read()
_r916 = io.open("results/_r916bma_w198_prereg_build.py", encoding="utf-8").read()
_r914 = io.open("results/_r914bma_w197_prereg_build.py", encoding="utf-8").read()

def _chain_right(src, target):
    t = ast.parse(src)
    for n in ast.walk(t):
        if (isinstance(n, ast.Assign) and len(n.targets) == 1
                and isinstance(n.targets[0], ast.Name)
                and n.targets[0].id == target
                and isinstance(n.value, ast.BinOp)
                and isinstance(n.value.op, ast.Add)):
            return ast.literal_eval(n.value.right)
    return None

def _chain_literal(src):
    t = ast.parse(src)
    for n in ast.walk(t):
        if (isinstance(n, ast.Assign) and len(n.targets) == 1
                and isinstance(n.targets[0], ast.Name)
                and n.targets[0].id == "BACK"
                and isinstance(n.value, ast.Dict)):
            for k, v in zip(n.value.keys, n.value.values):
                if ast.literal_eval(k) == "@CHAIN@":
                    assert isinstance(v, ast.Constant)
                    return ast.literal_eval(v)
    return None

append_916 = _chain_right(_r916, "CHAIN_NEW")
append_919 = _chain_right(_r919, "CHAIN_NEW")
append_921 = _chain_right(_r921, "CHAIN_NEW")
append_922 = _chain_right(io.open(SRC, encoding="utf-8").read(), "CHAIN_NEW")
chain_914 = _chain_literal(_r914)
assert append_916 == "；W197=bm-a r915 freeze（522a0aef5）", append_916
assert append_919 == "；W198=bm-a r916 freeze（82b881a4f）", append_919
assert append_921 == "；W199=bm-a r919 freeze（f312ec9d4）", append_921
assert append_922 == "；W200=bm-a r921 freeze（cd92a8d9c）", append_922
assert chain_914.endswith("；W196=bm-a r912 freeze（02cf6b44d）"), chain_914[-60:]
chain_919 = chain_914 + append_916 + append_919
chain_921 = chain_919 + append_921
chain_922 = chain_921 + append_922
assert chain_922.endswith("；W200=bm-a r921 freeze（cd92a8d9c）"), chain_922[-60:]
BACK["@CHAIN@"] = chain_922
out = {"chain_resolved": chain_922, "back": BACK}
io.open("results/_r926bma_w202_back_sidecar.json", "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))
print("BACK tokens:", len(BACK), "chain tail:", chain_922[-70:])
print("sidecar: results/_r926bma_w202_back_sidecar.json")
for k in sorted(BACK):
    v = BACK[k]
    print("==", k, "==")
    print((v if isinstance(v, str) else repr(v))[:400])
