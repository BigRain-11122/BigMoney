# -*- coding: utf-8 -*-
# W234 per-wave prereg derivation (bm-c r976 freeze-prep, 2026-10-13 20:5x).
# Method: machine transform of the freeze-time W233 prereg blob
# (git show 933e3ceea:research/PERPETUAL_N1_W233_PREREG.md -- the exact
# pre-backfill commit face; the sec.7/8 machine-read backfill landed later in
# 260217d39) with an explicit ordered replacement table.
# Pair old-sides are REPLAYED AT RUNTIME from the committed lineage chain
# (results/_w216bmc_prereg_derive.py PAIRS literal + _w217 SUB + _w218 SUB +
# _w219 SUB + _w220 SUB + _w221 SUB + _w222 SUB + _w223 SUB + _w224 SUB +
# _w225 SUB + _w226 SUB + _w227 SUB + _w228 SUB + _w229 SUB + _w230 SUB + _w231 SUB + _w232 SUB + _w233 SUB literals --
# EIGHTEEN-LEVEL replay chain, one deeper than the W233 seventeen-level chain;
# the W220 editor_gen same-window fix (r923 absorb freeze-window label) and
# the r927 pre-burn prose fixes (ledger 907,589->907,789 + own-block estate
# legs W220/W219+220) are replayed as corrective steps anchored to the
# committed blobs; placeholders materialized per level) -- zero transcription;
# every replayed block is assert-verified count==1 in the freeze-time blob
# BEFORE any pair application (r787 preflight law). Find sides of the own SUB
# table are machine-generated from the committed _w233 SUB new-sides by
# results/_w234bmc_subgen.py (m31 materialization; zero transcription).
# Bands/facts machine-derived from the committed ADMIT receipt
# results/_w234bmc_20261013_probe_receipt.json + n1_w233_results.json +
# _w233bmc_freeze_receipt.json -- never transcribed by eye (r587).
import ast, datetime, hashlib, json, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

def blob(rev, path):
    b = subprocess.run([r"C:\Program Files\Git\cmd\git.exe", "-C", REPO, "show", f"{rev}:{path}"],
                       capture_output=True).stdout
    assert b, f"blob fetch failed {rev}:{path}"
    return b.decode("utf-8")

# ---------- freeze-time blobs ----------
t219 = blob("0dae35332", "research/PERPETUAL_N1_W219_PREREG.md")  # RAM replay value (SUB19/20 BinOps)
t220 = blob("a9aee1d05", "research/PERPETUAL_N1_W220_PREREG.md")  # RAM face (SUB20/21 BinOps)
t221 = blob("98da27a40", "research/PERPETUAL_N1_W221_PREREG.md")  # RAM face (SUB21/22 BinOps)
t222 = blob("58f82fd63", "research/PERPETUAL_N1_W222_PREREG.md")  # RAM face (SUB22/23 BinOps)
t223 = blob("b7d46427d", "research/PERPETUAL_N1_W223_PREREG.md")  # RAM face (SUB23/24 BinOps)
t224 = blob("ac1b1de64", "research/PERPETUAL_N1_W224_PREREG.md")  # RAM face (SUB24/25 BinOps)
t225 = blob("4b22941a7", "research/PERPETUAL_N1_W225_PREREG.md")  # RAM face (SUB25/26 BinOps)
t226 = blob("f65d886cb", "research/PERPETUAL_N1_W226_PREREG.md")  # RAM/label face (SUB26/27 BinOps)
t227 = blob("0d0c63c6e", "research/PERPETUAL_N1_W227_PREREG.md")  # RAM/label face (SUB27/28 BinOps)
t228 = blob("e6c8441aa", "research/PERPETUAL_N1_W228_PREREG.md")  # RAM/label face (SUB28/29 BinOps)
t229 = blob("e485a0b3f", "research/PERPETUAL_N1_W229_PREREG.md")  # RAM/label face (SUB29/30 BinOps)
t230 = blob("91de0ae83", "research/PERPETUAL_N1_W230_PREREG.md")  # RAM/label face (SUB30/31 BinOps)
t231 = blob("aebe0a5ac", "research/PERPETUAL_N1_W231_PREREG.md")  # RAM/label face (SUB31/32 BinOps)
t232 = blob("a3a7aa632", "research/PERPETUAL_N1_W232_PREREG.md")  # RAM/label face (SUB32/33 BinOps)
t = blob("933e3ceea", "research/PERPETUAL_N1_W233_PREREG.md")    # base: freeze-time W233 face
assert "## §7" in t and "占位" in t, "not the freeze-time (pre-backfill) face"

def ram_face(txt):
    m = re.search(r"本窗 free RAM ~(\d+\.\d)GB", txt)
    assert m, "RAM note face not found"
    return "~" + m.group(1)

def win_label(txt):
    m = re.search(r"freeze 窗·(2026-10-1[23] \d+:\d+)x·", txt)
    assert m, "freeze-window label face not found"
    return m.group(1) + "x·"

RAM_REPLAY_219 = ram_face(t219)
RAM_FACE_220 = ram_face(t220)
RAM_FACE_221 = ram_face(t221)
RAM_FACE_222 = ram_face(t222)
RAM_FACE_223 = ram_face(t223)
RAM_FACE_224 = ram_face(t224)
RAM_FACE_225 = ram_face(t225)
RAM_FACE_226 = ram_face(t226)
RAM_FACE_227 = ram_face(t227)
RAM_FACE_228 = ram_face(t228)
RAM_FACE_229 = ram_face(t229)
RAM_FACE_230 = ram_face(t230)
RAM_FACE_231 = ram_face(t231)
RAM_FACE_232 = ram_face(t232)
RAM_FACE_233 = ram_face(t)
WIN_LABEL_REPLAY = win_label(t225)
WIN_LABEL_226 = win_label(t226)
WIN_LABEL_227 = win_label(t227)
WIN_LABEL_228 = win_label(t228)
WIN_LABEL_229 = win_label(t229)
WIN_LABEL_230 = win_label(t230)
WIN_LABEL_231 = win_label(t231)
WIN_LABEL_232 = win_label(t232)
WIN_LABEL_233 = win_label(t)
print(f"RAM anchors: W219-face {RAM_REPLAY_219!r} | W220-face {RAM_FACE_220!r} | W221-face {RAM_FACE_221!r} | W222-face {RAM_FACE_222!r} | W223-face {RAM_FACE_223!r} | W224-face {RAM_FACE_224!r} | W225-face {RAM_FACE_225!r} | W226-face {RAM_FACE_226!r} | W227-face {RAM_FACE_227!r} | W228-face {RAM_FACE_228!r} | W229-face {RAM_FACE_229!r} | W230-face {RAM_FACE_230!r} | W231-face {RAM_FACE_231!r} | W232-face {RAM_FACE_232!r} | W233-face {RAM_FACE_233!r} | WIN_LABEL_REPLAY {WIN_LABEL_REPLAY!r} | WIN_LABEL_226 {WIN_LABEL_226!r} | WIN_LABEL_227 {WIN_LABEL_227!r} | WIN_LABEL_228 {WIN_LABEL_228!r} | WIN_LABEL_229 {WIN_LABEL_229!r} | WIN_LABEL_230 {WIN_LABEL_230!r} | WIN_LABEL_231 {WIN_LABEL_231!r} | WIN_LABEL_232 {WIN_LABEL_232!r} | WIN_LABEL_233 {WIN_LABEL_233!r}")

# ---------- replay-extract literals (lineage, zero transcription) ----------
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

pairs216 = extract_lit(r"results\_w216bmc_prereg_derive.py", "PAIRS", 46)
SUB17 = extract_lit(r"results\_w217bmc_prereg_derive.py", "SUB", 46)
SUB18 = extract_lit(r"results\_w218bmc_prereg_derive.py", "SUB", 46)
SUB19 = extract_lit(r"results\_w219bmc_prereg_derive.py", "SUB", 46,
                    vars={"RAM_GB": RAM_REPLAY_219})
SUB20 = extract_lit(r"results\_w220bmc_prereg_derive.py", "SUB", 46,
                    vars={"RAM_GB": RAM_FACE_220, "RAM_REPLAY": RAM_REPLAY_219})
SUB21 = extract_lit(r"results\_w221bmc_prereg_derive.py", "SUB", 46,
                    vars={"RAM_FACE_220": RAM_FACE_220, "RAM_GB": RAM_FACE_221})
SUB22 = extract_lit(r"results\_w222bmc_prereg_derive.py", "SUB", 46,
                    vars={"RAM_GB": RAM_FACE_222, "RAM_FACE_221": RAM_FACE_221})
SUB23 = extract_lit(r"results\_w223bmc_prereg_derive.py", "SUB", 46,
                    vars={"RAM_GB": RAM_FACE_223, "RAM_FACE_222": RAM_FACE_222})
SUB24 = extract_lit(r"results\_w224bmc_prereg_derive.py", "SUB", 46,
                    vars={"RAM_GB": RAM_FACE_224, "RAM_FACE_223": RAM_FACE_223})
SUB25 = extract_lit(r"results\_w225bmc_prereg_derive.py", "SUB", 46,
                    vars={"WIN_LABEL": WIN_LABEL_REPLAY, "RAM_GB": RAM_FACE_225,
                          "RAM_FACE_224": RAM_FACE_224})
SUB26 = extract_lit(r"results\_w226bmc_prereg_derive.py", "SUB", 46,
                    vars={"WIN_LABEL_REPLAY": WIN_LABEL_REPLAY, "WIN_LABEL": WIN_LABEL_226,
                          "RAM_FACE_225": RAM_FACE_225, "RAM_GB": RAM_FACE_226})
SUB27 = extract_lit(r"results\_w227bmc_prereg_derive.py", "SUB", 46,
                    vars={"WIN_LABEL_226": WIN_LABEL_226, "WIN_LABEL": WIN_LABEL_227,
                          "RAM_FACE_226": RAM_FACE_226, "RAM_GB": RAM_FACE_227})
SUB28 = extract_lit(r"results\_w228bmc_prereg_derive.py", "SUB", 46,
                    vars={"WIN_LABEL_227": WIN_LABEL_227, "WIN_LABEL": WIN_LABEL_228,
                          "RAM_FACE_227": RAM_FACE_227, "RAM_GB": RAM_FACE_228})
SUB29 = extract_lit(r"results\_w229bmc_prereg_derive.py", "SUB", 46,
                    vars={"WIN_LABEL_228": WIN_LABEL_228, "WIN_LABEL": WIN_LABEL_229,
                          "RAM_FACE_228": RAM_FACE_228, "RAM_GB": RAM_FACE_229})
SUB30 = extract_lit(r"results\_w230bmc_prereg_derive.py", "SUB", 46,
                    vars={"WIN_LABEL_229": WIN_LABEL_229, "WIN_LABEL": WIN_LABEL_230,
                          "RAM_FACE_229": RAM_FACE_229, "RAM_GB": RAM_FACE_230})
SUB31 = extract_lit(r"results\_w231bmc_prereg_derive.py", "SUB", 46,
                    vars={"WIN_LABEL_230": WIN_LABEL_230, "WIN_LABEL": WIN_LABEL_231,
                          "RAM_FACE_230": RAM_FACE_230, "RAM_GB": RAM_FACE_231})
SUB32 = extract_lit(r"results\_w232bmc_prereg_derive.py", "SUB", 46,
                    vars={"WIN_LABEL_231": WIN_LABEL_231, "WIN_LABEL": WIN_LABEL_232,
                          "RAM_FACE_231": RAM_FACE_231, "RAM_GB": RAM_FACE_232})
SUB33 = extract_lit(r"results\_w233bmc_prereg_derive.py", "SUB", 46,
                    vars={"WIN_LABEL_232": WIN_LABEL_232, "WIN_LABEL": WIN_LABEL_233,
                          "RAM_FACE_232": RAM_FACE_232, "RAM_GB": RAM_FACE_233})

def lvl(prev, SUB, mats):
    out = []
    for i, old in enumerate(prev):
        new = old
        for find, repl in SUB[i]:
            c = new.count(find)
            assert c == 1, f"replay count {c} != 1 idx{i}: {find[:60]}..."
            new = new.replace(find, repl, 1)
        for tok, num in mats:
            new = new.replace(tok, num)
        out.append(new)
    return out

OLD16 = [b.replace("@L14@", "214").replace("@T15@", "15") for _, b in pairs216]
OLD17 = lvl(OLD16, SUB17, [("@L14@", "214"), ("@L15@", "215"), ("@T16@", "16")])
OLD18 = lvl(OLD17, SUB18, [("@L14@", "214"), ("@L15@", "215"), ("@L16@", "216"), ("@T17@", "17")])
OLD19 = lvl(OLD18, SUB19, [("@L14@", "214"), ("@L15@", "215"), ("@L16@", "216"), ("@L17@", "217"), ("@T18@", "18")])
OLD20 = lvl(OLD19, SUB20, [("@L14@", "214"), ("@L15@", "215"), ("@L16@", "216"), ("@L17@", "217"), ("@L18@", "218"), ("@T19@", "19")])

# W220 editor_gen same-window fix replay (r923 absorb: freeze-window label
# corrected in the committed face; lineage must reproduce it)
_fixW_old = "【bm-c 循环班 r922 freeze 窗·2026-10-12 10:5x·"
_fixW_new = "【bm-c 循环班 r923 freeze 窗（absorb r922 freeze-prep estate）·2026-10-12 11:4x·"
assert OLD20[0].count(_fixW_old) == 1, "W220 editor_gen fix anchor missing in replayed block[0]"
OLD20[0] = OLD20[0].replace(_fixW_old, _fixW_new, 1)

OLD21 = lvl(OLD20, SUB21, [("@L14@", "214"), ("@L15@", "215"), ("@L16@", "216"), ("@L17@", "217"), ("@L18@", "218"), ("@L19@", "219"), ("@T15@", "15"), ("@T16@", "16"), ("@T17@", "17"), ("@T18@", "18"), ("@T19@", "20")])

# r927 pre-burn prose fixes replay (cf0b51d21 corrective steps; the committed
# W221 face carries both -- lineage must reproduce them)
_fixA_old = "账本头 907,589 机读·n1_w220_results.json·12:0x"
_fixA_new = "账本头 907,789 机读·n1_w220_results.json·12:0x"
assert OLD21[3].count(_fixA_old) == 1, "r927 fixA anchor missing"
OLD21[3] = OLD21[3].replace(_fixA_old, _fixA_new, 1)
_fixB_old = "W219 块的 W218 leg（1 行）不入 estate 路径·提取后新增 W218+W219 leg 构成 W221 块 parity 79 行"
_fixB_new = "W220 块的 W219 leg（1 行）不入 estate 路径·提取后新增 W219+W220 leg 构成 W221 块 parity 79 行"
assert OLD21[30].count(_fixB_old) == 1, "r927 fixB anchor missing"
OLD21[30] = OLD21[30].replace(_fixB_old, _fixB_new, 1)

OLD22 = lvl(OLD21, SUB22, [("@L14@", "214"), ("@L15@", "215"), ("@L16@", "216"), ("@L17@", "217"), ("@L18@", "218"), ("@L19@", "219"), ("@L20@", "220"), ("@T15@", "15"), ("@T16@", "16"), ("@T17@", "17"), ("@T18@", "18"), ("@T19@", "20"), ("@T20@", "21")])
OLD23 = lvl(OLD22, SUB23, [("@L14@", "214"), ("@L15@", "215"), ("@L16@", "216"), ("@L17@", "217"), ("@L18@", "218"), ("@L19@", "219"), ("@L20@", "220"), ("@L21@", "221"), ("@T15@", "15"), ("@T16@", "16"), ("@T17@", "17"), ("@T18@", "18"), ("@T19@", "20"), ("@T20@", "21"), ("@T21@", "22")])
OLD24 = lvl(OLD23, SUB24, [("@L14@", "214"), ("@L15@", "215"), ("@L16@", "216"), ("@L17@", "217"), ("@L18@", "218"), ("@L19@", "219"), ("@L20@", "220"), ("@L21@", "221"), ("@L22@", "222"), ("@T15@", "15"), ("@T16@", "16"), ("@T17@", "17"), ("@T18@", "18"), ("@T19@", "20"), ("@T20@", "21"), ("@T21@", "22"), ("@T22@", "23")])
OLD25 = lvl(OLD24, SUB25, [("@L14@", "214"), ("@L15@", "215"), ("@L16@", "216"), ("@L17@", "217"), ("@L18@", "218"), ("@L19@", "219"), ("@L20@", "220"), ("@L21@", "221"), ("@L22@", "222"), ("@L23@", "223"), ("@T15@", "15"), ("@T16@", "16"), ("@T17@", "17"), ("@T18@", "18"), ("@T19@", "20"), ("@T20@", "21"), ("@T21@", "22"), ("@T22@", "23"), ("@T23@", "24")])
OLD26 = lvl(OLD25, SUB26, [("@L14@", "214"), ("@L15@", "215"), ("@L16@", "216"), ("@L17@", "217"), ("@L18@", "218"), ("@L19@", "219"), ("@L20@", "220"), ("@L21@", "221"), ("@L22@", "222"), ("@L23@", "223"), ("@L24@", "224"), ("@T15@", "15"), ("@T16@", "16"), ("@T17@", "17"), ("@T18@", "18"), ("@T19@", "20"), ("@T20@", "21"), ("@T21@", "22"), ("@T22@", "23"), ("@T23@", "24"), ("@T24@", "25")])
OLD27 = lvl(OLD26, SUB27, [("@L14@", "214"), ("@L15@", "215"), ("@L16@", "216"), ("@L17@", "217"), ("@L18@", "218"), ("@L19@", "219"), ("@L20@", "220"), ("@L21@", "221"), ("@L22@", "222"), ("@L23@", "223"), ("@L24@", "224"), ("@L25@", "225"), ("@T15@", "15"), ("@T16@", "16"), ("@T17@", "17"), ("@T18@", "18"), ("@T19@", "20"), ("@T20@", "21"), ("@T21@", "22"), ("@T22@", "23"), ("@T23@", "24"), ("@T24@", "25"), ("@T25@", "26")])
OLD28 = lvl(OLD27, SUB28, [("@L14@", "214"), ("@L15@", "215"), ("@L16@", "216"), ("@L17@", "217"), ("@L18@", "218"), ("@L19@", "219"), ("@L20@", "220"), ("@L21@", "221"), ("@L22@", "222"), ("@L23@", "223"), ("@L24@", "224"), ("@L25@", "225"), ("@L26@", "226"), ("@T15@", "15"), ("@T16@", "16"), ("@T17@", "17"), ("@T18@", "18"), ("@T19@", "20"), ("@T20@", "21"), ("@T21@", "22"), ("@T22@", "23"), ("@T23@", "24"), ("@T24@", "25"), ("@T25@", "26"), ("@T26@", "27")])
OLD29 = lvl(OLD28, SUB29, [("@L14@", "214"), ("@L15@", "215"), ("@L16@", "216"), ("@L17@", "217"), ("@L18@", "218"), ("@L19@", "219"), ("@L20@", "220"), ("@L21@", "221"), ("@L22@", "222"), ("@L23@", "223"), ("@L24@", "224"), ("@L25@", "225"), ("@L26@", "226"), ("@L27@", "227"), ("@T15@", "15"), ("@T16@", "16"), ("@T17@", "17"), ("@T18@", "18"), ("@T19@", "20"), ("@T20@", "21"), ("@T21@", "22"), ("@T22@", "23"), ("@T23@", "24"), ("@T24@", "25"), ("@T25@", "26"), ("@T26@", "27"), ("@T27@", "28")])
OLD30 = lvl(OLD29, SUB30, [("@L14@", "214"), ("@L15@", "215"), ("@L16@", "216"), ("@L17@", "217"), ("@L18@", "218"), ("@L19@", "219"), ("@L20@", "220"), ("@L21@", "221"), ("@L22@", "222"), ("@L23@", "223"), ("@L24@", "224"), ("@L25@", "225"), ("@L26@", "226"), ("@L27@", "227"), ("@L28@", "228"), ("@T15@", "15"), ("@T16@", "16"), ("@T17@", "17"), ("@T18@", "18"), ("@T19@", "20"), ("@T20@", "21"), ("@T21@", "22"), ("@T22@", "23"), ("@T23@", "24"), ("@T24@", "25"), ("@T25@", "26"), ("@T26@", "27"), ("@T27@", "28"), ("@T28@", "29")])
OLD31 = lvl(OLD30, SUB31, [("@L14@", "214"), ("@L15@", "215"), ("@L16@", "216"), ("@L17@", "217"), ("@L18@", "218"), ("@L19@", "219"), ("@L20@", "220"), ("@L21@", "221"), ("@L22@", "222"), ("@L23@", "223"), ("@L24@", "224"), ("@L25@", "225"), ("@L26@", "226"), ("@L27@", "227"), ("@L28@", "228"), ("@L29@", "229"), ("@T15@", "15"), ("@T16@", "16"), ("@T17@", "17"), ("@T18@", "18"), ("@T19@", "20"), ("@T20@", "21"), ("@T21@", "22"), ("@T22@", "23"), ("@T23@", "24"), ("@T24@", "25"), ("@T25@", "26"), ("@T26@", "27"), ("@T27@", "28"), ("@T28@", "29"), ("@T29@", "30")])
OLD32 = lvl(OLD31, SUB32, [("@L14@", "214"), ("@L15@", "215"), ("@L16@", "216"), ("@L17@", "217"), ("@L18@", "218"), ("@L19@", "219"), ("@L20@", "220"), ("@L21@", "221"), ("@L22@", "222"), ("@L23@", "223"), ("@L24@", "224"), ("@L25@", "225"), ("@L26@", "226"), ("@L27@", "227"), ("@L28@", "228"), ("@L29@", "229"), ("@L30@", "230"), ("@T15@", "15"), ("@T16@", "16"), ("@T17@", "17"), ("@T18@", "18"), ("@T19@", "20"), ("@T20@", "21"), ("@T21@", "22"), ("@T22@", "23"), ("@T23@", "24"), ("@T24@", "25"), ("@T25@", "26"), ("@T26@", "27"), ("@T27@", "28"), ("@T28@", "29"), ("@T29@", "30"), ("@T30@", "31")])
OLD33 = lvl(OLD32, SUB33, [("@L14@", "214"), ("@L15@", "215"), ("@L16@", "216"), ("@L17@", "217"), ("@L18@", "218"), ("@L19@", "219"), ("@L20@", "220"), ("@L21@", "221"), ("@L22@", "222"), ("@L23@", "223"), ("@L24@", "224"), ("@L25@", "225"), ("@L26@", "226"), ("@L27@", "227"), ("@L28@", "228"), ("@L29@", "229"), ("@L30@", "230"), ("@L31@", "231"), ("@T15@", "15"), ("@T16@", "16"), ("@T17@", "17"), ("@T18@", "18"), ("@T19@", "20"), ("@T20@", "21"), ("@T21@", "22"), ("@T22@", "23"), ("@T23@", "24"), ("@T24@", "25"), ("@T25@", "26"), ("@T26@", "27"), ("@T27@", "28"), ("@T28@", "29"), ("@T29@", "30"), ("@T30@", "31"), ("@T31@", "32")])

# preflight: every replayed W233-face block sits exactly once in the blob
for i, old in enumerate(OLD33):
    c = t.count(old)
    assert c == 1, f"preflight block[{i}] count {c} != 1 in freeze-time W233 blob"
print("preflight OK: 46/46 replayed blocks sit count==1 in the freeze-time W233 blob")

# ---------- machine-derived anchors (never hand-copied) ----------
rec = json.load(open(r"results\_w234bmc_20261013_probe_receipt.json", encoding="utf-8"))
assert rec["verdict"] == "ADMIT" and rec["bands"] == {"A": "529604_531603", "B": "531604_531803"}
w233 = json.load(open(r"results\perpetual_faces\n1_w233_results.json", encoding="utf-8"))
led = w233["science_gates"]["ledger"]
assert led["total"] == 936389 and led["prev_total"] == 934189 and led["batch_trials"] == 2200
merged = w233["null_pool_cumulative"]["merged"]
assert merged["n_values"] == 510520
w233only = w233["null_pool_cumulative"]["w233_only"]
A_p95 = w233["families"]["A_random_engine_exit"]["full_sharpe_p95"]
kl = w233["skill_line_v2_k_lift"]
assert kl["line_delta_k_lift"] == -0.0002 and kl["n_eff_held_equal"] == 934189
assert kl["line_pre_w233"] == 1.1924 and kl["line_merged_510520"] == 1.1922
se_mu = w233["null_pool_cumulative"]["se_mu_at_k510520"]
assert se_mu == 0.000343
leg1, leg4 = rec["legs"]["leg1"], rec["legs"]["leg4"]
assert leg1["A"] == [529604, 531603] and leg1["B"] == [531604, 531803]
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
assert leg1["ARITH_A"] == [529404, 531403] and leg1["B_naive_first_clean"] == [529604, 529803]
assert leg4["W234p_A"] == "531604..533603" and leg4["W234p_B"] == "531804..532003"
assert leg4["W234p_B_lands_inside_W234p_A"] is True
leg0 = rec["legs"]["leg0"]
assert leg0["rows"] == 231 and leg0["owner_rows"] == 223 and leg0["bmc_rows"] == 63 \
       and leg0["bmc_ordinal"] == 64 and leg0["ordinal"] == 224
assert "attempt-continuity" in leg0["bmc_ordinal_note"] and "63rd owned" in leg0["bmc_ordinal_note"]
fr = json.load(open(r"results\_w233bmc_freeze_receipt.json", encoding="utf-8"))
assert fr["ordinal_faces"]["bmc_own_ordinal"] == 63  # "63rd owned 承袭" prose anchor
# formatted-string guards: every literal below that carries a machine value
# is assert-verified against the live JSON here (zero eyeball)
def fmt8(x):
    return ("\u2212" if x < 0 else "") + f"{abs(x):.8f}"
assert fmt8(merged["mu"]) == "\u2212" + "0.09276956", fmt8(merged["mu"])
assert fmt8(w233only["mu"]) == "\u2212" + "0.09893318", fmt8(w233only["mu"])
assert f"{merged['sigma']:.8f}" == "0.24506207", f"{merged['sigma']:.8f}"
assert f"{abs(w233only['mu'] - merged['mu']):.4f}" == "0.0062", f"{abs(w233only['mu'] - merged['mu']):.4f}"
assert f"{A_p95:.4f}" == "0.3027", f"{A_p95:.4f}"
assert f"{kl['line_merged_510520']:.4f}" == "1.1922"
assert f"{kl['line_delta_k_lift']:+.4f}" == "-0.0002"  # ASCII f-string face; prose token uses U+2212 minus (R34[37] face)
# free RAM live read (honesty for the RAM note). Band kept wide at the low
# end: resident chassis load keeps the box near the floor some windows --
# honest face, engine RAM gate governs burn admission separately.
import psutil
_avail_gb = psutil.virtual_memory().available / 1e9
assert 0.03 <= _avail_gb <= 8.0, f"unexpected RAM face: {_avail_gb}"
RAM_GB = f"~{_avail_gb:.1f}"
print(f"live free RAM: {_avail_gb:.2f} GB -> note '{RAM_GB}GB'")
# engine live status (honesty for the block-1 carried face)
_st = subprocess.run([sys.executable, "Tools/saturation_engine.py", "status"],
                     cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
assert _st.returncode == 0, f"engine status FAIL: {(_st.stdout or '')[-300:]}"
assert '"burns_active": []' in (_st.stdout or "") or "'burns_active': []" in (_st.stdout or "") or '"burns_active":[]' in (_st.stdout or ""), "engine burns_active not empty at derive time"
assert '"queue_next": []' in (_st.stdout or "") or "'queue_next': []" in (_st.stdout or "") or '"queue_next":[]' in (_st.stdout or ""), "engine queue_next not empty at derive time"
print("engine live status: burns_active=[] queue_next=[] verified")
# freeze-window label (live honesty): this derivation runs in r976, 2026-10-13
_now = datetime.datetime.now()
assert (_now.year, _now.month, _now.day) == (2026, 10, 13), f"unexpected clock: {_now}"
WIN_LABEL = f"2026-10-13 {_now.hour}:{_now.minute // 10}x·"
print(f"freeze-window label: r976 {WIN_LABEL}")

SUB = {
 0: [('PERPETUAL-N1-W233 预注册 · N1 nulls-deepening 泵第 231 枚','PERPETUAL-N1-W234 预注册 · N1 nulls-deepening 泵第 232 枚'),
      ('engine_owner 行 222 注册在册（表尾 W232 行·probe leg0 机证 230 行','engine_owner 行 223 注册在册（表尾 W233 行·probe leg0 机证 231 行'),
      ('本候选=bm-c 第六十三枚自有波【live-derive face：席面 prose 63rd=seat-time face（r968 窗 W232 注册后 attempt-continuity live derive·r968 freeze receipt 62nd owned 承袭）→freeze 时 live derive bm-c rows 62+候选=第 63 枚 EXACT','本候选=bm-c 第六十四枚自有波【live-derive face：席面 prose 64th=seat-time face（r974 窗 W233 注册后 attempt-continuity live derive·r973 freeze receipt 63rd owned 承袭）→freeze 时 live derive bm-c rows 63+候选=第 64 枚 EXACT'),
      ("【bm-c 循环班 r972 freeze 窗·" + WIN_LABEL_233,"【bm-c 循环班 r976 freeze 窗·" + WIN_LABEL)],
 1: [('saturation_engine.py status live-read r972：','saturation_engine.py status live-read r976：')],
 2: [('**波号 233=注册表 W232 席后首个自由号**','**波号 234=注册表 W233 席后首个自由号**'),
      ('r972 窗实跑：origin inbox/processed/ 零 W233 席位外机命中','r976 窗实跑：origin inbox/processed/ 零 W234 席位外机命中'),
      ('origin perpetual_faces.py 零 233 行','origin perpetual_faces.py 零 234 行'),
      ('perpetual_faces_n1.py 零 PERPETUAL-N1-W233 WAVE_CONFIGS','perpetual_faces_n1.py 零 PERPETUAL-N1-W234 WAVE_CONFIGS'),
      ('origin 零 PERPETUAL_N1_W233_PREREG.md','origin 零 PERPETUAL_N1_W234_PREREG.md')],
 3: [('+W221=bm-c r928 五面冻结（98da27a40）+引擎自燃 12/12+r928 finalize one-pass 已落（K=484,120·账本头 909,989 机读·n1_w221_results.json·14:1x）+W222=bm-c r931 死窗五面冻结 estate 落盘·r932 absorb 提交（4167d791d）+引擎自燃 12/12+r932 finalize one-pass 已落（K=486,320·账本头 912,189 机读·n1_w222_results.json·15:5x）+W223=bm-c r934 五面冻结（448c4d8c2）+引擎自燃 12/12+r935 finalize one-pass 已落（K=488,520·账本头 914,389 机读·n1_w223_results.json·17:2x）+W224=bm-c r937 死窗五面冻结 estate 落盘·r937 absorb 提交（d307e3d1d）+引擎自燃 12/12+r937 finalize one-pass 已落（K=490,720·账本头 916,589 机读·n1_w224_results.json·19:1x）+W225=bm-c r939 五面冻结（84ecb3a3a）+引擎自燃 12/12+r940 finalize one-pass 已落（K=492,920·账本头 918,789 机读·n1_w225_results.json·20:2x）+W226=bm-c r943 死窗五面冻结 estate 落盘·r945 absorb 提交（bd50be730）+引擎自燃 12/12+r943 finalize one-pass 已落（K=495,120·账本头 920,989 机读·n1_w226_results.json·22:4x）+W227=bm-c r956 五面冻结（48c321706）+引擎自燃 12/12+r956 finalize one-pass 已落（K=497,320·账本头 923,189 机读·n1_w227_results.json·06:5x）+W228=bm-c r959 死窗五面冻结 estate 落盘·r959 absorb 提交（842f817ad）+引擎自燃 12/12+r959 finalize one-pass 已落（K=499,520·账本头 925,389 机读·n1_w228_results.json·08:3x）+W229=bm-c r961 死窗五面冻结 estate 落盘·r962 absorb 提交（2ae8553e6）+引擎自燃 12/12+r962 finalize one-pass 已落（K=501,720·账本头 927,589 机读·n1_w229_results.json·10:1x）+W230=bm-c r963 死窗五面冻结 estate 落盘·r963 absorb 提交（24e12fa5e）+引擎自燃 12/12+r963 finalize one-pass 已落（K=503,920·账本头 929,789 机读·n1_w230_results.json·11:5x）+W231=bm-c r966 五面冻结（aee0bd9fa）+引擎自燃 12/12+r966 finalize one-pass 已落（K=506,120·账本头 931,989 机读·n1_w231_results.json·13:2x）+W232=bm-c r968 死窗五面冻结 estate 落盘·r968 absorb 提交（e58dbcda3）+引擎自燃 12/12+r968 finalize one-pass 已落（K=508,320·账本头 934,189 机读·n1_w232_results.json·15:2x）——本波上游链=W1..W232 finalize 全落地','+W221=bm-c r928 五面冻结（98da27a40）+引擎自燃 12/12+r928 finalize one-pass 已落（K=484,120·账本头 909,989 机读·n1_w221_results.json·14:1x）+W222=bm-c r931 死窗五面冻结 estate 落盘·r932 absorb 提交（4167d791d）+引擎自燃 12/12+r932 finalize one-pass 已落（K=486,320·账本头 912,189 机读·n1_w222_results.json·15:5x）+W223=bm-c r934 五面冻结（448c4d8c2）+引擎自燃 12/12+r935 finalize one-pass 已落（K=488,520·账本头 914,389 机读·n1_w223_results.json·17:2x）+W224=bm-c r937 死窗五面冻结 estate 落盘·r937 absorb 提交（d307e3d1d）+引擎自燃 12/12+r937 finalize one-pass 已落（K=490,720·账本头 916,589 机读·n1_w224_results.json·19:1x）+W225=bm-c r939 五面冻结（84ecb3a3a）+引擎自燃 12/12+r940 finalize one-pass 已落（K=492,920·账本头 918,789 机读·n1_w225_results.json·20:2x）+W226=bm-c r943 死窗五面冻结 estate 落盘·r945 absorb 提交（bd50be730）+引擎自燃 12/12+r943 finalize one-pass 已落（K=495,120·账本头 920,989 机读·n1_w226_results.json·22:4x）+W227=bm-c r956 五面冻结（48c321706）+引擎自燃 12/12+r956 finalize one-pass 已落（K=497,320·账本头 923,189 机读·n1_w227_results.json·06:5x）+W228=bm-c r959 死窗五面冻结 estate 落盘·r959 absorb 提交（842f817ad）+引擎自燃 12/12+r959 finalize one-pass 已落（K=499,520·账本头 925,389 机读·n1_w228_results.json·08:3x）+W229=bm-c r961 死窗五面冻结 estate 落盘·r962 absorb 提交（2ae8553e6）+引擎自燃 12/12+r962 finalize one-pass 已落（K=501,720·账本头 927,589 机读·n1_w229_results.json·10:1x）+W230=bm-c r963 死窗五面冻结 estate 落盘·r963 absorb 提交（24e12fa5e）+引擎自燃 12/12+r963 finalize one-pass 已落（K=503,920·账本头 929,789 机读·n1_w230_results.json·11:5x）+W231=bm-c r966 五面冻结（aee0bd9fa）+引擎自燃 12/12+r966 finalize one-pass 已落（K=506,120·账本头 931,989 机读·n1_w231_results.json·13:2x）+W@L32@=bm-c r968 死窗五面冻结 estate 落盘·r968 absorb 提交（e58dbcda3）+引擎自燃 12/12+r968 finalize one-pass 已落（K=508,320·账本头 934,189 机读·n1_w2@L32@_results.json·15:2x）+W233=bm-c r973 死窗五面冻结（0ca920362）+引擎自燃 12/12+r974 finalize one-pass 已落（K=510,520·账本头 936,389 机读·n1_w233_results.json·19:5x）——本波上游链=W1..W233 finalize 全落地')],
 4: [('本机席位公示=MSG-20261013-1530-bmc 已推 origin dd38a9da8 先于本冻结【r565 律·席位先行·r968 窗】；下游 W234+ 投影见 §5.5（probe 机证 leg4·W234 freezer 承接面）】。','本机席位公示=MSG-20261013-1955-bmc 已推 origin 260217d39 先于本冻结【r565 律·席位先行·r974 窗】；下游 W235+ 投影见 §5.5（probe 机证 leg4·W235 freezer 承接面）】。')],
 5: [('W2..W232 全注册在冻结时点成立','W2..W233 全注册在冻结时点成立')],
 6: [('ADMIT 回执=results/_w233bmc_20261013_probe_receipt.json','ADMIT 回执=results/_w234bmc_20261013_probe_receipt.json')],
 7: [('**A-ext seed=527_404..529_403**','**A-ext seed=529_604..531_603**'),
      ('**A 面=FIRST-CLEAN past prior-wave B 阶梯第九十三例**','**A 面=FIRST-CLEAN past prior-wave B 阶梯第九十四例**'),
      ('A 面算术继续带 527_204..529_203（自注册 W232 A 尾 527_203 续）在其起点即被 W232 注册 B 带 527_204..527_403 **拒**（W232 席位 leg4 投影+其 probe 所预言+强制）→ 诚实前向走 **1 hop** 落 **527_404..529_403**','A 面算术继续带 529_404..531_403（自注册 W233 A 尾 529_403 续）在其起点即被 W233 注册 B 带 529_404..529_603 **拒**（W233 席位 leg4 投影+其 probe 所预言+强制）→ 诚实前向走 **1 hop** 落 **529_604..531_603**'),
      ('**A base==前波 B 尾+1（527_403+1）机检关系**','**A base==前波 B 尾+1（529_603+1）机检关系**'),
      ('=**A-hops-prior-B 阶梯几何第九十三例（E36 卡）**','=**A-hops-prior-B 阶梯几何第九十四例（E36 卡）**'),
      ('A_semantics 机读序数=NINETY-THIRD（第九十三例）','A_semantics 机读序数=NINETY-FOURTH（第九十四例）')],
 8: [('**B-ext exit seed=529_404..529_603**','**B-ext exit seed=531_604..531_803**'),
      ('B 面 naive first-clean 继续带 527_404..527_603 在注册宇宙上 CLEAN 但**落在本波 A 窗 527_404..529_403 内**','B 面 naive first-clean 继续带 529_604..529_803 在注册宇宙上 CLEAN 但**落在本波 A 窗 529_604..531_603 内**'),
      ('→ B 带本波 A 窗保留走 **1 hop** 落 **529_404..529_603**','→ B 带本波 A 窗保留走 **1 hop** 落 **531_604..531_803**'),
      ('**B base==本波 A 尾+1（529_403+1）机检关系**','**B base==本波 A 尾+1（531_603+1）机检关系**'),
      ('**W232 席位 leg4 投影承接面注记兑现**：投影预言 W233 须在 post-W232 注册宇宙重 derive 且 derive B 时预留本波 A 窗','**W233 席位 leg4 投影承接面注记兑现**：投影预言 W234 须在 post-W233 注册宇宙重 derive 且 derive B 时预留本波 A 窗')],
 9: [('R250：W233 带从未指派','R250：W234 带从未指派')],
 10: [('A base=527404 span=2000 checked=2000 verdict=FREE / B base=529404 span=200 checked=200 verdict=FREE','A base=529604 span=2000 checked=2000 verdict=FREE / B base=531604 span=200 checked=200 verdict=FREE')],
 11: [('扫描面=pre-W233 全二百三十行注册 N1 带表（表尾 W232 行·probe leg0 机证 230 行 live 单态 owner rows 222）','扫描面=pre-W234 全二百三十一行注册 N1 带表（表尾 W233 行·probe leg0 机证 231 行 live 单态 owner rows 223）')],
 12: [('`scripts/perpetual_faces_n1.py`（W2..W232 落地 runner 的 wave 参数化复用','`scripts/perpetual_faces_n1.py`（W2..W233 落地 runner 的 wave 参数化复用')],
 13: [('selftest W233 face 将随五面冻结落地验证','selftest W234 face 将随五面冻结落地验证')],
 14: [('本件与 results/_w233bmc_freeze_edits.py','本件与 results/_w234bmc_freeze_edits.py'),
      ('按 _w232bmc_freeze_edits.py 模板派生','按 _w2@T32@bmc_freeze_edits.py 模板派生'),
      ('gate0.5 自查 W232 行+W232 finalize 件在场','gate0.5 自查 W233 行+W233 finalize 件在场'),
      ('estate 提取面=本机 W232 块物理字节','estate 提取面=本机 W233 块物理字节'),
      ('（r968/W232 先例 freeze-prep 同式','（r973/W233 先例 freeze-prep 同式')],
 15: [('- 批名=**PERPETUAL-N1-W233**。','- 批名=**PERPETUAL-N1-W234**。')],
 16: [('**W1..W232 N1 finalize 已全部落地**【净账本锚头 **934,189**·K=508,320 合并池·n1_w232_results.json 机读·W232 finalize one-pass bm-c r968 窗 15:2x（W232 面完整性=12/12 shards consumed+finalize audit finalize_only=true 收口·r968 splice e58dbcda3+引擎自燃链如实注记）】','**W1..W233 N1 finalize 已全部落地**【净账本锚头 **936,389**·K=510,520 合并池·n1_w233_results.json 机读·W233 finalize one-pass bm-c r974 窗 19:5x（W233 面完整性=12/12 shards consumed+finalize audit finalize_only=true 收口·r973 splice 0ca920362+引擎自燃链如实注记）】')],
 17: [('累计 null 池=508,320+2,200（本波）=**510,520 投影**','累计 null 池=510,520+2,200（本波）=**512,720 投影**')],
 18: [('（本机席位公示 MSG-20261013-1530-bmc 已推 origin dd38a9da8 r565 律·probe W234+ 投影 A 529_404..531_403 / B 529_604..529_803','（本机席位公示 MSG-20261013-1955-bmc 已推 origin 260217d39 r565 律·probe W235+ 投影 A 531_604..533_603 / B 531_804..532_003'),
      ('投影 B 落投影 A 窗内·W233 B 带 529_404..529_603 注册后将拒 naive W234 A 窗=阶梯 A-hops-prior-B 第九十四例——**W234 freezer 承接面强制注记：须在 post-W233 宇宙重 derive 且 derive B 时预留本波 A 窗','投影 B 落投影 A 窗内·W234 B 带 531_604..531_803 注册后将拒 naive W235 A 窗=阶梯 A-hops-prior-B 第九十五例——**W235 freezer 承接面强制注记：须在 post-W234 宇宙重 derive 且 derive B 时预留本波 A 窗')],
 19: [('T-2026-10-01-141 s1 引擎线第 223 波【bm-c 第六十三枚自有波【机面 derive：probe leg0 bmc_ordinal=63 attempt-continuity face（r968 窗计法·W232 splice/freeze receipt=62nd owned 承袭注记）——freeze 时 live derive bm-c rows 62+候选=第 63 枚 EXACT','T-2026-10-01-141 s1 引擎线第 224 波【bm-c 第六十四枚自有波【机面 derive：probe leg0 bmc_ordinal=64 attempt-continuity face（r974 窗计法·W233 splice/freeze receipt=63rd owned 承袭注记）——freeze 时 live derive bm-c rows 63+候选=第 64 枚 EXACT'),
      ('波号=注册表 W232 席后首个自由号·单态零席位空档于冻结时点成立；中位公示 MSG-20261013-1530-bmc 先推 origin dd38a9da8 r565 律','波号=注册表 W233 席后首个自由号·单态零席位空档于冻结时点成立；中位公示 MSG-20261013-1955-bmc 先推 origin 260217d39 r565 律')],
 20: [("本窗 free RAM " + RAM_FACE_233 + "GB","本窗 free RAM " + RAM_GB + "GB"),
      ('W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225/W226/W227/W228/W229/W230/W231/W232 低 RAM 实烧先例','W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225/W226/W227/W228/W229/W230/W231/W@L32@/W233 低 RAM 实烧先例')],
 21: [('复读自见 W233 行并点火自烧','复读自见 W234 行并点火自烧')],
 22: [('--prereg research/PERPETUAL_N1_W233_PREREG.md','--prereg research/PERPETUAL_N1_W234_PREREG.md')],
 23: [('（p2_calibration v1/v2 canon；v1 ext；v2..W232 落地）','（p2_calibration v1/v2 canon；v1 ext；v2..W233 落地）')],
 24: [('entry rng seed=**527_404+j**','entry rng seed=**529_604+j**'),
      ('法典 §4 W233 行 A=527_404..529_403','法典 §4 W234 行 A=529_604..531_603'),
      ('**FIRST-CLEAN past prior-wave B 阶梯第九十三例**：算术续带 527_204..529_203 起点即被 W232 注册 B 带 527_204..527_403 拒→1 hop 落 527_404..529_403','**FIRST-CLEAN past prior-wave B 阶梯第九十四例**：算术续带 529_404..531_403 起点即被 W233 注册 B 带 529_404..529_603 拒→1 hop 落 529_604..531_603')],
 25: [('entry rng=**527_404+j**','entry rng=**529_604+j**'),
      ('exit rng=**529_404+j**','exit rng=**531_604+j**'),
      ('法典 §4 W233 行 B=529_404..529_603','法典 §4 W234 行 B=531_604..531_803'),
      ('B 算术续带 527_404..527_603 在注册宇宙 CLEAN 但落在本波 A 窗 527_404..529_403 内','B 算术续带 529_604..529_803 在注册宇宙 CLEAN 但落在本波 A 窗 529_604..531_603 内'),
      ('保留走落 529_404..529_603','保留走落 531_604..531_803'),
      ('与 W232 席位 leg4 投影承接面注记兑现收敛','与 W233 席位 leg4 投影承接面注记兑现收敛')],
 26: [('种子带 disjoint 全例（selftest 强制）：W233 带与 v1 在用带','种子带 disjoint 全例（selftest 强制）：W234 带与 v1 在用带')],
 27: [('W2..W232 带（冻结时点全注册单态）','W2..W233 带（冻结时点全注册单态）')],
 28: [('本波机验 ADMIT 回执在场=_w233bmc_20261013 探针窗','本波机验 ADMIT 回执在场=_w234bmc_20261013 探针窗')],
 29: [('selftest W233 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W232 行 parity 腿','selftest W234 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W233 行 parity 腿')],
 30: [('从**本机 W232 块物理字节**提取','从**本机 W233 块物理字节**提取'),
      ('——W231 块的 W230 leg（1 行）不入 estate 路径·提取后新增 W230+W231 leg 构成 W233 块 parity 91 行（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W232）','——W@L32@ 块的 W231 leg（1 行）不入 estate 路径·提取后新增 W231+W@L32@ leg 构成 W234 块 parity 92 行（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W@L32@+W233）')],
 31: [('起草窗实流 W1..W232 已落账 508,320 实测','起草窗实流 W1..W233 已落账 510,520 实测')],
 32: [('batch_name="PERPETUAL-N1-W233", batch_trials=2200, file_name="results/perpetual_faces/n1_w233_results.json"','batch_name="PERPETUAL-N1-W234", batch_trials=2200, file_name="results/perpetual_faces/n1_w234_results.json"')],
 33: [('（起草窗实况注记：**W1..W232 N1 finalize 已全部落地**——净账本锚头 934,189·**K=508,320 合并池**·**零在飞上游席——本波 §5 预测键=**W232 实测值**【results/perpetual_faces/n1_w232_results.json·N1 面最新已落账键·15:2x finalize one-pass】。','（起草窗实况注记：**W1..W233 N1 finalize 已全部落地**——净账本锚头 936,389·**K=510,520 合并池**·**零在飞上游席——本波 §5 预测键=**W233 实测值**【results/perpetual_faces/n1_w233_results.json·N1 面最新已落账键·19:5x finalize one-pass】。')],
 34: [('1. W233-only mu 与累计池 merged mu（W232 实测键 **−0.09274288**·K=508,320 合并池·W232-only 实测 **−0.10490950**）差异 **|Δ|<0.02**（W2..W232 共二百三十面实测 mu 稳定先例·单波跨键微；W232-only vs merged 实差 0.0122 在带内）。','1. W234-only mu 与累计池 merged mu（W233 实测键 **−0.09276956**·K=510,520 合并池·W233-only 实测 **−0.09893318**）差异 **|Δ|<0.02**（W2..W233 共二百三十一面实测 mu 稳定先例·单波跨键微；W233-only vs merged 实差 0.0062 在带内）。')],
 35: [('键 **0.24508296**=W232 合并池实测）。','键 **0.24506207**=W233 合并池实测）。')],
 36: [('3. A 档 full_sharpe_p95 与 W232 A 档 p95（**0.3063** 实测锚）差 **<0.05**（门标注法 W5..W232 先例','3. A 档 full_sharpe_p95 与 W233 A 档 p95（**0.3027** 实测锚）差 **<0.05**（门标注法 W5..W233 先例')],
 37: [('W136..W232 先例链披露','W136..W233 先例链披露'),
      ('键 W232 实测 K-lift **+0.0001**·line_merged@K508,320 **1.1923**·line_pre_w232 1.1922·n_eff_held_equal 931,989','键 W233 实测 K-lift **−0.0002**·line_merged@K510,520 **1.1922**·line_pre_w233 1.1924·n_eff_held_equal 934,189'),
      ('se_mu 收窄链 …→W209 0.000362→W211 0.000361→W212 0.000360→W213 0.000359→W214 0.000358→W215 0.000357→W216 0.000356→W217 **0.000355**→W218 **0.000355**→W219 **0.000354**→W220 **0.000353**→W221 **0.000352**→W222 **0.000351**→W223 **0.000351**→W224 **0.00035**→W225 **0.000349**→W226 **0.000348**→W227 **0.000348**→W228 **0.000347**→W229 **0.000346**→W230 **0.000345**→W231 **0.000344**→W232 **0.000344**】','se_mu 收窄链 …→W209 0.000362→W211 0.000361→W212 0.000360→W213 0.000359→W214 0.000358→W215 0.000357→W216 0.000356→W217 **0.000355**→W218 **0.000355**→W219 **0.000354**→W220 **0.000353**→W221 **0.000352**→W222 **0.000351**→W223 **0.000351**→W224 **0.00035**→W225 **0.000349**→W226 **0.000348**→W227 **0.000348**→W228 **0.000347**→W229 **0.000346**→W230 **0.000345**→W231 **0.000344**→W@L32@ **0.000344**→W233 **0.000343**】')],
 38: [('5. **W234+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 529_404..531_403 CLEAN（hops=0·pre-W233 宇宙）；B naive first-clean **529_604..529_803 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W234：W234 冻结方必须在 post-W233 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W233 B 带 529_404..529_603 注册后将拒 naive W234 A 窗**——W234 A 重 derive 同强制（越过 W233 B 带·阶梯 A-hops-prior-B 第九十四例）；verify at W234 prereg','5. **W235+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 531_604..533_603 CLEAN（hops=0·pre-W234 宇宙）；B naive first-clean **531_804..532_003 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W235：W235 冻结方必须在 post-W234 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W234 B 带 531_604..531_803 注册后将拒 naive W235 A 窗**——W235 A 重 derive 同强制（越过 W234 B 带·阶梯 A-hops-prior-B 第九十五例）；verify at W235 prereg')],
 39: [(' --wave 233/finalize --wave 233',' --wave 234/finalize --wave 234')],
 40: [('【n1_w233/ 分片计数增长·唯一点火证据·r325 律】','【n1_w234/ 分片计数增长·唯一点火证据·r325 律】')],
 41: [('`results/p2cal_ext/n1_w233/shard-<k>-of-12.json`','`results/p2cal_ext/n1_w234/shard-<k>-of-12.json`')],
 42: [('`results/perpetual_faces/n1_w233_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 键序前置=**起草窗零在飞上游席（W1..W232 全落）','`results/perpetual_faces/n1_w234_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 键序前置=**起草窗零在飞上游席（W1..W233 全落）')],
 43: [('engine_owner==bm-c 62 行注册〔冻结时点〕+ 本候选','engine_owner==bm-c 63 行注册〔冻结时点〕+ 本候选')],
 44: [('段——r968 W232 §7 范式）','段——r974 W233 §7 范式）')],
 45: [('（占位·finalize 同窗回填：§5.5 W234+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——r968 W232 §8 范式）','（占位·finalize 同窗回填：§5.5 W235+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——r974 W233 §8 范式）')],
}

# ---------- build + apply W234 pairs ----------
PAIRS = []
for i, old in enumerate(OLD33):
    new = old
    for find, repl in SUB[i]:
        c = new.count(find)
        assert c == 1, f"submap[{i}] count {c} != 1 for: {find[:60]}..."
        new = new.replace(find, repl, 1)
    PAIRS.append((old, new))

for old, new in PAIRS:
    c = t.count(old)
    assert c == 1, f"pair count {c} != 1: {old[:70]}..."
    t = t.replace(old, new, 1)

# ---- generic wave-token shifts (after targeted pairs) ----
# Pairs covered every W233 self face (each count==1 asserted). Remaining
# "W233" tokens = pair-written legit refs (chain W233 leg, refusing band,
# W233 finalize keys, W1..W233 scope) which must STAY W233 -- mask, then age
# one-wave-older W232 refs to W233, then restore. @L32@/@T32@ hold heritage
# tokens immune.
t = t.replace("n1_w233_results", "n1_@u_w@_results")   # protect pair-written upstream file refs
t = t.replace("PERPETUAL-N1-W233", "PERPETUAL-N1-W234")
t = t.replace("PERPETUAL_N1_W233", "PERPETUAL_N1_W234")
t = t.replace("n1_w233", "n1_w234")
t = t.replace("_w233bmc", "_w234bmc")
t = t.replace("W233", "@U_W@")
t = t.replace("W232", "W233")
t = t.replace("n1_w232", "n1_w233")
t = t.replace("PERPETUAL_N1_W232", "PERPETUAL_N1_W233")
t = t.replace("_w232bmc", "_w233bmc")
t = t.replace("@u_w@", "w233")
t = t.replace("@U_W@", "W233")
t = t.replace("@L32@", "232")
t = t.replace("@T32@", "33")

# ---- stale-token checklist (must all be ZERO) ----
STALE = ["527_404..529_403", "527_204..529_203", "527_204..527_403",
         "527404", "529404", "527_404+j", "529_404+j", "第 231 枚", "NINETY-THIRD", "第九十三例", "第六十三枚",
         "222 注册在册", "bmc_ordinal=63", "r972 freeze 窗", "0.3063", "\u2212" + "0.09274288",
         "\u2212" + "0.10490950", "0.24508296", "1530-bmc", "dd38a9da8",
         "15:2x（W232 面完整性", "15:2x finalize one-pass】", "r968 窗 15:2x", "二百三十行",
         "共二百三十面", "机证 230 行", "第 223 波",
         "n_eff_held_equal 931,989", "line_pre_w232 1.1922", "=**510,520 投影**", "engine_owner==bm-c 62 行",
         "prose 63rd", "r968 freeze receipt 62nd", "第 63 枚 EXACT", "pre-W233 宇宙",
         "W234 freezer 承接面", "r968 W232 §7 范式", "r968 W232 §8 范式", "r968/W232 先例",
         "W233 B 带 529_404..529_603 注册后将拒 naive W234 A 窗",
         "（527_403+1）", "（529_403+1）", "波号 233=", "A base=527404", "B base=529404", "n1_w233/ 分片计数增长",
         'batch_name="PERPETUAL-N1-W233"', "line_merged@K508,320",
         "实差 0.0122 在带内", "parity 91 行",
         "W136..W232 先例链披露", "W5..W232 先例", "v2..W232 落地", "W2..W232 落地 runner",
         "W2..W232 带（冻结时点", "W2..W232 全注册在冻结时点成立", "W1..W232 N1 finalize 已全部落地",
         "W1..W232 已落账", "（W1..W232 全落）", "508,320+2,200", "K=508,320 合并池",
         "净账本锚头 934,189", "净账本锚头 **934,189**", "splice e58dbcda3", "W232 **0.000344**】",
         "verify at W234 prereg", "r972 窗", "2026-10-13 18:4x"]
# NOTE: "529_404..531_403" / "529_604..529_803" are NOT stale in the W234
# face -- they are the fresh A/B arithmetic-continuation faces (SUB[7]/SUB[8]
# /SUB[24]/SUB[25] write them); the §5.5 projection instances were consumed
# by pair 38. Same digits, different semantics (probed live 20:5x).
# "529_404..529_603" is NOT stale -- it is the fresh upstream refusing band
# (>=2 asserted below). "n1_w233_results.json" file refs stay (upstream
# legs) while "n1_w233/ 分片计数增长" IS stale (self shard face now n1_w234).
# "529404" IS stale here but listed bare-digit-gated: the fresh B seed base
# is 531604; W233's 529404 appears only inside band-range strings with
# underscores (different token face).
for s in STALE:
    c = t.count(s)
    if c:
        import re as _re2
        for m in _re2.finditer(_re2.escape(s), t):
            print(f"--- STALE[{s}] ctx ---")
            print(t[max(0, m.start()-160):m.end()+80].replace("\n", " | "))
    assert c == 0, f"STALE token survives x{c}: {s}"

# ---- new-face presence checks ----
NEW = ["PERPETUAL-N1-W234", "第 232 枚", "529_604..531_603", "531_604..531_803",
       "NINETY-FOURTH", "第九十四例", "第九十五例", "第六十四枚",
       "936,389", "510,520", "512,720", "934,189", "508,320", "931,989",
       "MSG-20261013-1955-bmc", "260217d39",
       "bmc_ordinal=64", "n1_w234_results.json", "n1_w233_results.json", "0.3027", "\u2212" + "0.09276956",
       "\u2212" + "0.09893318", "0.24506207", "n_eff_held_equal 934,189", "0.000343",
       "1.1924", "第 224 波", "531_604..533_603", "531_804..532_003",
       "529_404..531_403", "529_604..529_803",
       "0.0062", "48c321706", "842f817ad", "2ae8553e6", "24e12fa5e", "aee0bd9fa", "e58dbcda3", "0ca920362", "第 64 枚 EXACT", "W235 freezer 承接面",
       "r974 W233 §7 范式", "K-lift **−0.0002**", "实差 0.0062 在带内",
       "parity 92 行", "二百三十一行", "共二百三十一面", "机证 231 行",
       "r976 freeze 窗", "prose 64th", "63rd owned 承袭",
       "19:5x（W233 面完整性", "19:5x finalize one-pass】", "verify at W235 prereg",
       "r973/W233 先例", "（529_603+1）", "（531_603+1）", "r976 窗实跑", "r974 窗 19:5x",
       "engine_owner==bm-c 63 行"]
for s in NEW:
    assert t.count(s) >= 1, f"NEW token missing: {s}"
# in-band sanity: own A band appears as the ADMIT face (>=4), own B band too
assert t.count("529_604..531_603") >= 4 and t.count("531_604..531_803") >= 4
# upstream W233 refusing band appears in A-face prose (band-facts + §3A)
assert t.count("529_404..529_603") >= 2
# chain-history legs present exactly once each (heritage restored verbatim)
assert t.count("+W213=bm-c r908 五面冻结（a24069f4c）") == 1
assert t.count("+W214=bm-c r910 五面冻结（4664900c8）") == 1
assert t.count("+W215=bm-c r912 五面冻结（1e71c3b93）") == 1
assert t.count("+W216=bm-c r914 五面冻结（0b3c489f0）") == 1
assert t.count("+W217=bm-c r916 五面冻结（ad011fee2）") == 1
assert t.count("+W218=bm-c r918 五面冻结（9afb0b1d7）") == 1
assert t.count("+W219=bm-c r920 五面冻结（0dae35332）") == 1
assert t.count("+W220=bm-c r923 五面冻结（a9aee1d05）") == 1
assert t.count("+W221=bm-c r928 五面冻结（98da27a40）") == 1
assert t.count("+W222=bm-c r931 死窗五面冻结") == 1
assert t.count("+W223=bm-c r934 五面冻结（448c4d8c2）") == 1
assert t.count("+W224=bm-c r937 死窗五面冻结") == 1
assert t.count("+W225=bm-c r939 五面冻结（84ecb3a3a）") == 1
assert t.count("+W226=bm-c r943 死窗五面冻结") == 1
assert t.count("+W227=bm-c r956 五面冻结（48c321706）") == 1
assert t.count("+W228=bm-c r959 死窗五面冻结") == 1
assert t.count("+W229=bm-c r961 死窗五面冻结") == 1
assert t.count("+W230=bm-c r963 死窗五面冻结") == 1
assert t.count("+W231=bm-c r966 五面冻结（aee0bd9fa）") == 1
assert t.count("+W232=bm-c r968 死窗五面冻结 estate 落盘·r968 absorb 提交（e58dbcda3）") == 1
assert t.count("+W233=bm-c r973 死窗五面冻结（0ca920362）") == 1
assert t.count("n1_w213_results.json·04:2x") == 1
assert t.count("n1_w214_results.json·05:2x") == 1
assert t.count("n1_w215_results.json·06:1x") == 1
assert t.count("n1_w216_results.json·06:5x") == 1
assert t.count("n1_w217_results.json·08:1x") == 1
assert t.count("n1_w218_results.json·09:1x") == 1
assert t.count("n1_w219_results.json·10:1x") == 1
assert t.count("n1_w220_results.json·12:0x") == 1
assert t.count("n1_w221_results.json·14:1x") == 1
assert t.count("n1_w222_results.json·15:5x") == 1
assert t.count("n1_w223_results.json·17:2x") == 1
assert t.count("n1_w224_results.json·19:1x") == 1
assert t.count("n1_w225_results.json·20:2x") == 1
assert t.count("n1_w226_results.json·22:4x") == 1
assert t.count("n1_w227_results.json·06:5x") == 1
assert t.count("n1_w228_results.json·08:3x") == 1
assert t.count("n1_w229_results.json·10:1x") == 1
assert t.count("n1_w230_results.json·11:5x") == 1
assert t.count("n1_w231_results.json·13:2x") == 1

import re as _re
for _tok in ["n1_w232_results.json·15:2x", "n1_w233_results.json·15:2x",
             "n1_w2@L32@_results.json", "n1_w231_results.json·13:2x",
             "n1_w233_results.json·19:5x", "@L32@", "n1_@u_w@_results"]:
    _c = t.count(_tok)
    print(f"DBG[{_tok}] x{_c}")
    for _m in list(_re.finditer(_re.escape(_tok), t))[:3]:
        print("   ctx:", t[max(0, _m.start()-80):_m.end()+40].replace("\n", " | "))
sys.exit(0)

assert t.count("n1_w233_results.json·19:5x") == 1
# healed RAM list + estate note + se_mu chain present
assert t.count("W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225/W226/W227/W228/W229/W230/W231/W232/W233 低 RAM 实烧先例") == 1
assert t.count("（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W232+W233）") == 1
assert t.count("按 _w233bmc_freeze_edits.py 模板派生") == 1
assert t.count("→W213 0.000359→W214 0.000358→W215 0.000357→W216 0.000356→W217 **0.000355**→W218 **0.000355**→W219 **0.000354**→W220 **0.000353**→W221 **0.000352**→W222 **0.000351**→W223 **0.000351**→W224 **0.00035**→W225 **0.000349**→W226 **0.000348**→W227 **0.000348**→W228 **0.000347**→W229 **0.000346**→W230 **0.000345**→W231 **0.000344**→W232 **0.000344**→W233 **0.000343**】") == 1

out = r"research\PERPETUAL_N1_W234_PREREG.md"
open(out, "wb").write(t.encode("utf-8"))
print("W234 prereg derived OK:", out)
print("bytes:", len(t.encode("utf-8")), "| sha16:", hashlib.sha256(t.encode("utf-8")).hexdigest()[:16])
print("W233(upper) refs (upstream, expected 40+):", t.count("W233"), "| W234 self:", t.count("W234"))
print("W232 heritage refs (chain legs + estate face):", t.count("W232"))
