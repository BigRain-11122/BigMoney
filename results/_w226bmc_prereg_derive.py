# -*- coding: utf-8 -*-
# W226 per-wave prereg derivation (bm-c r941 freeze-prep, 2026-10-12 21:0x).
# Method: machine transform of the freeze-time W225 prereg blob
# (git show 4b22941a7:research/PERPETUAL_N1_W225_PREREG.md -- the exact
# pre-backfill commit face; the sec.7/8 machine-read backfill landed later in
# 8b12ace73) with an explicit ordered replacement table.
# Pair old-sides are REPLAYED AT RUNTIME from the committed lineage chain
# (results/_w216bmc_prereg_derive.py PAIRS literal + _w217 SUB + _w218 SUB +
# _w219 SUB + _w220 SUB + _w221 SUB + _w222 SUB + _w223 SUB + _w224 SUB +
# _w225 SUB literals -- TEN-LEVEL replay chain, one deeper than the W225
# nine-level chain; the W220 editor_gen same-window fix (r923 absorb
# freeze-window label) and the r927 pre-burn prose fixes (ledger
# 907,589->907,789 + own-block estate legs W220/W219+220) are replayed as
# corrective steps anchored to the committed blobs; placeholders materialized
# per level) -- zero transcription; every replayed block is assert-verified
# count==1 in the freeze-time blob BEFORE any pair application (r787
# preflight law).
# Bands/facts machine-derived from the committed ADMIT receipt
# results/_w226bmc_20261012_probe_receipt.json + n1_w225_results.json +
# _w225bmc_freeze_receipt.json -- never transcribed by eye (r587).
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
t = blob("4b22941a7", "research/PERPETUAL_N1_W225_PREREG.md")    # base: freeze-time W225 face
assert "## §7" in t and "占位" in t, "not the freeze-time (pre-backfill) face"

def ram_face(txt):
    m = re.search(r"本窗 free RAM ~(\d+\.\d)GB", txt)
    assert m, "RAM note face not found"
    return "~" + m.group(1)

RAM_REPLAY_219 = ram_face(t219)
RAM_FACE_220 = ram_face(t220)
RAM_FACE_221 = ram_face(t221)
RAM_FACE_222 = ram_face(t222)
RAM_FACE_223 = ram_face(t223)
RAM_FACE_224 = ram_face(t224)
RAM_FACE_225 = ram_face(t)
m_wl = re.search(r"freeze 窗·(2026-10-12 \d+:\d)x·", t)
assert m_wl, "W225 freeze-window label face not found"
WIN_LABEL_REPLAY = m_wl.group(1) + "x·"
print(f"RAM anchors: W219-face {RAM_REPLAY_219!r} | W220-face {RAM_FACE_220!r} | W221-face {RAM_FACE_221!r} | W222-face {RAM_FACE_222!r} | W223-face {RAM_FACE_223!r} | W224-face {RAM_FACE_224!r} | W225-face {RAM_FACE_225!r} | WIN_LABEL_REPLAY {WIN_LABEL_REPLAY!r}")

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

# preflight: every replayed W225-face block sits exactly once in the blob
for i, old in enumerate(OLD25):
    c = t.count(old)
    assert c == 1, f"preflight block[{i}] count {c} != 1 in freeze-time W225 blob"
print("preflight OK: 46/46 replayed blocks sit count==1 in the freeze-time W225 blob")

# ---------- machine-derived anchors (never hand-copied) ----------
rec = json.load(open(r"results\_w226bmc_20261012_probe_receipt.json", encoding="utf-8"))
assert rec["verdict"] == "ADMIT" and rec["bands"] == {"A": "512004_514003", "B": "514004_514203"}
w225 = json.load(open(r"results\perpetual_faces\n1_w225_results.json", encoding="utf-8"))
led = w225["science_gates"]["ledger"]
assert led["total"] == 918789 and led["prev_total"] == 916589 and led["batch_trials"] == 2200
merged = w225["null_pool_cumulative"]["merged"]
assert merged["n_values"] == 492920
w225only = w225["null_pool_cumulative"]["w225_only"]
A_p95 = w225["families"]["A_random_engine_exit"]["full_sharpe_p95"]
kl = w225["skill_line_v2_k_lift"]
assert kl["line_delta_k_lift"] == -0.0001 and kl["n_eff_held_equal"] == 916589
assert kl["line_pre_w225"] == 1.1915 and kl["line_merged_492920"] == 1.1914
se_mu = w225["null_pool_cumulative"]["se_mu_at_k492920"]
assert se_mu == 0.000349
leg1, leg4 = rec["legs"]["leg1"], rec["legs"]["leg4"]
assert leg1["A"] == [512004, 514003] and leg1["B"] == [514004, 514203]
assert leg1["ARITH_A"] == [511804, 513803] and leg1["B_naive_first_clean"] == [512004, 512203]
assert leg4["W226p_A"] == "514004..516003" and leg4["W226p_B"] == "514204..514403"
assert leg4["W226p_B_lands_inside_W226p_A"] is True
leg0 = rec["legs"]["leg0"]
assert leg0["rows"] == 223 and leg0["owner_rows"] == 215 and leg0["bmc_rows"] == 55 \
       and leg0["bmc_ordinal"] == 56 and leg0["ordinal"] == 216
assert "attempt-continuity" in leg0["bmc_ordinal_note"] and "55th owned" in leg0["bmc_ordinal_note"]
fr = json.load(open(r"results\_w225bmc_freeze_receipt.json", encoding="utf-8"))
assert fr["ordinal_faces"]["bmc_own_ordinal"] == 55  # "55th owned 承袭" prose anchor
# formatted-string guards: every literal below that carries a machine value
# is assert-verified against the live JSON here (zero eyeball)
def fmt8(x):
    return ("−" if x < 0 else "") + f"{abs(x):.8f}"
assert fmt8(merged["mu"]) == "−0.09279454", fmt8(merged["mu"])
assert fmt8(w225only["mu"]) == "−0.09782473", fmt8(w225only["mu"])
assert f"{merged['sigma']:.8f}" == "0.24508719", f"{merged['sigma']:.8f}"
assert f"{abs(w225only['mu'] - merged['mu']):.4f}" == "0.0050", f"{abs(w225only['mu'] - merged['mu']):.4f}"
assert f"{A_p95:.4f}" == "0.3014", f"{A_p95:.4f}"
assert f"{kl['line_merged_492920']:.4f}" == "1.1914"
assert f"{kl['line_delta_k_lift']:+.4f}" == "-0.0001"  # ASCII f-string face; prose token uses U+2212
# free RAM live read (honesty for the RAM note). Band kept wide at the low
# end: resident chassis load (ComfyUI + MV lane) keeps the box near the
# floor -- honest face, engine RAM gate governs burn admission separately.
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
# freeze-window label (live honesty): this derivation runs in r941, 2026-10-12
_now = datetime.datetime.now()
assert (_now.year, _now.month, _now.day) == (2026, 10, 12), f"unexpected clock: {_now}"
WIN_LABEL = f"2026-10-12 {_now.hour}:{_now.minute // 10}x·"
print(f"freeze-window label: r941 {WIN_LABEL}")

# ---------- per-pair submaps: index -> ordered (find, replace) ----------
SUB = {
 0: [("PERPETUAL-N1-W225 预注册 · N1 nulls-deepening 泵第 223 枚","PERPETUAL-N1-W226 预注册 · N1 nulls-deepening 泵第 224 枚"),
     ("engine_owner 行 214 注册在册（表尾 W224 行·probe leg0 机证 222 行","engine_owner 行 215 注册在册（表尾 W225 行·probe leg0 机证 223 行"),
     ("本候选=bm-c 第五十五枚自有波【live-derive face：席面 prose 55th=seat-time face（r938 窗 W224 注册后 attempt-continuity live derive·r937 freeze receipt 54th owned 承袭）→freeze 时 live derive bm-c rows 54+候选=第 55 枚 EXACT","本候选=bm-c 第五十六枚自有波【live-derive face：席面 prose 56th=seat-time face（r940 窗 W225 注册后 attempt-continuity live derive·r939 freeze receipt 55th owned 承袭）→freeze 时 live derive bm-c rows 55+候选=第 56 枚 EXACT"),
     ("【bm-c 循环班 r939 freeze 窗·" + WIN_LABEL_REPLAY,"【bm-c 循环班 r941 freeze 窗·" + WIN_LABEL)],
 1: [("saturation_engine.py status live-read r939：","saturation_engine.py status live-read r941：")],
 2: [("**波号 225=注册表 W224 席后首个自由号**","**波号 226=注册表 W225 席后首个自由号**"),
     ("r938 窗实跑：origin inbox/processed/ 零 W225 席位外机命中","r940 窗实跑：origin inbox/processed/ 零 W226 席位外机命中"),
     ("origin perpetual_faces.py 零 225 行","origin perpetual_faces.py 零 226 行"),
     ("perpetual_faces_n1.py 零 PERPETUAL-N1-W225 WAVE_CONFIGS","perpetual_faces_n1.py 零 PERPETUAL-N1-W226 WAVE_CONFIGS"),
     ("origin 零 PERPETUAL_N1_W225_PREREG.md","origin 零 PERPETUAL_N1_W226_PREREG.md")],
 3: [("+W221=bm-c r928 五面冻结（98da27a40）+引擎自燃 12/12+r928 finalize one-pass 已落（K=484,120·账本头 909,989 机读·n1_w221_results.json·14:1x）+W222=bm-c r931 死窗五面冻结 estate 落盘·r932 absorb 提交（4167d791d）+引擎自燃 12/12+r932 finalize one-pass 已落（K=486,320·账本头 912,189 机读·n1_w222_results.json·15:5x）+W223=bm-c r934 五面冻结（448c4d8c2）+引擎自燃 12/12+r935 finalize one-pass 已落（K=488,520·账本头 914,389 机读·n1_w223_results.json·17:2x）+W224=bm-c r937 死窗五面冻结 estate 落盘·r937 absorb 提交（d307e3d1d）+引擎自燃 12/12+r937 finalize one-pass 已落（K=490,720·账本头 916,589 机读·n1_w224_results.json·19:1x）——本波上游链=W1..W224 finalize 全落地","+W221=bm-c r928 五面冻结（98da27a40）+引擎自燃 12/12+r928 finalize one-pass 已落（K=484,120·账本头 909,989 机读·n1_w221_results.json·14:1x）+W222=bm-c r931 死窗五面冻结 estate 落盘·r932 absorb 提交（4167d791d）+引擎自燃 12/12+r932 finalize one-pass 已落（K=486,320·账本头 912,189 机读·n1_w222_results.json·15:5x）+W223=bm-c r934 五面冻结（448c4d8c2）+引擎自燃 12/12+r935 finalize one-pass 已落（K=488,520·账本头 914,389 机读·n1_w223_results.json·17:2x）+W@L24@=bm-c r937 死窗五面冻结 estate 落盘·r937 absorb 提交（d307e3d1d）+引擎自燃 12/12+r937 finalize one-pass 已落（K=490,720·账本头 916,589 机读·n1_w@L24@_results.json·19:1x）+W225=bm-c r939 五面冻结（84ecb3a3a）+引擎自燃 12/12+r940 finalize one-pass 已落（K=492,920·账本头 918,789 机读·n1_w225_results.json·20:2x）——本波上游链=W1..W225 finalize 全落地")],
 4: [("本机席位公示=MSG-20261012-1943-bmc-w225-seat 已推 origin c78dd1a44 先于本冻结【r565 律·席位先行·r938 窗】；下游 W226+ 投影见 §5.5（probe 机证 leg4·W226 freezer 承接面）】。","本机席位公示=MSG-20261012-2040-bmc-w226-seat 已推 origin d7d270752 先于本冻结【r565 律·席位先行·r940 窗】；下游 W227+ 投影见 §5.5（probe 机证 leg4·W227 freezer 承接面）】。")],
 5: [("W2..W224 全注册在冻结时点成立","W2..W225 全注册在冻结时点成立")],
 6: [("ADMIT 回执=results/_w225bmc_20261012_probe_receipt.json","ADMIT 回执=results/_w226bmc_20261012_probe_receipt.json")],
 7: [("本波 **A-ext seed=509_804..511_803**","本波 **A-ext seed=512_004..514_003**"),
     ("**A 面=FIRST-CLEAN past prior-wave B 阶梯第八十五例**","**A 面=FIRST-CLEAN past prior-wave B 阶梯第八十六例**"),
     ("A 面算术继续带 509_604..511_603（自注册 W224 A 尾 511_603 续）在其起点即被 W224 注册 B 带 509_604..509_803 **拒**（W224 席位 leg4 投影+其 probe 所预言+强制）→ 诚实前向走 **1 hop** 落 **509_804..511_803**","A 面算术继续带 511_804..513_803（自注册 W225 A 尾 511_803 续）在其起点即被 W225 注册 B 带 511_804..512_003 **拒**（W225 席位 leg4 投影+其 probe 所预言+强制）→ 诚实前向走 **1 hop** 落 **512_004..514_003**"),
     ("**A base==前波 B 尾+1（509_803+1）机检关系**","**A base==前波 B 尾+1（512_003+1）机检关系**"),
     ("=**A-hops-prior-B 阶梯几何第八十五例（E36 卡）**","=**A-hops-prior-B 阶梯几何第八十六例（E36 卡）**"),
     ("A_semantics 机读序数=EIGHTY-FIFTH（第八十五例）","A_semantics 机读序数=EIGHTY-SIXTH（第八十六例）")],
 8: [("**B-ext exit seed=511_804..512_003**","**B-ext exit seed=514_004..514_203**"),
     ("B 面 naive first-clean 继续带 509_804..510_003 在注册宇宙上 CLEAN 但**落在本波 A 窗 509_804..511_803 内**","B 面 naive first-clean 继续带 512_004..512_203 在注册宇宙上 CLEAN 但**落在本波 A 窗 512_004..514_003 内**"),
     ("→ B 带本波 A 窗保留走 **1 hop** 落 **511_804..512_003**","→ B 带本波 A 窗保留走 **1 hop** 落 **514_004..514_203**"),
     ("**B base==本波 A 尾+1（511_803+1）机检关系**","**B base==本波 A 尾+1（514_003+1）机检关系**"),
     ("**W224 席位 leg4 投影承接面注记兑现**：投影预言 W225 须在 post-W224 注册宇宙重 derive 且 derive B 时预留本波 A 窗","**W225 席位 leg4 投影承接面注记兑现**：投影预言 W226 须在 post-W225 注册宇宙重 derive 且 derive B 时预留本波 A 窗")],
 9: [("R250：W225 带从未指派","R250：W226 带从未指派")],
 10: [("A base=509804 span=2000 checked=2000 verdict=FREE / B base=511804 span=200 checked=200 verdict=FREE","A base=512004 span=2000 checked=2000 verdict=FREE / B base=514004 span=200 checked=200 verdict=FREE")],
 11: [("扫描面=pre-W225 全二百二十二行注册 N1 带表（表尾 W224 行·probe leg0 机证 222 行 live 单态 owner rows 214）","扫描面=pre-W226 全二百二十三行注册 N1 带表（表尾 W225 行·probe leg0 机证 223 行 live 单态 owner rows 215）")],
 12: [("`scripts/perpetual_faces_n1.py`（W2..W224 落地 runner 的 wave 参数化复用","`scripts/perpetual_faces_n1.py`（W2..W225 落地 runner 的 wave 参数化复用")],
 13: [("selftest W225 face 将随五面冻结落地验证","selftest W226 face 将随五面冻结落地验证")],
 14: [("本件与 results/_w225bmc_freeze_edits.py","本件与 results/_w226bmc_freeze_edits.py"),
     ("按 _w224bmc_freeze_edits.py 模板派生","按 _w2@T24@bmc_freeze_edits.py 模板派生"),
     ("gate0.5 自查 W224 行+W224 finalize 件在场","gate0.5 自查 W225 行+W225 finalize 件在场"),
     ("estate 提取面=本机 W224 块物理字节","estate 提取面=本机 W225 块物理字节"),
     ("（r937/W224 先例 freeze-prep 同式","（r939/W225 先例 freeze-prep 同式")],
 15: [("- 批名=**PERPETUAL-N1-W225**。","- 批名=**PERPETUAL-N1-W226**。")],
 16: [("**W1..W224 N1 finalize 已全部落地**【净账本锚头 **916,589**·K=490,720 合并池·n1_w224_results.json 机读·W224 finalize one-pass bm-c r937 absorb 窗 19:1x（W224 面完整性=12/12 shards consumed+finalize audit finalize_only=true 收口·r937 splice d307e3d1d+引擎自燃链如实注记）】","**W1..W225 N1 finalize 已全部落地**【净账本锚头 **918,789**·K=492,920 合并池·n1_w225_results.json 机读·W225 finalize one-pass bm-c r940 窗 20:2x（W225 面完整性=12/12 shards consumed+finalize audit finalize_only=true 收口·r939 splice 84ecb3a3a+引擎自燃链如实注记）】")],
 17: [("累计 null 池=490,720+2,200（本波）=**492,920 投影**","累计 null 池=492,920+2,200（本波）=**495,120 投影**")],
 18: [("（本机席位公示 MSG-20261012-1943-bmc-w225-seat 已推 origin c78dd1a44 r565 律·probe W226+ 投影 A 511_804..513_803 / B 512_004..512_203","（本机席位公示 MSG-20261012-2040-bmc-w226-seat 已推 origin d7d270752 r565 律·probe W227+ 投影 A 514_004..516_003 / B 514_204..514_403"),
     ("投影 B 落投影 A 窗内·W225 B 带 511_804..512_003 注册后将拒 naive W226 A 窗=阶梯 A-hops-prior-B 第八十六例——**W226 freezer 承接面强制注记：须在 post-W225 宇宙重 derive 且 derive B 时预留本波 A 窗","投影 B 落投影 A 窗内·W226 B 带 514_004..514_203 注册后将拒 naive W227 A 窗=阶梯 A-hops-prior-B 第八十七例——**W227 freezer 承接面强制注记：须在 post-W226 宇宙重 derive 且 derive B 时预留本波 A 窗")],
 19: [("T-2026-10-01-141 s1 引擎线第 215 波【bm-c 第五十五枚自有波【机面 derive：probe leg0 bmc_ordinal=55 attempt-continuity face（r938 窗计法·W224 splice/freeze receipt=54th owned 承袭注记）——freeze 时 live derive bm-c rows 54+候选=第 55 枚 EXACT","T-2026-10-01-141 s1 引擎线第 216 波【bm-c 第五十六枚自有波【机面 derive：probe leg0 bmc_ordinal=56 attempt-continuity face（r940 窗计法·W225 splice/freeze receipt=55th owned 承袭注记）——freeze 时 live derive bm-c rows 55+候选=第 56 枚 EXACT"),
     ("波号=注册表 W224 席后首个自由号·单态零席位空档于冻结时点成立；中位公示 MSG-20261012-1943-bmc-w225-seat 先推 origin c78dd1a44 r565 律","波号=注册表 W225 席后首个自由号·单态零席位空档于冻结时点成立；中位公示 MSG-20261012-2040-bmc-w226-seat 先推 origin d7d270752 r565 律")],
 20: [("本窗 free RAM " + RAM_FACE_225 + "GB","本窗 free RAM " + RAM_GB + "GB"),
     ("W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224 低 RAM 实烧先例","W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W@L24@/W225 低 RAM 实烧先例")],
 21: [("复读自见 W225 行并点火自烧","复读自见 W226 行并点火自烧")],
 22: [("--prereg research/PERPETUAL_N1_W225_PREREG.md","--prereg research/PERPETUAL_N1_W226_PREREG.md")],
 23: [("（p2_calibration v1/v2 canon；v1 ext；v2..W224 落地）","（p2_calibration v1/v2 canon；v1 ext；v2..W225 落地）")],
 24: [("entry rng seed=**509_804+j**","entry rng seed=**512_004+j**"),
     ("法典 §4 W225 行 A=509_804..511_803","法典 §4 W226 行 A=512_004..514_003"),
     ("**FIRST-CLEAN past prior-wave B 阶梯第八十五例**：算术续带 509_604..511_603 起点即被 W224 注册 B 带 509_604..509_803 拒→1 hop 落 509_804..511_803","**FIRST-CLEAN past prior-wave B 阶梯第八十六例**：算术续带 511_804..513_803 起点即被 W225 注册 B 带 511_804..512_003 拒→1 hop 落 512_004..514_003")],
 25: [("entry rng=**509_804+j**","entry rng=**512_004+j**"),
     ("exit rng=**511_804+j**","exit rng=**514_004+j**"),
     ("法典 §4 W225 行 B=511_804..512_003","法典 §4 W226 行 B=514_004..514_203"),
     ("B 算术续带 509_804..510_003 在注册宇宙上 CLEAN 但落在本波 A 窗 509_804..511_803 内","B 算术续带 512_004..512_203 在注册宇宙上 CLEAN 但落在本波 A 窗 512_004..514_003 内"),
     ("保留走落 511_804..512_003","保留走落 514_004..514_203"),
     ("与 W224 席位 leg4 投影承接面注记兑现收敛","与 W225 席位 leg4 投影承接面注记兑现收敛")],
 26: [("种子带 disjoint 全例（selftest 强制）：W225 带与 v1 在用带","种子带 disjoint 全例（selftest 强制）：W226 带与 v1 在用带")],
 27: [("W2..W224 带（冻结时点全注册单态）","W2..W225 带（冻结时点全注册单态）")],
 28: [("本波机验 ADMIT 回执在场=_w225bmc_20261012 探针窗","本波机验 ADMIT 回执在场=_w226bmc_20261012 探针窗")],
 29: [("selftest W225 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W224 行 parity 腿","selftest W226 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W225 行 parity 腿")],
 30: [("从**本机 W224 块物理字节**提取","从**本机 W225 块物理字节**提取"),
     ("——W223 块的 W222 leg（1 行）不入 estate 路径·提取后新增 W222+W223 leg 构成 W225 块 parity 83 行（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224）","——W@L24@ 块的 W223 leg（1 行）不入 estate 路径·提取后新增 W223+W@L24@ leg 构成 W226 块 parity 84 行（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W@L24@+W225）")],
 31: [("起草窗实流 W1..W224 已落账 490,720 实测","起草窗实流 W1..W225 已落账 492,920 实测")],
 32: [("batch_name=\"PERPETUAL-N1-W225\", batch_trials=2200, file_name=\"results/perpetual_faces/n1_w225_results.json\"","batch_name=\"PERPETUAL-N1-W226\", batch_trials=2200, file_name=\"results/perpetual_faces/n1_w226_results.json\"")],
 33: [("（起草窗实况注记：**W1..W224 N1 finalize 已全部落地**——净账本锚头 916,589·**K=490,720 合并池**·**零在飞上游席——本波 §5 预测键=**W224 实测值**【results/perpetual_faces/n1_w224_results.json·N1 面最新已落账键·19:1x finalize one-pass】。","（起草窗实况注记：**W1..W225 N1 finalize 已全部落地**——净账本锚头 918,789·**K=492,920 合并池**·**零在飞上游席——本波 §5 预测键=**W225 实测值**【results/perpetual_faces/n1_w225_results.json·N1 面最新已落账键·20:2x finalize one-pass】。")],
 34: [("1. W225-only mu 与累计池 merged mu（W224 实测键 **−0.09277199**·K=490,720 合并池·W224-only 实测 **−0.09231609**）差异 **|Δ|<0.02**（W2..W224 共二百二十二面实测 mu 稳定先例·单波跨键微；W224-only vs merged 实差 0.0005 在带内）。","1. W226-only mu 与累计池 merged mu（W225 实测键 **−0.09279454**·K=492,920 合并池·W225-only 实测 **−0.09782473**）差异 **|Δ|<0.02**（W2..W225 共二百二十三面实测 mu 稳定先例·单波跨键微；W225-only vs merged 实差 0.0050 在带内）。")],
 35: [("键 **0.24508442**=W224 合并池实测）。","键 **0.24508719**=W225 合并池实测）。")],
 36: [("3. A 档 full_sharpe_p95 与 W224 A 档 p95（**0.3168** 实测锚）差 **<0.05**（门标注法 W5..W224 先例","3. A 档 full_sharpe_p95 与 W225 A 档 p95（**0.3014** 实测锚）差 **<0.05**（门标注法 W5..W225 先例")],
 37: [("W136..W224 先例链披露","W136..W225 先例链披露"),
     ("键 W224 实测 K-lift **−0.0001**·line_merged@K490,720 **1.1913**·line_pre_w224 1.1914·n_eff_held_equal 914,389","键 W225 实测 K-lift **−0.0001**·line_merged@K492,920 **1.1914**·line_pre_w225 1.1915·n_eff_held_equal 916,589"),
     ("se_mu 收窄链 …→W209 0.000362→W211 0.000361→W212 0.000360→W213 0.000359→W214 0.000358→W215 0.000357→W216 0.000356→W217 **0.000355**→W218 **0.000355**→W219 **0.000354**→W220 **0.000353**→W221 **0.000352**→W222 **0.000351**→W223 **0.000351**→W224 **0.00035**】","se_mu 收窄链 …→W209 0.000362→W211 0.000361→W212 0.000360→W213 0.000359→W214 0.000358→W215 0.000357→W216 0.000356→W217 **0.000355**→W218 **0.000355**→W219 **0.000354**→W220 **0.000353**→W221 **0.000352**→W222 **0.000351**→W223 **0.000351**→W@L24@ **0.00035**→W225 **0.000349**】")],
 38: [("5. **W226+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 511_804..513_803 CLEAN（hops=0·pre-W225 宇宙）；B naive first-clean **512_004..512_203 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W226：W226 冻结方必须在 post-W225 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W225 B 带 511_804..512_003 注册后将拒 naive W226 A 窗**——W226 A 重 derive 同强制（越过 W225 B 带·阶梯 A-hops-prior-B 第八十六例）；verify at W226 prereg","5. **W227+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 514_004..516_003 CLEAN（hops=0·pre-W226 宇宙）；B naive first-clean **514_204..514_403 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W227：W227 冻结方必须在 post-W226 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W226 B 带 514_004..514_203 注册后将拒 naive W227 A 窗**——W227 A 重 derive 同强制（越过 W226 B 带·阶梯 A-hops-prior-B 第八十七例）；verify at W227 prereg")],
 39: [(" --wave 225/finalize --wave 225"," --wave 226/finalize --wave 226")],
 40: [("【n1_w225/ 分片计数增长·唯一点火证据·r325 律】","【n1_w226/ 分片计数增长·唯一点火证据·r325 律】")],
 41: [("`results/p2cal_ext/n1_w225/shard-<k>-of-12.json`","`results/p2cal_ext/n1_w226/shard-<k>-of-12.json`")],
 42: [("`results/perpetual_faces/n1_w225_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 键序前置=**起草窗零在飞上游席（W1..W224 全落）**","`results/perpetual_faces/n1_w226_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 键序前置=**起草窗零在飞上游席（W1..W225 全落）**")],
 43: [("engine_owner==bm-c 54 行注册〔冻结时点〕+ 本候选","engine_owner==bm-c 55 行注册〔冻结时点〕+ 本候选")],
 44: [("段——r937 W224 §7 范式）","段——r940 W225 §7 范式）")],
 45: [("（占位·finalize 同窗回填：§5.5 W226+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——r937 W224 §8 范式）","（占位·finalize 同窗回填：§5.5 W227+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——r940 W225 §8 范式）")],
}

# ---------- build + apply W226 pairs ----------
PAIRS = []
for i, old in enumerate(OLD25):
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
# Pairs covered every W225 self face (each count==1 asserted). Remaining
# "W225" tokens = pair-written legit refs (chain W225 leg, refusing band,
# W225 finalize keys, W1..W225 scope) which must STAY W225 -- mask, then age
# one-wave-older W224 refs to W225, then restore. @L24@/@T24@ hold heritage
# tokens immune.
t = t.replace("n1_w225_results", "n1_@u_w@_results")   # protect pair-written upstream file refs
t = t.replace("PERPETUAL-N1-W225", "PERPETUAL-N1-W226")
t = t.replace("PERPETUAL_N1_W225", "PERPETUAL_N1_W226")
t = t.replace("n1_w225", "n1_w226")
t = t.replace("_w225bmc", "_w226bmc")
t = t.replace("W225", "@U_W@")
t = t.replace("W224", "W225")
t = t.replace("n1_w224", "n1_w225")
t = t.replace("PERPETUAL_N1_W224", "PERPETUAL_N1_W225")
t = t.replace("_w224bmc", "_w225bmc")
t = t.replace("@u_w@", "w225")
t = t.replace("@U_W@", "W225")
t = t.replace("@L24@", "224")
t = t.replace("@T24@", "25")

# ---- stale-token checklist (must all be ZERO) ----
STALE = ["509_804..511_803", "509_604..511_603", "509_604..509_803", "509_804..510_003",
         "509804", "511804", "509_804+j", "511_804+j", "第 223 枚", "EIGHTY-FIFTH", "第八十五例", "第五十五枚",
         "214 注册在册", "bmc_ordinal=55", "r939 freeze 窗", "0.3168", "−0.09277199",
         "−0.09231609", "0.24508442", "1943-bmc", "c78dd1a44",
         "19:1x（W224 面完整性", "19:1x finalize one-pass】", "r937 absorb 窗", "二百二十二行",
         "共二百二十二面", "机证 222 行", "第 215 波",
         "n_eff_held_equal 914,389", "line_pre_w224 1.1914", "=**492,920 投影**", "engine_owner==bm-c 54 行",
         "prose 55th", "r937 freeze receipt 54th", "第 55 枚 EXACT", "pre-W225 宇宙",
         "W226 freezer 承接面", "r937 W224 §7 范式", "r937 W224 §8 范式", "r937/W224 先例",
         "W225 B 带 511_804..512_003 注册后将拒 naive W226",
         "（509_803+1）", "（511_803+1）", "波号 225=", "A base=509804", "B base=511804", "n1_w225/ 分片计数增长",
         'batch_name="PERPETUAL-N1-W225"', "line_merged@K490,720",
         "实差 0.0005 在带内", "parity 83 行",
         "W136..W224 先例链披露", "W5..W224 先例", "v2..W224 落地", "W2..W224 落地 runner",
         "W2..W224 带（冻结时点", "W2..W224 全注册在冻结时点成立", "W1..W224 N1 finalize 已全部落地",
         "W1..W224 已落账", "（W1..W224 全落）", "490,720+2,200", "K=490,720 合并池",
         "净账本锚头 916,589", "净账本锚头 **916,589**", "splice d307e3d1d", "W224 **0.00035**】",
         "verify at W226 prereg", "r938 窗", "2026-10-12 20:1x"]
# NOTE: "511_804..513_803" / "512_004..512_203" are NOT stale in the W226
# face -- they are the fresh A/B arithmetic-continuation faces (SUB[7]/SUB[8]
# /SUB[24]/SUB[25] write them); the §5.5 projection instances were consumed
# by pair 38. Same digits, different semantics (probed live 21:0x).
# "511_804..512_003" is NOT stale -- it is the fresh upstream refusing band
# (>=2 asserted below). "n1_w225_results.json" file refs stay (upstream
# legs) while "n1_w225/ 分片计数增长" IS stale (self shard face now n1_w226).
# "511804" IS stale here but listed bare-digit-gated: the fresh B seed base
# is 514004; W225's 511804 appears only inside band-range strings with
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
NEW = ["PERPETUAL-N1-W226", "第 224 枚", "512_004..514_003", "514_004..514_203",
       "EIGHTY-SIXTH", "第八十六例", "第八十七例", "第五十六枚",
       "918,789", "492,920", "495,120", "916,589",
       "MSG-20261012-2040-bmc-w226-seat", "d7d270752",
       "bmc_ordinal=56", "n1_w226_results.json", "0.3014", "−0.09279454",
       "−0.09782473", "0.24508719", "n_eff_held_equal 916,589", "0.000349",
       "1.1914", "1.1915", "第 216 波", "514_004..516_003", "514_204..514_403",
       "511_804..513_803", "512_004..512_203",
       "0.0050", "84ecb3a3a", "第 56 枚 EXACT", "W227 freezer 承接面",
       "r940 W225 §7 范式", "K-lift **−0.0001**", "实差 0.0050 在带内",
       "parity 84 行", "二百二十三行", "共二百二十三面", "机证 223 行",
       "r941 freeze 窗", "prose 56th", "55th owned 承袭",
       "20:2x（W225 面完整性", "20:2x finalize one-pass】", "verify at W227 prereg",
       "r939/W225 先例"]
for s in NEW:
    assert t.count(s) >= 1, f"NEW token missing: {s}"
# in-band sanity: own A band appears as the ADMIT face (>=4), own B band too
assert t.count("512_004..514_003") >= 4 and t.count("514_004..514_203") >= 4
# upstream W225 refusing band appears in A-face prose (band-facts + §3A)
assert t.count("511_804..512_003") >= 2
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
# healed RAM list + estate note + se_mu chain present
assert t.count("W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225 低 RAM 实烧先例") == 1
assert t.count("（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225）") == 1
assert t.count("按 _w225bmc_freeze_edits.py 模板派生") == 1
assert t.count("→W213 0.000359→W214 0.000358→W215 0.000357→W216 0.000356→W217 **0.000355**→W218 **0.000355**→W219 **0.000354**→W220 **0.000353**→W221 **0.000352**→W222 **0.000351**→W223 **0.000351**→W224 **0.00035**→W225 **0.000349**】") == 1

out = r"research\PERPETUAL_N1_W226_PREREG.md"
open(out, "wb").write(t.encode("utf-8"))
print("W226 prereg derived OK:", out)
print("bytes:", len(t.encode("utf-8")), "| sha16:", hashlib.sha256(t.encode("utf-8")).hexdigest()[:16])
print("W225(upper) refs (upstream, expected 40+):", t.count("W225"), "| W226 self:", t.count("W226"))
print("W224 heritage refs (chain legs + estate face):", t.count("W224"))
