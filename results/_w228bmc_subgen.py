# -*- coding: utf-8 -*-
# W228 prereg derive SUB-block generator (scratch, r958 freeze-prep).
# Emits the full literal SUB dict for _w228bmc_prereg_derive.py:
#   find  = m25(SUB27[i][k][1])  -- materialized W227-face, extracted from the
#                                   committed _w227bmc_prereg_derive.py lineage
#                                   (zero transcription; r787/r587 laws)
#   repl  = R28[i][k]            -- authored W228 faces (_w228bmc_r28_data.py)
# Two live-value pairs keep the BinOp source form so the W229-level
# extract_lit replay resolves them with vars (lineage continuity):
#   (0,3) freeze-window label ; (20,0) live RAM.
import ast, re, subprocess, sys
sys.path.insert(0, r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results")
sys.stdout.reconfigure(encoding="utf-8")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

def blob(rev, path):
    b = subprocess.run([r"C:\Program Files\Git\cmd\git.exe", "-C", REPO, "show", f"{rev}:{path}"],
                       capture_output=True).stdout
    assert b, f"blob fetch failed {rev}:{path}"
    return b.decode("utf-8")

def ram_face(txt):
    m = re.search(r"本窗 free RAM ~(\d+\.\d)GB", txt)
    assert m, "RAM note face not found"
    return "~" + m.group(1)

def win_label(txt):
    m = re.search(r"freeze 窗·(2026-10-1[23] \d+:\d+)x·", txt)
    assert m, "freeze-window label face not found"
    return m.group(1) + "x·"

t226 = blob("f65d886cb", "research/PERPETUAL_N1_W226_PREREG.md")
t227 = blob("0d0c63c6e", "research/PERPETUAL_N1_W227_PREREG.md")
assert "## §7" in t227 and "占位" in t227, "not the freeze-time (pre-backfill) W227 face"
WIN_LABEL_226, WIN_LABEL_227 = win_label(t226), win_label(t227)
RAM_FACE_226, RAM_FACE_227 = ram_face(t226), ram_face(t227)
print("faces:", repr(WIN_LABEL_226), repr(WIN_LABEL_227), repr(RAM_FACE_226), repr(RAM_FACE_227))

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
    raise AssertionError(f"unresolvable AST node: {ast.dump(node)[:100]}")

def extract_lit(path, varname, expect, vars=None):
    vars = vars or {}
    src = open(path, encoding="utf-8").read()
    val = None
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == varname:
            try:
                cand = resolve_node(node.value, vars)
            except Exception:
                cand = None
            if cand:
                val = cand
                break
    assert val and len(val) == expect, f"{varname} extract failed: {len(val) if val else 0}"
    return val

SUB27 = extract_lit(r"results\_w227bmc_prereg_derive.py", "SUB", 46,
                    vars={"WIN_LABEL_226": WIN_LABEL_226, "WIN_LABEL": WIN_LABEL_227,
                          "RAM_FACE_226": RAM_FACE_226, "RAM_GB": RAM_FACE_227})
from _w228bmc_r28_data import R28

def m25(s):
    return s.replace("@L25@", "225").replace("@T25@", "26")

# structural sanity for the two BinOp specials
assert SUB27[0][3][0] == "【bm-c 循环班 r941 freeze 窗·" + WIN_LABEL_226, "special (0,3) find shape drifted"
assert SUB27[0][3][1] == "【bm-c 循环班 r956 freeze 窗·" + WIN_LABEL_227, "special (0,3) repl shape drifted"
assert SUB27[20][0][0] == "本窗 free RAM " + RAM_FACE_226 + "GB", "special (20,0) find shape drifted"
assert SUB27[20][0][1] == "本窗 free RAM " + RAM_FACE_227 + "GB", "special (20,0) repl shape drifted"

lines = ["SUB = {"]
for i in range(46):
    assert len(SUB27[i]) == len(R28[i]), f"R28[{i}] len {len(R28[i])} != SUB27 {len(SUB27[i])}"
    entries = []
    for k, (find, repl) in enumerate(SUB27[i]):
        r = R28[i][k]
        if i == 0 and k == 3:
            assert r.startswith("@@BINOP_WINLABEL@@"), "R28[0][3] marker missing"
            pre = r[len("@@BINOP_WINLABEL@@"):]
            assert pre == "【bm-c 循环班 r958 freeze 窗·"
            entries.append('("【bm-c 循环班 r956 freeze 窗·" + WIN_LABEL_227,"' + pre + '" + WIN_LABEL)')
            continue
        if i == 20 and k == 0:
            assert r == "@@BINOP_RAM@@", "R28[20][0] marker missing"
            entries.append('("本窗 free RAM " + RAM_FACE_227 + "GB","本窗 free RAM " + RAM_GB + "GB")')
            continue
        f = m25(repl)  # the W227-script SUB pair's NEW side = our find
        assert f and "@L25@" not in f and "@T25@" not in f, f"unmaterialized token in find[{i}][{k}]"
        entries.append("(" + repr(f) + "," + repr(r) + ")")
    lines.append(" " + str(i) + ": [" + ",\n      ".join(entries) + "],")
lines.append("}")
block = "\n".join(lines) + "\n"
open(r"results\_w228bmc_sub_block.py", "w", encoding="utf-8", newline="").write(block)
import py_compile
py_compile.compile(r"results\_w228bmc_sub_block.py", doraise=True)
print("SUB block emitted OK: results/_w228bmc_sub_block.py bytes=", len(block.encode("utf-8")))
