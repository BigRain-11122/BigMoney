# -*- coding: utf-8 -*-
# W232 prereg derive SUB-block generator (scratch, r967 freeze-prep).
# Emits the full literal SUB dict for _w232bmc_prereg_derive.py:
#   find  = m29(SUB31[i][k][1])  -- materialized W231-face, extracted from the
#                                   committed _w231bmc_prereg_derive.py lineage
#                                   (zero transcription; r787/r587 laws)
#   repl  = R32[i][k]            -- authored W232 faces (_w232bmc_r32_data.py)
# Two live-value pairs keep the BinOp source form so the W233-level
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

t230 = blob("91de0ae83", "research/PERPETUAL_N1_W230_PREREG.md")
t231 = blob("aebe0a5ac", "research/PERPETUAL_N1_W231_PREREG.md")
assert "## §7" in t231 and "占位" in t231, "not the freeze-time (pre-backfill) W231 face"
WIN_LABEL_230, WIN_LABEL_231 = win_label(t230), win_label(t231)
RAM_FACE_230, RAM_FACE_231 = ram_face(t230), ram_face(t231)
print("faces:", repr(WIN_LABEL_230), repr(WIN_LABEL_231), repr(RAM_FACE_230), repr(RAM_FACE_231))

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

SUB31 = extract_lit(r"results\_w231bmc_prereg_derive.py", "SUB", 46,
                    vars={"WIN_LABEL_230": WIN_LABEL_230, "WIN_LABEL": WIN_LABEL_231,
                          "RAM_FACE_230": RAM_FACE_230, "RAM_GB": RAM_FACE_231})
from _w232bmc_r32_data import R32

def m29(s):
    return s.replace("@L29@", "229").replace("@T29@", "30")

# structural sanity for the two BinOp specials
assert SUB31[0][3][0] == "【bm-c 循环班 r963 freeze 窗·" + WIN_LABEL_230, "special (0,3) find shape drifted"
assert SUB31[0][3][1] == "【bm-c 循环班 r964 freeze 窗·" + WIN_LABEL_231, "special (0,3) repl shape drifted"
assert SUB31[20][0][0] == "本窗 free RAM " + RAM_FACE_230 + "GB", "special (20,0) find shape drifted"
assert SUB31[20][0][1] == "本窗 free RAM " + RAM_FACE_231 + "GB", "special (20,0) repl shape drifted"

lines = ["SUB = {"]
for i in range(46):
    assert len(SUB31[i]) == len(R32[i]), f"R32[{i}] len {len(R32[i])} != SUB31 {len(SUB31[i])}"
    entries = []
    for k, (find, repl) in enumerate(SUB31[i]):
        r = R32[i][k]
        if i == 0 and k == 3:
            assert r.startswith("@@BINOP_WINLABEL@@"), "R32[0][3] marker missing"
            pre = r[len("@@BINOP_WINLABEL@@"):]
            assert pre == "【bm-c 循环班 r967 freeze 窗·"
            entries.append('("【bm-c 循环班 r964 freeze 窗·" + WIN_LABEL_231,"' + pre + '" + WIN_LABEL)')
            continue
        if i == 20 and k == 0:
            assert r == "@@BINOP_RAM@@", "R32[20][0] marker missing"
            entries.append('("本窗 free RAM " + RAM_FACE_231 + "GB","本窗 free RAM " + RAM_GB + "GB")')
            continue
        f = m29(repl)  # the W231-script SUB pair's NEW side = our find
        assert f and "@L29@" not in f and "@T29@" not in f, f"unmaterialized token in find[{i}][{k}]"
        entries.append("(" + repr(f) + "," + repr(r) + ")")
    lines.append(" " + str(i) + ": [" + ",\n      ".join(entries) + "],")
lines.append("}")
block = "\n".join(lines) + "\n"
open(r"results\_w232bmc_sub_block.py", "w", encoding="utf-8", newline="").write(block)
import py_compile
py_compile.compile(r"results\_w232bmc_sub_block.py", doraise=True)
print("SUB block emitted OK: results/_w232bmc_sub_block.py bytes=", len(block.encode("utf-8")))
