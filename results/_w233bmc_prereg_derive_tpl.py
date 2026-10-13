# -*- coding: utf-8 -*-
# W233 per-wave prereg derivation (bm-c r972 freeze-prep, 2026-10-13 17:5x).
# Method: machine transform of the freeze-time W232 prereg blob
# (git show a3a7aa632:research/PERPETUAL_N1_W232_PREREG.md -- the exact
# pre-backfill commit face; the sec.7/8 machine-read backfill landed later in
# 59856ff28) with an explicit ordered replacement table.
# Pair old-sides are REPLAYED AT RUNTIME from the committed lineage chain
# (results/_w216bmc_prereg_derive.py PAIRS literal + _w217 SUB + _w218 SUB +
# _w219 SUB + _w220 SUB + _w221 SUB + _w222 SUB + _w223 SUB + _w224 SUB +
# _w225 SUB + _w226 SUB + _w227 SUB + _w228 SUB + _w229 SUB + _w230 SUB + _w231 SUB + _w232 SUB literals --
# SEVENTEEN-LEVEL replay chain, one deeper than the W232 sixteen-level chain;
# the W220 editor_gen same-window fix (r923 absorb freeze-window label) and
# the r927 pre-burn prose fixes (ledger 907,589->907,789 + own-block estate
# legs W220/W219+220) are replayed as corrective steps anchored to the
# committed blobs; placeholders materialized per level) -- zero transcription;
# every replayed block is assert-verified count==1 in the freeze-time blob
# BEFORE any pair application (r787 preflight law). Find sides of the own SUB
# table are machine-generated from the committed _w232 SUB new-sides by
# results/_w233bmc_subgen.py (m30 materialization; zero transcription).
# Bands/facts machine-derived from the committed ADMIT receipt
# results/_w233bmc_20261013_probe_receipt.json + n1_w232_results.json +
# _w232bmc_freeze_receipt.json -- never transcribed by eye (r587).
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
t = blob("a3a7aa632", "research/PERPETUAL_N1_W232_PREREG.md")    # base: freeze-time W232 face
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
RAM_FACE_232 = ram_face(t)
WIN_LABEL_REPLAY = win_label(t225)
WIN_LABEL_226 = win_label(t226)
WIN_LABEL_227 = win_label(t227)
WIN_LABEL_228 = win_label(t228)
WIN_LABEL_229 = win_label(t229)
WIN_LABEL_230 = win_label(t230)
WIN_LABEL_231 = win_label(t231)
WIN_LABEL_232 = win_label(t)
print(f"RAM anchors: W219-face {RAM_REPLAY_219!r} | W220-face {RAM_FACE_220!r} | W221-face {RAM_FACE_221!r} | W222-face {RAM_FACE_222!r} | W223-face {RAM_FACE_223!r} | W224-face {RAM_FACE_224!r} | W225-face {RAM_FACE_225!r} | W226-face {RAM_FACE_226!r} | W227-face {RAM_FACE_227!r} | W228-face {RAM_FACE_228!r} | W229-face {RAM_FACE_229!r} | W230-face {RAM_FACE_230!r} | W231-face {RAM_FACE_231!r} | W232-face {RAM_FACE_232!r} | WIN_LABEL_REPLAY {WIN_LABEL_REPLAY!r} | WIN_LABEL_226 {WIN_LABEL_226!r} | WIN_LABEL_227 {WIN_LABEL_227!r} | WIN_LABEL_228 {WIN_LABEL_228!r} | WIN_LABEL_229 {WIN_LABEL_229!r} | WIN_LABEL_230 {WIN_LABEL_230!r} | WIN_LABEL_231 {WIN_LABEL_231!r} | WIN_LABEL_232 {WIN_LABEL_232!r}")

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

# preflight: every replayed W232-face block sits exactly once in the blob
for i, old in enumerate(OLD32):
    c = t.count(old)
    assert c == 1, f"preflight block[{i}] count {c} != 1 in freeze-time W232 blob"
print("preflight OK: 46/46 replayed blocks sit count==1 in the freeze-time W232 blob")

# ---------- machine-derived anchors (never hand-copied) ----------
rec = json.load(open(r"results\_w233bmc_20261013_probe_receipt.json", encoding="utf-8"))
assert rec["verdict"] == "ADMIT" and rec["bands"] == {"A": "527404_529403", "B": "529404_529603"}
w232 = json.load(open(r"results\perpetual_faces\n1_w232_results.json", encoding="utf-8"))
led = w232["science_gates"]["ledger"]
assert led["total"] == 934189 and led["prev_total"] == 931989 and led["batch_trials"] == 2200
merged = w232["null_pool_cumulative"]["merged"]
assert merged["n_values"] == 508320
w232only = w232["null_pool_cumulative"]["w232_only"]
A_p95 = w232["families"]["A_random_engine_exit"]["full_sharpe_p95"]
kl = w232["skill_line_v2_k_lift"]
assert kl["line_delta_k_lift"] == 0.0001 and kl["n_eff_held_equal"] == 931989
assert kl["line_pre_w232"] == 1.1922 and kl["line_merged_508320"] == 1.1923
se_mu = w232["null_pool_cumulative"]["se_mu_at_k508320"]
assert se_mu == 0.000344
leg1, leg4 = rec["legs"]["leg1"], rec["legs"]["leg4"]
assert leg1["A"] == [527404, 529403] and leg1["B"] == [529404, 529603]
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
assert leg1["ARITH_A"] == [527204, 529203] and leg1["B_naive_first_clean"] == [527404, 527603]
assert leg4["W233p_A"] == "529404..531403" and leg4["W233p_B"] == "529604..529803"
assert leg4["W233p_B_lands_inside_W233p_A"] is True
leg0 = rec["legs"]["leg0"]
assert leg0["rows"] == 230 and leg0["owner_rows"] == 222 and leg0["bmc_rows"] == 62 \
       and leg0["bmc_ordinal"] == 63 and leg0["ordinal"] == 223
assert "attempt-continuity" in leg0["bmc_ordinal_note"] and "62nd owned" in leg0["bmc_ordinal_note"]
fr = json.load(open(r"results\_w232bmc_freeze_receipt.json", encoding="utf-8"))
assert fr["ordinal_faces"]["bmc_own_ordinal"] == 62  # "62nd owned 承袭" prose anchor
# formatted-string guards: every literal below that carries a machine value
# is assert-verified against the live JSON here (zero eyeball)
def fmt8(x):
    return ("\u2212" if x < 0 else "") + f"{abs(x):.8f}"
assert fmt8(merged["mu"]) == "\u2212" + "0.09274288", fmt8(merged["mu"])
assert fmt8(w232only["mu"]) == "\u2212" + "0.10490950", fmt8(w232only["mu"])
assert f"{merged['sigma']:.8f}" == "0.24508296", f"{merged['sigma']:.8f}"
assert f"{abs(w232only['mu'] - merged['mu']):.4f}" == "0.0122", f"{abs(w232only['mu'] - merged['mu']):.4f}"
assert f"{A_p95:.4f}" == "0.3063", f"{A_p95:.4f}"
assert f"{kl['line_merged_508320']:.4f}" == "1.1923"
assert f"{kl['line_delta_k_lift']:+.4f}" == "+0.0001"  # ASCII f-string face; prose token uses ASCII + sign (W232 face +0.0001)
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
# freeze-window label (live honesty): this derivation runs in r972, 2026-10-13
_now = datetime.datetime.now()
assert (_now.year, _now.month, _now.day) == (2026, 10, 13), f"unexpected clock: {_now}"
WIN_LABEL = f"2026-10-13 {_now.hour}:{_now.minute // 10}x·"
print(f"freeze-window label: r972 {WIN_LABEL}")

@@SUB_BLOCK@@

# ---------- build + apply W233 pairs ----------
PAIRS = []
for i, old in enumerate(OLD32):
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
# Pairs covered every W232 self face (each count==1 asserted). Remaining
# "W232" tokens = pair-written legit refs (chain W232 leg, refusing band,
# W232 finalize keys, W1..W232 scope) which must STAY W232 -- mask, then age
# one-wave-older W231 refs to W232, then restore. @L31@/@T31@ hold heritage
# tokens immune.
t = t.replace("n1_w232_results", "n1_@u_w@_results")   # protect pair-written upstream file refs
t = t.replace("PERPETUAL-N1-W232", "PERPETUAL-N1-W233")
t = t.replace("PERPETUAL_N1_W232", "PERPETUAL_N1_W233")
t = t.replace("n1_w232", "n1_w233")
t = t.replace("_w232bmc", "_w233bmc")
t = t.replace("W232", "@U_W@")
t = t.replace("W231", "W232")
t = t.replace("n1_w231", "n1_w232")
t = t.replace("PERPETUAL_N1_W231", "PERPETUAL_N1_W232")
t = t.replace("_w231bmc", "_w232bmc")
t = t.replace("@u_w@", "w232")
t = t.replace("@U_W@", "W232")
t = t.replace("@L31@", "231")
t = t.replace("@T31@", "32")

# ---- stale-token checklist (must all be ZERO) ----
STALE = ["525_204..527_203", "525_004..527_003", "525_004..525_203",
         "525204", "527204", "525_204+j", "527_204+j", "第 230 枚", "NINETY-SECOND", "第九十二例", "第六十二枚",
         "221 注册在册", "bmc_ordinal=62", "r967 freeze 窗", "0.3251", "\u2212" + "0.09268999",
         "\u2212" + "0.09203368", "0.24507072", "1345-bmc", "8d3a1b78a",
         "13:2x（W231 面完整性", "13:2x finalize one-pass】", "r966 窗 13:2x", "二百二十九",
         "共二百二十九面", "机证 229 行", "第 222 波",
         "n_eff_held_equal 929,789", "line_pre_w231 1.1921", "=**508,320 投影**", "engine_owner==bm-c 61 行",
         "prose 62nd", "r966 freeze receipt 61st", "第 62 枚 EXACT", "pre-W232 宇宙",
         "W233 freezer 承接面", "r966 W231 §7 范式", "r966 W231 §8 范式", "r966/W231 先例",
         "W232 B 带 527_204..527_403 注册后将拒 naive W233",
         "（525_203+1）", "（527_203+1）", "波号 232=", "A base=525204", "B base=527204", "n1_w232/ 分片计数增长",
         'batch_name="PERPETUAL-N1-W232"', "line_merged@K506,120",
         "实差 0.0007 在带内", "parity 90 行",
         "W136..W231 先例链披露", "W5..W231 先例", "v2..W231 落地", "W2..W231 落地 runner",
         "W2..W231 带（冻结时点", "W2..W231 全注册在冻结时点成立", "W1..W231 N1 finalize 已全部落地",
         "W1..W231 已落账", "（W1..W231 全落）", "506,120+2,200", "K=506,120 合并池",
         "净账本锚头 931,989", "净账本锚头 **931,989**", "splice aee0bd9fa", "W231 **0.000344**】",
         "verify at W233 prereg", "r966 窗", "2026-10-13 13:5x"]
# NOTE: "527_204..529_203" / "527_404..527_603" are NOT stale in the W233
# face -- they are the fresh A/B arithmetic-continuation faces (SUB[7]/SUB[8]
# /SUB[24]/SUB[25] write them); the §5.5 projection instances were consumed
# by pair 38. Same digits, different semantics (probed live 17:5x).
# "527_204..527_403" is NOT stale -- it is the fresh upstream refusing band
# (>=2 asserted below). "n1_w232_results.json" file refs stay (upstream
# legs) while "n1_w232/ 分片计数增长" IS stale (self shard face now n1_w233).
# "527204" IS stale here but listed bare-digit-gated: the fresh B seed base
# is 529404; W232's 527204 appears only inside band-range strings with
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
NEW = ["PERPETUAL-N1-W233", "第 231 枚", "527_404..529_403", "529_404..529_603",
       "NINETY-THIRD", "第九十三例", "第九十四例", "第六十三枚",
       "934,189", "508,320", "510,520", "931,989", "506,120", "929,789",
       "MSG-20261013-1530-bmc", "dd38a9da8",
       "bmc_ordinal=63", "n1_w233_results.json", "n1_w232_results.json", "0.3063", "\u2212" + "0.09274288",
       "\u2212" + "0.10490950", "0.24508296", "n_eff_held_equal 931,989", "0.000344",
       "1.1922", "第 223 波", "529_404..531_403", "529_604..529_803",
       "527_204..529_203", "527_404..527_603",
       "0.0122", "48c321706", "842f817ad", "2ae8553e6", "24e12fa5e", "aee0bd9fa", "e58dbcda3", "第 63 枚 EXACT", "W234 freezer 承接面",
       "r968 W232 §7 范式", "K-lift **+0.0001**", "实差 0.0122 在带内",
       "parity 91 行", "二百三十行", "共二百三十面", "机证 230 行",
       "r972 freeze 窗", "prose 63rd", "62nd owned 承袭",
       "15:2x（W232 面完整性", "15:2x finalize one-pass】", "verify at W234 prereg",
       "r968/W232 先例", "（527_403+1）", "（529_403+1）", "r972 窗实跑", "r968 窗 15:2x",
       "engine_owner==bm-c 62 行"]
for s in NEW:
    assert t.count(s) >= 1, f"NEW token missing: {s}"
# in-band sanity: own A band appears as the ADMIT face (>=4), own B band too
assert t.count("527_404..529_403") >= 4 and t.count("529_404..529_603") >= 4
# upstream W232 refusing band appears in A-face prose (band-facts + §3A)
assert t.count("527_204..527_403") >= 2
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
assert t.count("n1_w232_results.json·15:2x") == 1
# healed RAM list + estate note + se_mu chain present
assert t.count("W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225/W226/W227/W228/W229/W230/W231/W232 低 RAM 实烧先例") == 1
assert t.count("（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W232）") == 1
assert t.count("按 _w232bmc_freeze_edits.py 模板派生") == 1
assert t.count("→W213 0.000359→W214 0.000358→W215 0.000357→W216 0.000356→W217 **0.000355**→W218 **0.000355**→W219 **0.000354**→W220 **0.000353**→W221 **0.000352**→W222 **0.000351**→W223 **0.000351**→W224 **0.00035**→W225 **0.000349**→W226 **0.000348**→W227 **0.000348**→W228 **0.000347**→W229 **0.000346**→W230 **0.000345**→W231 **0.000344**→W232 **0.000344**】") == 1

out = r"research\PERPETUAL_N1_W233_PREREG.md"
open(out, "wb").write(t.encode("utf-8"))
print("W233 prereg derived OK:", out)
print("bytes:", len(t.encode("utf-8")), "| sha16:", hashlib.sha256(t.encode("utf-8")).hexdigest()[:16])
print("W232(upper) refs (upstream, expected 40+):", t.count("W232"), "| W233 self:", t.count("W233"))
print("W231 heritage refs (chain legs + estate face):", t.count("W231"))
