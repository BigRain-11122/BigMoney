# -*- coding: utf-8 -*-
# W235 prereg derive SUB-block generator (bm-a r967 takeover freeze-prep,
# bloodline clone of the committed _w234bmc_subgen.py per the same seat law).
# Emits the full literal SUB dict for _w235bma_prereg_derive.py:
#   find  = m32(SUB34[i][k][1])  -- materialized W234-face, extracted from the
#                                   committed _w234bmc_prereg_derive.py lineage
#                                   (zero transcription; r787/r587 laws)
#   repl  = R35[i][k]            -- authored W235 takeover faces
#                                   (results/_w235bma_r35_data.py -- authored
#                                   r967 from _w235bmc_facts.json + seat
#                                   ADMIT receipt + takeover evidence)
# Two live-value pairs keep the BinOp source form so the W236-level
# extract_lit replay resolves them with vars (lineage continuity):
#   (0,3) freeze-window label ; (20,0) live RAM.
# TAKEOVER NOTE: engine_owner flips bm-c->bm-a (r885/r898 precedent); bands
# unchanged (R250 no re-pick, seat receipt verbatim).
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
    m = re.search(r"freeze 窗·(2026-10-1[234] \d+:\d+)x·", txt)
    assert m, "freeze-window label face not found"
    return m.group(1) + "x·"

FACTS = json.load(open(REPO + r"\results\_w235bmc_facts.json", encoding="utf-8"))
t233 = blob("933e3ceea", "research/PERPETUAL_N1_W233_PREREG.md")
assert "## §7" in t233 and "占位" in t233, "not the freeze-time (pre-backfill) W233 face"
WIN_LABEL_233 = win_label(t233)                    # W233 derive-window label (r972 face)
RAM_FACE_233 = ram_face(t233)                      # W233 RAM face
WIN_234 = FACTS["w234_win_label"]                  # W234 derive-window label (r976 face, frozen)
RAM_234 = FACTS["w234_ram_face"]                   # W234 RAM face (frozen)
print("faces:", repr(WIN_LABEL_233), repr(WIN_234), repr(RAM_FACE_233), repr(RAM_234))

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

# SUB34 = the W234 script's own transform table (W233-face -> W234-face pairs);
# its NEW sides (index [1]) = the W234-face find sides for the W235 table.
SUB34 = extract_lit(r"results\_w234bmc_prereg_derive.py", "SUB", 46,
                    vars={"WIN_LABEL_233": WIN_LABEL_233, "WIN_LABEL": WIN_234,
                          "RAM_FACE_233": RAM_FACE_233, "RAM_GB": RAM_234})

from _w235bma_r35_data import R35   # <-- authored this window (bm-a takeover faces)

def m32(s):
    return s.replace("@L32@", "232").replace("@T32@", "33")

# structural sanity for the two BinOp specials (W234-face shapes)
assert SUB34[0][3][0] == "【bm-c 循环班 r972 freeze 窗·" + WIN_LABEL_233, "special (0,3) find shape drifted"
assert SUB34[0][3][1] == "【bm-c 循环班 r976 freeze 窗·" + WIN_234, "special (0,3) repl shape drifted"
assert SUB34[20][0][0] == "本窗 free RAM " + RAM_FACE_233 + "GB", "special (20,0) find shape drifted"
assert SUB34[20][0][1] == "本窗 free RAM " + RAM_234 + "GB", "special (20,0) repl shape drifted"

lines = ["SUB = {"]
for i in range(46):
    assert len(SUB34[i]) == len(R35[i]), f"R35[{i}] len {len(R35[i])} != SUB34 {len(SUB34[i])}"
    entries = []
    for k, (find, repl) in enumerate(SUB34[i]):
        r = R35[i][k]
        if i == 0 and k == 3:
            assert r.startswith("@@BINOP_WINLABEL@@"), "R35[0][3] marker missing"
            pre = r[len("@@BINOP_WINLABEL@@"):]
            assert pre == "【bm-a 循环班 r967 takeover freeze 窗·"
            entries.append('("【bm-c 循环班 r976 freeze 窗·" + WIN_LABEL_234,"' + pre + '" + WIN_LABEL)')
            continue
        if i == 20 and k == 0:
            assert r == "@@BINOP_RAM@@", "R35[20][0] marker missing"
            entries.append('("本窗 free RAM " + RAM_FACE_234 + "GB","本窗 free RAM " + RAM_GB + "GB")')
            continue
        f = m32(repl)  # the W234-script SUB pair's NEW side = our find
        assert f and "@L32@" not in f and "@T32@" not in f, f"unmaterialized token in find[{i}][{k}]"
        entries.append("(" + repr(f) + "," + repr(r) + ")")
    lines.append(" " + str(i) + ": [" + ",\n      ".join(entries) + "],")
lines.append("}")
block = "\n".join(lines) + "\n"
open(r"results\_w235bma_sub_block.py", "w", encoding="utf-8", newline="").write(block)
import py_compile
py_compile.compile(r"results\_w235bma_sub_block.py", doraise=True)
print("SUB block emitted OK: results/_w235bma_sub_block.py bytes=", len(block.encode("utf-8")))
