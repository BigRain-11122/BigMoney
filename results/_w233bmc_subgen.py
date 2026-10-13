# -*- coding: utf-8 -*-
# W233 prereg derive SUB-block generator (scratch, r971 freeze-prep facts + skeleton).
# Emits the full literal SUB dict for _w233bmc_prereg_derive.py:
#   find  = m30(SUB32[i][k][1])  -- materialized W232-face, extracted from the
#                                   committed _w232bmc_prereg_derive.py lineage
#                                   (zero transcription; r787/r587 laws)
#   repl  = R33[i][k]            -- authored W233 faces (_w233bmc_r33_data.py --
#                                   TO BE AUTHORED NEXT WINDOW from _w233bmc_facts.json)
# Two live-value pairs keep the BinOp source form so the W234-level
# extract_lit replay resolves them with vars (lineage continuity):
#   (0,3) freeze-window label ; (20,0) live RAM.
# STATUS r971: skeleton complete; requires results/_w233bmc_r33_data.py to run.
# All historical faces resolved from _w233bmc_facts.json (machine-frozen r971)
# + the W231 freeze-time blob (aebe0a5ac) -- zero eyeball transcription.
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

FACTS = json.load(open(REPO + r"\results\_w233bmc_facts.json", encoding="utf-8"))
t231 = blob("aebe0a5ac", "research/PERPETUAL_N1_W231_PREREG.md")
assert "## §7" in t231 and "占位" in t231, "not the freeze-time (pre-backfill) W231 face"
WIN_LABEL_231 = win_label(t231)                    # W231 derive-window label (r964 face)
RAM_FACE_231 = ram_face(t231)                      # W231 RAM face
WIN_LABEL_232 = FACTS["w232_win_label"]            # W232 derive-window label (r967 face, frozen)
RAM_FACE_232 = FACTS["w232_ram_face"]              # W232 RAM face (frozen)
print("faces:", repr(WIN_LABEL_231), repr(WIN_LABEL_232), repr(RAM_FACE_231), repr(RAM_FACE_232))

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

# SUB32 = the W232 script's own transform table (W231-face -> W232-face pairs);
# its NEW sides (index [1]) = the W232-face find sides for the W233 table.
SUB32 = extract_lit(r"results\_w232bmc_prereg_derive.py", "SUB", 46,
                    vars={"WIN_LABEL_231": WIN_LABEL_231, "WIN_LABEL": WIN_LABEL_232,
                          "RAM_FACE_231": RAM_FACE_231, "RAM_GB": RAM_FACE_232})

from _w233bmc_r33_data import R33   # <-- authored next window from _w233bmc_facts.json

def m30(s):
    return s.replace("@L30@", "230").replace("@T30@", "31")

# structural sanity for the two BinOp specials (W232-face shapes)
assert SUB32[0][3][0] == "【bm-c 循环班 r964 freeze 窗·" + WIN_LABEL_231, "special (0,3) find shape drifted"
assert SUB32[0][3][1] == "【bm-c 循环班 r967 freeze 窗·" + WIN_LABEL_232, "special (0,3) repl shape drifted"
assert SUB32[20][0][0] == "本窗 free RAM " + RAM_FACE_231 + "GB", "special (20,0) find shape drifted"
assert SUB32[20][0][1] == "本窗 free RAM " + RAM_FACE_232 + "GB", "special (20,0) repl shape drifted"

lines = ["SUB = {"]
for i in range(46):
    assert len(SUB32[i]) == len(R33[i]), f"R33[{i}] len {len(R33[i])} != SUB32 {len(SUB32[i])}"
    entries = []
    for k, (find, repl) in enumerate(SUB32[i]):
        r = R33[i][k]
        if i == 0 and k == 3:
            assert r.startswith("@@BINOP_WINLABEL@@"), "R33[0][3] marker missing"
            pre = r[len("@@BINOP_WINLABEL@@"):]
            assert pre == "【bm-c 循环班 r971 freeze 窗·"
            entries.append('("【bm-c 循环班 r967 freeze 窗·" + WIN_LABEL_232,"' + pre + '" + WIN_LABEL)')
            continue
        if i == 20 and k == 0:
            assert r == "@@BINOP_RAM@@", "R33[20][0] marker missing"
            entries.append('("本窗 free RAM " + RAM_FACE_232 + "GB","本窗 free RAM " + RAM_GB + "GB")')
            continue
        f = m30(repl)  # the W232-script SUB pair's NEW side = our find
        assert f and "@L30@" not in f and "@T30@" not in f, f"unmaterialized token in find[{i}][{k}]"
        entries.append("(" + repr(f) + "," + repr(r) + ")")
    lines.append(" " + str(i) + ": [" + ",\n      ".join(entries) + "],")
lines.append("}")
block = "\n".join(lines) + "\n"
open(r"results\_w233bmc_sub_block.py", "w", encoding="utf-8", newline="").write(block)
import py_compile
py_compile.compile(r"results\_w233bmc_sub_block.py", doraise=True)
print("SUB block emitted OK: results/_w233bmc_sub_block.py bytes=", len(block.encode("utf-8")))
