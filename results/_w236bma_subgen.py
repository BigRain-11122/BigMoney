# -*- coding: utf-8 -*-
# W236 prereg derive SUB-block generator (bm-a r972 freeze-prep, own-seat
# chain, bloodline clone of the committed _w235bma_subgen.py per the same
# seat law). Emits the full literal SUB dict for _w236bma_prereg_derive.py:
#   find  = m33(SUB35[i][k][1])  -- materialized W235-face, extracted from the
#                                   committed _w235bma_sub_block.py lineage
#                                   (zero transcription; r787/r587 laws)
#   repl  = R36[i][k]            -- authored W236 own-seat faces
#                                   (results/_w236bma_r36_data.py -- authored
#                                   r972 from _w236bma_facts.json + seat ADMIT
#                                   receipt + live n1_w235_results.json)
# Two live-value pairs keep the BinOp source form so the W237-level
# extract_lit replay resolves them with vars (lineage continuity):
#   (0,3) freeze-window label ; (20,0) live RAM.
# OWN-SEAT NOTE: engine_owner stays bm-a (zero flip, zero takeover); bands
# unchanged from the seat ADMIT receipt (R250 no re-pick).
import ast, json, re, subprocess, sys
sys.path.insert(0, r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\results")
sys.stdout.reconfigure(encoding="utf-8")
REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

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
    m = re.search(r"freeze 窗·(2026-10-1[234] \d+:\d+)x·", txt)
    assert m, "freeze-window label face not found"
    return m.group(1) + "x·"

FACTS = json.load(open(REPO + r"\results\_w236bma_facts.json", encoding="utf-8"))
t234 = blob("252d5cc95", "research/PERPETUAL_N1_W234_PREREG.md")
assert "## §7" in t234 and "占位" in t234, "not the freeze-time (pre-backfill) W234 face"
WIN_LABEL_234 = win_label(t234)                    # W234 derive-window label (r976 face)
RAM_FACE_234 = ram_face(t234)                      # W234 RAM face
WIN_235 = FACTS["w235_win_label"]                   # W235 derive-window label (r968 face, frozen)
RAM_235 = FACTS["w235_ram_face"]                   # W235 RAM face (frozen)
print("faces:", repr(WIN_LABEL_234), repr(WIN_235), repr(RAM_FACE_234), repr(RAM_235))
# cross-assert the W234 window faces against the prior-wave facts mirror (lineage continuity)
_f235 = json.load(open(REPO + r"\results\_w235bmc_facts.json", encoding="utf-8"))
assert WIN_LABEL_234 == _f235["w234_win_label"], "W234 win label drift vs prior facts"
assert RAM_FACE_234 == _f235["w234_ram_face"], "W234 RAM face drift vs prior facts"

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

# SUB35 = the W235 script's own transform table (W234-face -> W235-face pairs);
# its NEW sides (index [1]) = the W235-face find sides for the W236 table.
SUB35 = extract_lit(r"results\_w235bma_sub_block.py", "SUB", 46,
                    vars={"WIN_LABEL_234": WIN_LABEL_234, "WIN_LABEL": WIN_235,
                          "RAM_FACE_234": RAM_FACE_234, "RAM_GB": RAM_235})

from _w236bma_r36_data import R36   # <-- authored this window (bm-a own-seat faces)

def m33(s):
    return s.replace("@L33@", "233").replace("@T33@", "34")

# structural sanity for the two BinOp specials (W235-face shapes)
assert SUB35[0][3][0] == "【bm-c 循环班 r976 freeze 窗·" + WIN_LABEL_234, "special (0,3) find shape drifted"
assert SUB35[0][3][1] == "【bm-a 循环班 r967 takeover freeze 窗·" + WIN_235, "special (0,3) repl shape drifted"
assert SUB35[20][0][0] == "本窗 free RAM " + RAM_FACE_234 + "GB", "special (20,0) find shape drifted"
assert SUB35[20][0][1] == "本窗 free RAM " + RAM_235 + "GB", "special (20,0) repl shape drifted"

lines = ["SUB = {"]
for i in range(46):
    assert len(R36[i]) == len(SUB35[i]), f"R36[{i}] len {len(R36[i])} != SUB35 {len(SUB35[i])}"
    entries = []
    for k, (find, repl) in enumerate(SUB35[i]):
        r = R36[i][k]
        if i == 0 and k == 3:
            assert r.startswith("@@BINOP_WINLABEL@@"), "R36[0][3] marker missing"
            pre = r[len("@@BINOP_WINLABEL@@"):]
            assert pre == "【bm-a 循环班 r972 freeze 窗·"
            entries.append('("【bm-a 循环班 r967 takeover freeze 窗·" + WIN_LABEL_235,"' + pre + '" + WIN_LABEL)')
            continue
        if i == 20 and k == 0:
            assert r == "@@BINOP_RAM@@", "R36[20][0] marker missing"
            entries.append('("本窗 free RAM " + RAM_FACE_235 + "GB","本窗 free RAM " + RAM_GB + "GB")')
            continue
        f = m33(repl)  # the W235-script SUB pair's NEW side = our find
        assert f and "@L33@" not in f and "@T33@" not in f, f"unmaterialized token in find[{i}][{k}]"
        entries.append("(" + repr(f) + "," + repr(r) + ")")
    lines.append(" " + str(i) + ": [" + ",\n      ".join(entries) + "],")
lines.append("}")
block = "\n".join(lines) + "\n"
open(r"results\_w236bma_sub_block.py", "w", encoding="utf-8", newline="").write(block)
import py_compile
py_compile.compile(r"results\_w236bma_sub_block.py", doraise=True)
print("SUB block emitted OK: results/_w236bma_sub_block.py bytes=", len(block.encode("utf-8")))
