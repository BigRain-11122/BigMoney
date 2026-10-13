# -*- coding: utf-8 -*-
# W234 prereg derive SUB-block generator (r975 freeze-prep, bloodline clone of
# the committed _w233bmc_subgen.py per MSG-20261013-1955 seat law).
# Emits the full literal SUB dict for _w234bmc_prereg_derive.py:
#   find  = m31(SUB33[i][k][1])  -- materialized W233-face, extracted from the
#                                   committed _w233bmc_prereg_derive.py lineage
#                                   (zero transcription; r787/r587 laws)
#   repl  = R34[i][k]            -- authored W234 faces (results/_w234bmc_r34_data.py
#                                   -- authored r975 from _w234bmc_facts.json)
# Two live-value pairs keep the BinOp source form so the W235-level
# extract_lit replay resolves them with vars (lineage continuity):
#   (0,3) freeze-window label ; (20,0) live RAM.
# STATUS r976: R34 authored r975 window (results/_w234bmc_r34_data.py, all
# values live-verified against _w234bmc_facts.json + probe receipt +
# n1_w233_results.json); derive-round label face corrected r975->r976 at
# derive-window entry (the derive runs in the r976 window; r971->r972
# precedent per r975 next-window pointer note; hygiene re-scan green this
# window = the "r976 窗实跑" claim is live-true).
# All historical faces resolved from _w234bmc_facts.json (machine-frozen r975)
# + the W232 freeze-time blob (a3a7aa632) -- zero eyeball transcription.
import ast, json, re, subprocess, sys
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

FACTS = json.load(open(REPO + r"\results\_w234bmc_facts.json", encoding="utf-8"))
t232 = blob("a3a7aa632", "research/PERPETUAL_N1_W232_PREREG.md")
assert "## §7" in t232 and "占位" in t232, "not the freeze-time (pre-backfill) W232 face"
WIN_LABEL_232 = win_label(t232)                    # W232 derive-window label (r967 face)
RAM_FACE_232 = ram_face(t232)                      # W232 RAM face
WIN_LABEL_233 = FACTS["w233_win_label"]            # W233 derive-window label (r972 face, frozen)
RAM_FACE_233 = FACTS["w233_ram_face"]              # W233 RAM face (frozen)
print("faces:", repr(WIN_LABEL_232), repr(WIN_LABEL_233), repr(RAM_FACE_232), repr(RAM_FACE_233))

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
            except Exception as e:
                if "dbg" in sys.argv:
                    import traceback
                    traceback.print_exc()
                print("EXC:", repr(e)[:300])
                cand = None
            if cand:
                val = cand
                break
    assert val and len(val) == expect, f"{varname} extract failed: {len(val) if val else 0}"
    return val

# SUB33 = the W233 script's own transform table (W232-face -> W233-face pairs);
# its NEW sides (index [1]) = the W233-face find sides for the W234 table.
SUB33 = extract_lit(r"results\_w233bmc_prereg_derive.py", "SUB", 46,
                    vars={"WIN_LABEL_232": WIN_LABEL_232, "WIN_LABEL": WIN_LABEL_233,
                          "RAM_FACE_232": RAM_FACE_232, "RAM_GB": RAM_FACE_233})

from _w234bmc_r34_data import R34   # <-- authored this window from _w234bmc_facts.json

def m31(s):
    return s.replace("@L31@", "231").replace("@T31@", "32")

# structural sanity for the two BinOp specials (W233-face shapes)
assert SUB33[0][3][0] == "【bm-c 循环班 r967 freeze 窗·" + WIN_LABEL_232, "special (0,3) find shape drifted"
assert SUB33[0][3][1] == "【bm-c 循环班 r972 freeze 窗·" + WIN_LABEL_233, "special (0,3) repl shape drifted"
assert SUB33[20][0][0] == "本窗 free RAM " + RAM_FACE_232 + "GB", "special (20,0) find shape drifted"
assert SUB33[20][0][1] == "本窗 free RAM " + RAM_FACE_233 + "GB", "special (20,0) repl shape drifted"

lines = ["SUB = {"]
for i in range(46):
    assert len(SUB33[i]) == len(R34[i]), f"R34[{i}] len {len(R34[i])} != SUB33 {len(SUB33[i])}"
    entries = []
    for k, (find, repl) in enumerate(SUB33[i]):
        r = R34[i][k]
        if i == 0 and k == 3:
            assert r.startswith("@@BINOP_WINLABEL@@"), "R34[0][3] marker missing"
            pre = r[len("@@BINOP_WINLABEL@@"):]
            assert pre == "【bm-c 循环班 r976 freeze 窗·"
            entries.append('("【bm-c 循环班 r972 freeze 窗·" + WIN_LABEL_233,"' + pre + '" + WIN_LABEL)')
            continue
        if i == 20 and k == 0:
            assert r == "@@BINOP_RAM@@", "R34[20][0] marker missing"
            entries.append('("本窗 free RAM " + RAM_FACE_233 + "GB","本窗 free RAM " + RAM_GB + "GB")')
            continue
        f = m31(repl)  # the W233-script SUB pair's NEW side = our find
        assert f and "@L31@" not in f and "@T31@" not in f, f"unmaterialized token in find[{i}][{k}]"
        entries.append("(" + repr(f) + "," + repr(r) + ")")
    lines.append(" " + str(i) + ": [" + ",\n      ".join(entries) + "],")
lines.append("}")
block = "\n".join(lines) + "\n"
open(r"results\_w234bmc_sub_block.py", "w", encoding="utf-8", newline="").write(block)
import py_compile
py_compile.compile(r"results\_w234bmc_sub_block.py", doraise=True)
print("SUB block emitted OK: results/_w234bmc_sub_block.py bytes=", len(block.encode("utf-8")))
