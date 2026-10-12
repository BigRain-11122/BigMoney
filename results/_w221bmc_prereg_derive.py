# -*- coding: utf-8 -*-
# W221 per-wave prereg derivation (bm-c r925 freeze-prep, 2026-10-12 12:5x).
# Method: machine transform of the freeze-time W220 prereg blob
# (git show a9aee1d05:research/PERPETUAL_N1_W220_PREREG.md -- the exact
# pre-backfill commit face) with an explicit ordered replacement table.
# Pair old-sides are REPLAYED AT RUNTIME from the committed lineage chain
# (results/_w216bmc_prereg_derive.py PAIRS literal + _w217 SUB + _w218 SUB +
# _w219 SUB + _w220 SUB literals -- FIVE-LEVEL replay chain, one deeper than
# the W220 four-level chain; the W220 editor_gen same-window fix (r923 absorb
# freeze-window label) is replayed as a sixth corrective step anchored to the
# committed blob; placeholders materialized per level) -- zero transcription;
# every replayed block is assert-verified count==1 in the freeze-time blob
# BEFORE any pair application (r787 preflight law).
# Bands/facts machine-derived from the committed ADMIT receipt
# results/_w221bmc_20261012_probe_receipt.json + n1_w220_results.json --
# never transcribed by eye (r587).
import ast, hashlib, json, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

# ---------- freeze-time W220 blob ----------
BLOB = subprocess.run(["git", "-C", REPO, "show",
                       "a9aee1d05:research/PERPETUAL_N1_W220_PREREG.md"],
                      capture_output=True).stdout
assert BLOB, "freeze-time W220 blob fetch failed"
t = BLOB.decode("utf-8")
assert "## §7" in t and "占位" in t, "not the freeze-time (pre-backfill) face"

# ---------- upstream W219 blob (RAM replay value for the SUB19/20 BinOps) ----------
BLOB219 = subprocess.run(["git", "-C", REPO, "show",
                          "0dae35332:research/PERPETUAL_N1_W219_PREREG.md"],
                         capture_output=True).stdout
assert BLOB219, "freeze-time W219 blob fetch failed"
t219 = BLOB219.decode("utf-8")

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

# RAM notes machine-anchored to the committed blobs (zero eyeball)
_m219 = re.search(r"本窗 free RAM ~(\d+\.\d)GB", t219)
assert _m219, "W219 RAM note face not found"
RAM_REPLAY_219 = "~" + _m219.group(1)
_m220 = re.search(r"本窗 free RAM ~(\d+\.\d)GB", t)
assert _m220, "W220 RAM note face not found"
RAM_FACE_220 = "~" + _m220.group(1)
print(f"RAM anchors: W219-face {RAM_REPLAY_219!r} | W220-face {RAM_FACE_220!r}")

pairs216 = extract_lit(r"results\_w216bmc_prereg_derive.py", "PAIRS", 46)
SUB17 = extract_lit(r"results\_w217bmc_prereg_derive.py", "SUB", 46)
SUB18 = extract_lit(r"results\_w218bmc_prereg_derive.py", "SUB", 46)
SUB19 = extract_lit(r"results\_w219bmc_prereg_derive.py", "SUB", 46,
                    vars={"RAM_GB": RAM_REPLAY_219})
SUB20 = extract_lit(r"results\_w220bmc_prereg_derive.py", "SUB", 46,
                    vars={"RAM_GB": RAM_FACE_220, "RAM_REPLAY": RAM_REPLAY_219})

OLD16 = [b.replace("@L14@", "214").replace("@T15@", "15") for _, b in pairs216]
OLD17 = []
for i, old in enumerate(OLD16):
    new = old
    for find, repl in SUB17[i]:
        c = new.count(find)
        assert c == 1, f"replay SUB17[{i}] count {c} != 1 for: {find[:60]}..."
        new = new.replace(find, repl, 1)
    OLD17.append(new.replace("@L14@", "214").replace("@L15@", "215").replace("@T16@", "16"))
OLD18 = []
for i, old in enumerate(OLD17):
    new = old
    for find, repl in SUB18[i]:
        c = new.count(find)
        assert c == 1, f"replay SUB18[{i}] count {c} != 1 for: {find[:60]}..."
        new = new.replace(find, repl, 1)
    OLD18.append(new.replace("@L14@", "214").replace("@L15@", "215").replace("@L16@", "216").replace("@T17@", "17"))
OLD19 = []
for i, old in enumerate(OLD18):
    new = old
    for find, repl in SUB19[i]:
        c = new.count(find)
        assert c == 1, f"replay SUB19[{i}] count {c} != 1 for: {find[:60]}..."
        new = new.replace(find, repl, 1)
    OLD19.append(new.replace("@L14@", "214").replace("@L15@", "215").replace("@L16@", "216").replace("@L17@", "217").replace("@T18@", "18"))
OLD20 = []
for i, old in enumerate(OLD19):
    new = old
    for find, repl in SUB20[i]:
        c = new.count(find)
        assert c == 1, f"replay SUB20[{i}] count {c} != 1 for: {find[:60]}..."
        new = new.replace(find, repl, 1)
    OLD20.append(new.replace("@L14@", "214").replace("@L15@", "215").replace("@L16@", "216").replace("@L17@", "217").replace("@L18@", "218").replace("@T19@", "19"))

# W220 editor_gen same-window fix replay (r923 absorb: freeze-window label
# corrected in the committed face; lineage must reproduce it)
_fix_old = "【bm-c 循环班 r922 freeze 窗·2026-10-12 10:5x·"
_fix_new = "【bm-c 循环班 r923 freeze 窗（absorb r922 freeze-prep estate）·2026-10-12 11:4x·"
assert OLD20[0].count(_fix_old) == 1, "editor_gen fix anchor missing in replayed block[0]"
OLD20[0] = OLD20[0].replace(_fix_old, _fix_new, 1)

# preflight: every replayed W220-face block sits exactly once in the blob
for i, old in enumerate(OLD20):
    c = t.count(old)
    assert c == 1, f"preflight block[{i}] count {c} != 1 in freeze-time W220 blob"
print("preflight OK: 46/46 replayed blocks sit count==1 in the freeze-time W220 blob")

# ---------- machine-derived anchors (never hand-copied) ----------
rec = json.load(open(r"results\_w221bmc_20261012_probe_receipt.json", encoding="utf-8"))
assert rec["verdict"] == "ADMIT" and rec["bands"] == {"A": "501004_503003", "B": "503004_503203"}
w220 = json.load(open(r"results\perpetual_faces\n1_w220_results.json", encoding="utf-8"))
led = w220["science_gates"]["ledger"]
assert led["total"] == 907789 and led["prev_total"] == 905589 and led["batch_trials"] == 2200
merged = w220["null_pool_cumulative"]["merged"]
assert merged["n_values"] == 481920
w220only = w220["null_pool_cumulative"]["w220_only"]
A_p95 = w220["families"]["A_random_engine_exit"]["full_sharpe_p95"]
kl = w220["skill_line_v2_k_lift"]
assert kl["line_delta_k_lift"] == -0.0001 and kl["n_eff_held_equal"] == 905589
assert kl["line_pre_w220"] == 1.1911 and kl["line_merged_481920"] == 1.191
se_mu = w220["null_pool_cumulative"]["se_mu_at_k481920"]
assert se_mu == 0.000353
leg1, leg4 = rec["legs"]["leg1"], rec["legs"]["leg4"]
assert leg1["A"] == [501004, 503003] and leg1["B"] == [503004, 503203]
assert leg1["ARITH_A"] == [500804, 502803] and leg1["B_naive_first_clean"] == [501004, 501203]
assert leg4["W222p_A"] == "503004..505003" and leg4["W222p_B"] == "503204..503403"
assert leg4["W222p_B_lands_inside_W222p_A"] is True
leg0 = rec["legs"]["leg0"]
assert leg0["rows"] == 218 and leg0["owner_rows"] == 210 and leg0["bmc_ordinal"] == 51 and leg0["ordinal"] == 211
# formatted-string guards: every literal below that carries a machine value
# is assert-verified against the live JSON here (zero eyeball)
def fmt8(x):
    return ("−" if x < 0 else "") + f"{abs(x):.8f}"
assert fmt8(merged["mu"]) == "−0.09279922", fmt8(merged["mu"])
assert fmt8(w220only["mu"]) == "−0.09285445", fmt8(w220only["mu"])
assert f"{merged['sigma']:.8f}" == "0.24511808", f"{merged['sigma']:.8f}"
assert f"{abs(w220only['mu'] - merged['mu']):.4f}" == "0.0001", f"{abs(w220only['mu'] - merged['mu']):.4f}"
assert f"{A_p95:.4f}" == "0.3120", f"{A_p95:.4f}"
assert f"{kl['line_merged_481920']:.4f}" == "1.1910"
# free RAM live read (honesty for the RAM note). Band widened at the low end
# vs the W220 face (0.2): the MV-album film chain + jman LoRA training (both
# CEO-priority lanes) hold the box at ~0.1G free -- honest face, engine RAM
# gate governs burn admission separately.
import psutil
_avail_gb = psutil.virtual_memory().available / 1e9
assert 0.08 <= _avail_gb <= 3.0, f"unexpected RAM face: {_avail_gb}"
RAM_GB = f"~{_avail_gb:.1f}"
print(f"live free RAM: {_avail_gb:.2f} GB -> note '{RAM_GB}GB'")
# engine live status (honesty for the block-1 carried face)
_st = subprocess.run([sys.executable, "Tools/saturation_engine.py", "status"],
                     cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
assert _st.returncode == 0, f"engine status FAIL: {(_st.stdout or '')[-300:]}"
assert '"burns_active": []' in (_st.stdout or "") or "'burns_active': []" in (_st.stdout or "") or '"burns_active":[]' in (_st.stdout or ""), "engine burns_active not empty at derive time"
assert '"queue_next": []' in (_st.stdout or "") or "'queue_next': []" in (_st.stdout or "") or '"queue_next":[]' in (_st.stdout or ""), "engine queue_next not empty at derive time"
print("engine live status: burns_active=[] queue_next=[] verified")

# ---------- per-pair submaps: index -> ordered (find, replace) ----------
SUB = {
 0: [("PERPETUAL-N1-W220 预注册 · N1 nulls-deepening 泵第 218 枚","PERPETUAL-N1-W221 预注册 · N1 nulls-deepening 泵第 219 枚"),
     ("engine_owner 行 209 注册在册（表尾 W219 行·probe leg0 机证 217 行","engine_owner 行 210 注册在册（表尾 W220 行·probe leg0 机证 218 行"),
     ("本候选=bm-c 第五十枚自有波【live-derive face：席面 prose 49th=seat-time face（r921 窗 W219 注册后 live derive·r920 freeze receipt 49th owned 承袭）→freeze 时 live derive bm-c rows 49+候选=第 50 枚 EXACT","本候选=bm-c 第五十一枚自有波【live-derive face：席面 prose 50th=seat-time face（r924 窗 W220 注册后 live derive·r923 freeze receipt 50th owned 承袭）→freeze 时 live derive bm-c rows 50+候选=第 51 枚 EXACT"),
     ("【bm-c 循环班 r923 freeze 窗（absorb r922 freeze-prep estate）·2026-10-12 11:4x·","【bm-c 循环班 r925 freeze 窗·2026-10-12 12:5x·")],
 1: [("live-read r922：","live-read r925：")],
 2: [("波号 220=注册表 W219 席后首个自由号","波号 221=注册表 W220 席后首个自由号"),
     ("r921 窗实跑：origin inbox/processed/ 零 W220 席位外机命中","r924 窗实跑：origin inbox/processed/ 零 W221 席位外机命中"),
     ("perpetual_faces.py 零 220 行","perpetual_faces.py 零 221 行"),
     ("perpetual_faces_n1.py 零 PERPETUAL-N1-W220 WAVE_CONFIGS","perpetual_faces_n1.py 零 PERPETUAL-N1-W221 WAVE_CONFIGS"),
     ("origin 零 PERPETUAL_N1_W220_PREREG.md","origin 零 PERPETUAL_N1_W221_PREREG.md")],
 3: [("+W214=bm-c r910 五面冻结（4664900c8）+引擎自燃 12/12+r911 finalize one-pass 已落（K=468,720·账本头 894,589 机读·n1_w214_results.json·05:2x）+W215=bm-c r912 五面冻结（1e71c3b93）+引擎自燃 12/12+r913 finalize one-pass 已落（K=470,920·账本头 896,789 机读·n1_w215_results.json·06:1x）+W216=bm-c r914 五面冻结（0b3c489f0）+引擎自燃 12/12+r915 finalize one-pass 已落（K=473,120·账本头 898,989 机读·n1_w216_results.json·06:5x）+W217=bm-c r916 五面冻结（ad011fee2）+引擎自燃 12/12+r917 finalize one-pass 已落（K=475,320·账本头 901,189 机读·n1_w217_results.json·08:1x）+W218=bm-c r918 五面冻结（9afb0b1d7）+引擎自燃 12/12+r919 finalize one-pass 已落（K=477,520·账本头 903,389 机读·n1_w218_results.json·09:1x）+W219=bm-c r920 五面冻结（0dae35332）+引擎自燃 12/12+r921 finalize one-pass 已落（K=479,720·账本头 905,589 机读·n1_w219_results.json·10:1x）——本波上游链=W1..W219 finalize 全落地","+W214=bm-c r910 五面冻结（4664900c8）+引擎自燃 12/12+r911 finalize one-pass 已落（K=468,720·账本头 894,589 机读·n1_w214_results.json·05:2x）+W215=bm-c r912 五面冻结（1e71c3b93）+引擎自燃 12/12+r913 finalize one-pass 已落（K=470,920·账本头 896,789 机读·n1_w215_results.json·06:1x）+W216=bm-c r914 五面冻结（0b3c489f0）+引擎自燃 12/12+r915 finalize one-pass 已落（K=473,120·账本头 898,989 机读·n1_w216_results.json·06:5x）+W217=bm-c r916 五面冻结（ad011fee2）+引擎自燃 12/12+r917 finalize one-pass 已落（K=475,320·账本头 901,189 机读·n1_w217_results.json·08:1x）+W218=bm-c r918 五面冻结（9afb0b1d7）+引擎自燃 12/12+r919 finalize one-pass 已落（K=477,520·账本头 903,389 机读·n1_w218_results.json·09:1x）+W@L19@=bm-c r920 五面冻结（0dae35332）+引擎自燃 12/12+r921 finalize one-pass 已落（K=479,720·账本头 905,589 机读·n1_w@L19@_results.json·10:1x）+W220=bm-c r923 五面冻结（a9aee1d05）+引擎自燃 12/12+r923 finalize one-pass 已落（K=481,920·账本头 907,589 机读·n1_w220_results.json·12:0x）——本波上游链=W1..W220 finalize 全落地")],
 4: [("本机席位公示=MSG-20261012-1025-bmc-w220-seat 已推 origin 13a81d182 先于本冻结【r565 律·席位先行·r921 窗】；下游 W221+ 投影见 §5.5（probe 机证 leg4·W221 freezer 承接面）】。","本机席位公示=MSG-20261012-1225-bmc-w221-seat 已推 origin 063bb5a77 先于本冻结【r565 律·席位先行·r924 窗】；下游 W222+ 投影见 §5.5（probe 机证 leg4·W222 freezer 承接面）】。")],
 5: [("W2..W219 全注册在冻结时点成立","W2..W220 全注册在冻结时点成立")],
 6: [("results/_w220bmc_20261012_probe_receipt.json","results/_w221bmc_20261012_probe_receipt.json")],
 7: [("A-ext seed=498_804..500_803","A-ext seed=501_004..503_003"),
     ("A 面=FIRST-CLEAN past prior-wave B 阶梯第八十例","A 面=FIRST-CLEAN past prior-wave B 阶梯第八十一例"),
     ("A 面算术继续带 498_604..500_603（自注册 W219 A 尾 498_603 续）在其起点即被 W219 注册 B 带 498_604..498_803 **拒**（W219 席位 leg4 投影+其 probe 所预言+强制）→ 诚实前向走 **1 hop** 落 **498_804..500_803**","A 面算术继续带 500_804..502_803（自注册 W220 A 尾 500_803 续）在其起点即被 W220 注册 B 带 500_804..501_003 **拒**（W220 席位 leg4 投影+其 probe 所预言+强制）→ 诚实前向走 **1 hop** 落 **501_004..503_003**"),
     ("A base==前波 B 尾+1（498_803+1）机检关系","A base==前波 B 尾+1（501_003+1）机检关系"),
     ("A-hops-prior-B 阶梯几何第八十例（E36 卡）","A-hops-prior-B 阶梯几何第八十一例（E36 卡）"),
     ("A_semantics 机读序数=EIGHTIETH（第八十例）","A_semantics 机读序数=EIGHTY-FIRST（第八十一例）")],
 8: [("B-ext exit seed=500_804..501_003","B-ext exit seed=503_004..503_203"),
     ("B 面 naive first-clean 继续带 498_804..499_003 在注册宇宙上 CLEAN 但**落在本波 A 窗 498_804..500_803 内**","B 面 naive first-clean 继续带 501_004..501_203 在注册宇宙上 CLEAN 但**落在本波 A 窗 501_004..503_003 内**"),
     ("B 带本波 A 窗保留走 **1 hop** 落 **500_804..501_003**","B 带本波 A 窗保留走 **1 hop** 落 **503_004..503_203**"),
     ("B base==本波 A 尾+1（500_803+1）机检关系","B base==本波 A 尾+1（503_003+1）机检关系"),
     ("**W219 席位 leg4 投影承接面注记兑现**：投影预言 W220 须在 post-W219 注册宇宙重 derive 且 derive B 时预留本波 A 窗","**W220 席位 leg4 投影承接面注记兑现**：投影预言 W221 须在 post-W220 注册宇宙重 derive 且 derive B 时预留本波 A 窗")],
 9: [("R250：W220 带从未指派","R250：W221 带从未指派")],
 10: [("A base=498804 span=2000 checked=2000 verdict=FREE / B base=500804 span=200 checked=200 verdict=FREE","A base=501004 span=2000 checked=2000 verdict=FREE / B base=503004 span=200 checked=200 verdict=FREE")],
 11: [("扫描面=pre-W220 全二百一十七行注册 N1 带表（表尾 W219 行·probe leg0 机证 217 行 live 单态 owner rows 209）","扫描面=pre-W221 全二百一十八行注册 N1 带表（表尾 W220 行·probe leg0 机证 218 行 live 单态 owner rows 210）")],
 12: [("W2..W219 落地 runner","W2..W220 落地 runner")],
 13: [("selftest W220 face 将随五面冻结落地验证","selftest W221 face 将随五面冻结落地验证")],
 14: [("本件与 results/_w220bmc_freeze_edits.py","本件与 results/_w221bmc_freeze_edits.py"),
     ("按 _w219bmc_freeze_edits.py 模板派生","按 _w2@T19@bmc_freeze_edits.py 模板派生"),
     ("gate0.5 自查 W219 行+W219 finalize 件在场","gate0.5 自查 W220 行+W220 finalize 件在场"),
     ("estate 提取面=本机 W219 块物理字节","estate 提取面=本机 W220 块物理字节"),
     ("（r920/W219 先例 freeze-prep 同式","（r923/W220 先例 freeze-prep 同式")],
 15: [("- 批名=**PERPETUAL-N1-W220**。","- 批名=**PERPETUAL-N1-W221**。")],
 16: [("**W1..W219 N1 finalize 已全部落地**","**W1..W220 N1 finalize 已全部落地**"),
     ("净账本锚头 **905,589**·K=479,720 合并池·n1_w219_results.json 机读·W219 finalize one-pass bm-c r921 窗 10:1x（W219 面完整性=12/12 shards consumed+finalize audit finalize_only=true 收口·r920 freeze 0dae35332","净账本锚头 **907,789**·K=481,920 合并池·n1_w220_results.json 机读·W220 finalize one-pass bm-c r923 窗 12:0x（W220 面完整性=12/12 shards consumed+finalize audit finalize_only=true 收口·r923 freeze a9aee1d05")],
 17: [("累计 null 池=479,720+2,200（本波）=**481,920 投影**","累计 null 池=481,920+2,200（本波）=**484,120 投影**")],
 18: [("（本机席位公示 MSG-20261012-1025-bmc-w220-seat 已推 origin 13a81d182 r565 律·probe W221+ 投影 A 500_804..502_803 / B 501_004..501_203","（本机席位公示 MSG-20261012-1225-bmc-w221-seat 已推 origin 063bb5a77 r565 律·probe W222+ 投影 A 503_004..505_003 / B 503_204..503_403"),
     ("投影 B 落投影 A 窗内·W220 B 带 500_804..501_003 注册后将拒 naive W221 A 窗=阶梯 A-hops-prior-B 第八十一例——**W221 freezer 承接面强制注记：须在 post-W220 宇宙重 derive 且 derive B 时预留本波 A 窗","投影 B 落投影 A 窗内·W221 B 带 503_004..503_203 注册后将拒 naive W222 A 窗=阶梯 A-hops-prior-B 第八十二例——**W222 freezer 承接面强制注记：须在 post-W221 宇宙重 derive 且 derive B 时预留本波 A 窗")],
 19: [("T-2026-10-01-141 s1 引擎线第 210 波【bm-c 第五十枚自有波【机面 derive：probe leg0 bmc_ordinal=49 live face（r921 窗 live 单态计法）——freeze 时 live derive bm-c rows 49+候选=第 50 枚 EXACT","T-2026-10-01-141 s1 引擎线第 211 波【bm-c 第五十一枚自有波【机面 derive：probe leg0 bmc_ordinal=50 live face（r924 窗 live 单态计法）——freeze 时 live derive bm-c rows 50+候选=第 51 枚 EXACT"),
     ("波号=注册表 W219 席后首个自由号·单态零席位空档于冻结时点成立；中位公示 MSG-20261012-1025-bmc-w220-seat 先推 origin 13a81d182 r565 律","波号=注册表 W220 席后首个自由号·单态零席位空档于冻结时点成立；中位公示 MSG-20261012-1225-bmc-w221-seat 先推 origin 063bb5a77 r565 律")],
 20: [("本窗 free RAM " + RAM_FACE_220 + "GB","本窗 free RAM " + RAM_GB + "GB"),
     ("W206/W211/W212/W213/W214/W215/W216/W217/W218/W219 低 RAM 实烧先例","W206/W211/W212/W213/W214/W215/W216/W217/W218/W@L19@/W220 低 RAM 实烧先例")],
 21: [("复读自见 W220 行并点火自烧","复读自见 W221 行并点火自烧")],
 22: [("--prereg research/PERPETUAL_N1_W220_PREREG.md","--prereg research/PERPETUAL_N1_W221_PREREG.md")],
 23: [("v2..W219 落地）","v2..W220 落地）")],
 24: [("entry rng seed=**498_804+j**","entry rng seed=**501_004+j**"),
     ("法典 §4 W220 行 A=498_804..500_803","法典 §4 W221 行 A=501_004..503_003"),
     ("阶梯第八十例**：算术续带 498_604..500_603 起点即被 W219 注册 B 带 498_604..498_803 拒→1 hop 落 498_804..500_803","阶梯第八十一例**：算术续带 500_804..502_803 起点即被 W220 注册 B 带 500_804..501_003 拒→1 hop 落 501_004..503_003")],
 25: [("entry rng=**498_804+j**","entry rng=**501_004+j**"),
     ("exit rng=**500_804+j**","exit rng=**503_004+j**"),
     ("法典 §4 W220 行 B=500_804..501_003","法典 §4 W221 行 B=503_004..503_203"),
     ("B 算术续带 498_804..499_003 在注册宇宙上 CLEAN 但落在本波 A 窗 498_804..500_803 内","B 算术续带 501_004..501_203 在注册宇宙上 CLEAN 但落在本波 A 窗 501_004..503_003 内"),
     ("保留走落 500_804..501_003","保留走落 503_004..503_203"),
     ("与 W219 席位 leg4 投影承接面注记兑现收敛","与 W220 席位 leg4 投影承接面注记兑现收敛")],
 26: [("（selftest 强制）：W220 带与 v1 在用带","（selftest 强制）：W221 带与 v1 在用带")],
 27: [("W2..W219 带（冻结时点全注册单态）","W2..W220 带（冻结时点全注册单态）")],
 28: [("本波机验 ADMIT 回执在场=_w220bmc_20261012 探针窗","本波机验 ADMIT 回执在场=_w221bmc_20261012 探针窗")],
 29: [("selftest W220 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W219 行 parity 腿","selftest W221 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W220 行 parity 腿")],
 30: [("从**本机 W219 块物理字节**提取","从**本机 W220 块物理字节**提取"),
     ("W218 块的 W217 leg（1 行）不入 estate 路径·提取后新增 W217+W218 leg 构成 W220 块 parity 78 行（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219）","W@L19@ 块的 W218 leg（1 行）不入 estate 路径·提取后新增 W218+W@L19@ leg 构成 W221 块 parity 79 行（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W@L19@+W220）")],
 31: [("起草窗实流 W1..W219 已落账 479,720 实测","起草窗实流 W1..W220 已落账 481,920 实测")],
 32: [("batch_name=\"PERPETUAL-N1-W220\", batch_trials=2200, file_name=\"results/perpetual_faces/n1_w220_results.json\"","batch_name=\"PERPETUAL-N1-W221\", batch_trials=2200, file_name=\"results/perpetual_faces/n1_w221_results.json\"")],
 33: [("（起草窗实况注记：**W1..W219 N1 finalize 已全部落地**——净账本锚头 905,589·**K=479,720 合并池**·**零在飞上游席——本波 §5 预测键=**W219 实测值**【results/perpetual_faces/n1_w219_results.json·N1 面最新已落账键·10:1x finalize one-pass】。","（起草窗实况注记：**W1..W220 N1 finalize 已全部落地**——净账本锚头 907,789·**K=481,920 合并池**·**零在飞上游席——本波 §5 预测键=**W220 实测值**【results/perpetual_faces/n1_w220_results.json·N1 面最新已落账键·12:0x finalize one-pass】。")],
 34: [("1. W220-only mu 与累计池 merged mu（W219 实测键 **−0.09279897**·K=479,720 合并池·W219-only 实测 **−0.09624182**）差异 **|Δ|<0.02**（W2..W219 共二百一十七面实测 mu 稳定先例·单波跨键微；W219-only vs merged 实差 0.0034 在带内）。","1. W221-only mu 与累计池 merged mu（W220 实测键 **−0.09279922**·K=481,920 合并池·W220-only 实测 **−0.09285445**）差异 **|Δ|<0.02**（W2..W220 共二百一十八面实测 mu 稳定先例·单波跨键微；W220-only vs merged 实差 0.0001 在带内）。")],
 35: [("键 **0.24512506**=W219 合并池实测）。","键 **0.24511808**=W220 合并池实测）。")],
 36: [("3. A 档 full_sharpe_p95 与 W219 A 档 p95（**0.3142** 实测锚）差 **<0.05**（门标注法 W5..W219 先例","3. A 档 full_sharpe_p95 与 W220 A 档 p95（**0.3120** 实测锚）差 **<0.05**（门标注法 W5..W220 先例")],
 37: [("W136..W219 先例链披露","W136..W220 先例链披露"),
     ("键 W219 实测 K-lift **+0.0001**·line_merged@K479,720 **1.1910**·line_pre_w219 1.1909·n_eff_held_equal 903,389","键 W220 实测 K-lift **−0.0001**·line_merged@K481,920 **1.1910**·line_pre_w220 1.1911·n_eff_held_equal 905,589"),
     ("se_mu 收窄链 …→W209 0.000362→W211 0.000361→W212 0.000360→W213 0.000359→W214 0.000358→W215 0.000357→W216 0.000356→W217 **0.000355**→W218 **0.000355**→W219 **0.000354**】","se_mu 收窄链 …→W209 0.000362→W211 0.000361→W212 0.000360→W213 0.000359→W214 0.000358→W215 0.000357→W216 0.000356→W217 **0.000355**→W218 **0.000355**→W@L19@ **0.000354**→W220 **0.000353**】")],
 38: [("5. **W221+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 500_804..502_803 CLEAN（hops=0·pre-W220 宇宙）；B naive first-clean **501_004..501_203 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W221：W221 冻结方必须在 post-W220 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W220 B 带 500_804..501_003 注册后将拒 naive W221 A 窗**——W221 A 重 derive 同强制（越过 W220 B 带·阶梯 A-hops-prior-B 第八十一例）；verify at W221 prereg","5. **W222+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 503_004..505_003 CLEAN（hops=0·pre-W221 宇宙）；B naive first-clean **503_204..503_403 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W222：W222 冻结方必须在 post-W221 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W221 B 带 503_004..503_203 注册后将拒 naive W222 A 窗**——W222 A 重 derive 同强制（越过 W221 B 带·阶梯 A-hops-prior-B 第八十二例）；verify at W222 prereg")],
 39: [(" --wave 220/finalize --wave 220"," --wave 221/finalize --wave 221")],
 40: [("【n1_w220/ 分片计数增长·唯一点火证据·r325 律】","【n1_w221/ 分片计数增长·唯一点火证据·r325 律】")],
 41: [("`results/p2cal_ext/n1_w220/shard-<k>-of-12.json`","`results/p2cal_ext/n1_w221/shard-<k>-of-12.json`")],
 42: [("`results/perpetual_faces/n1_w220_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 键序前置=**起草窗零在飞上游席（W1..W219 全落）","`results/perpetual_faces/n1_w221_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 键序前置=**起草窗零在飞上游席（W1..W220 全落）")],
 43: [("engine_owner==bm-c 49 行注册〔冻结时点〕+ 本候选","engine_owner==bm-c 50 行注册〔冻结时点〕+ 本候选")],
 44: [("段——r921 W219 §7 范式）","段——r923 W220 §7 范式）")],
 45: [("（占位·finalize 同窗回填：§5.5 W221+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——r921 W219 §8 范式）","（占位·finalize 同窗回填：§5.5 W222+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——r923 W220 §8 范式）")],
}

# ---------- build + apply W221 pairs ----------
PAIRS = []
for i, old in enumerate(OLD20):
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
# Pairs covered every W220 self face (each count==1 asserted). Remaining
# "W220" tokens = pair-written legit refs (chain W220 leg, W1..W220 scope)
# which must STAY W220 -- mask, then age one-wave-older W219 refs to W220,
# then restore. @L19@/@T19@ hold heritage tokens immune.
t = t.replace("n1_w220_results", "n1_@u_w@_results")   # protect pair-written upstream file refs
t = t.replace("PERPETUAL-N1-W220", "PERPETUAL-N1-W221")
t = t.replace("PERPETUAL_N1_W220", "PERPETUAL_N1_W221")
t = t.replace("n1_w220", "n1_w221")
t = t.replace("_w220bmc", "_w221bmc")
t = t.replace("W220", "@U_W@")
t = t.replace("W219", "W220")
t = t.replace("n1_w219", "n1_w220")
t = t.replace("PERPETUAL_N1_W219", "PERPETUAL_N1_W220")
t = t.replace("_w219bmc", "_w220bmc")
t = t.replace("@u_w@", "w220")
t = t.replace("@U_W@", "W220")
t = t.replace("@L19@", "219")
t = t.replace("@T19@", "20")

# ---- stale-token checklist (must all be ZERO) ----
STALE = ["498_804..500_803", "498_604..500_603", "498_604..498_803", "498_804..499_003",
         "498804", "第 218 枚", "EIGHTIETH", "第八十例", "第五十枚",
         "209 注册在册", "bmc_ordinal=49", "r921 窗 W219 注册后", "0.3142", "−0.09279897",
         "−0.09624182", "0.24512506", "1025-bmc", "13a81d182",
         "10:1x（W219 面完整性", "10:1x finalize one-pass】", "二百一十七行", "r922 freeze 窗·2026-10-12 10:5x", "第 210 波",
         "n_eff_held_equal 903,389", "1.1909", "0.0034", "=**481,920 投影**", "engine_owner==bm-c 49 行",
         "prose 49th", "r920 freeze receipt 49th", "第 50 枚 EXACT", "pre-W220 宇宙",
         "W221 freezer 承接面", "r921 W219 §7 范式", "r921 W219 §8 范式",
         "W220 B 带 500_804..501_003 注册后将拒 naive W221",
         "（498_803+1）", "（500_803+1）", "波号 220=", "A base=498804", "n1_w220/ 分片计数增长",
         'batch_name="PERPETUAL-N1-W220"', "r923 freeze 窗（absorb r922 freeze-prep estate）"]
# NOTE: "500_804..502_803" / "501_004..501_203" are NOT stale in the W221
# face -- they are the fresh A/B arithmetic-continuation bands (SUB[7]/SUB[8]
# /SUB[24]/SUB[25] write them); the §5.5 projection instances were consumed
# by pair 38. Same digits, different semantics (probed live 12:2x).
# "500_804..501_003" is NOT stale -- it is the fresh upstream refusing band
# (>=2 asserted below). "n1_w220_results.json" file refs stay (upstream
# legs) while "n1_w220/ 分片计数增长" IS stale (self shard face now n1_w221).
for s in STALE:
    c = t.count(s)
    if c:
        import re as _re2
        for m in _re2.finditer(_re2.escape(s), t):
            print(f"--- STALE[{s}] ctx ---")
            print(t[max(0, m.start()-160):m.end()+80].replace("\n", " | "))
    assert c == 0, f"STALE token survives x{c}: {s}"

# ---- new-face presence checks ----
NEW = ["PERPETUAL-N1-W221", "第 219 枚", "501_004..503_003", "503_004..503_203",
       "EIGHTY-FIRST", "第八十一例", "第八十二例", "第五十一枚",
       "907,789", "481,920", "484,120", "905,589",
       "MSG-20261012-1225-bmc-w221-seat", "063bb5a77",
       "bmc_ordinal=50", "n1_w221_results.json", "0.3120", "−0.09279922",
       "−0.09285445", "0.24511808", "n_eff_held_equal 905,589", "0.000353",
       "1.1911", "1.1910", "第 211 波", "503_004..505_003", "503_204..503_403",
       "500_804..502_803", "501_004..501_203",
       "0.0001", "a9aee1d05", "第 51 枚 EXACT", "W222 freezer 承接面",
       "r923 W220 §7 范式"]
for s in NEW:
    assert t.count(s) >= 1, f"NEW token missing: {s}"
# in-band sanity: own A band appears as the ADMIT face (>=4), own B band too
assert t.count("501_004..503_003") >= 4 and t.count("503_004..503_203") >= 4
# upstream W220 refusing band appears in A-face prose (band-facts + §3A)
assert t.count("500_804..501_003") >= 2
# chain-history legs present exactly once each (heritage restored verbatim)
assert t.count("+W213=bm-c r908 五面冻结（a24069f4c）") == 1
assert t.count("+W214=bm-c r910 五面冻结（4664900c8）") == 1
assert t.count("+W215=bm-c r912 五面冻结（1e71c3b93）") == 1
assert t.count("+W216=bm-c r914 五面冻结（0b3c489f0）") == 1
assert t.count("+W217=bm-c r916 五面冻结（ad011fee2）") == 1
assert t.count("+W218=bm-c r918 五面冻结（9afb0b1d7）") == 1
assert t.count("+W219=bm-c r920 五面冻结（0dae35332）") == 1
assert t.count("+W220=bm-c r923 五面冻结（a9aee1d05）") == 1
assert t.count("n1_w213_results.json·04:2x") == 1
assert t.count("n1_w214_results.json·05:2x") == 1
assert t.count("n1_w215_results.json·06:1x") == 1
assert t.count("n1_w216_results.json·06:5x") == 1
assert t.count("n1_w217_results.json·08:1x") == 1
assert t.count("n1_w218_results.json·09:1x") == 1
assert t.count("n1_w219_results.json·10:1x") == 1
assert t.count("n1_w220_results.json·12:0x") == 1
# healed RAM list + estate note + se_mu chain present
assert t.count("W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220 低 RAM 实烧先例") == 1
assert t.count("（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220）") == 1
assert t.count("按 _w220bmc_freeze_edits.py 模板派生") == 1
assert t.count("→W213 0.000359→W214 0.000358→W215 0.000357→W216 0.000356→W217 **0.000355**→W218 **0.000355**→W219 **0.000354**→W220 **0.000353**】") == 1

out = r"research\PERPETUAL_N1_W221_PREREG.md"
open(out, "wb").write(t.encode("utf-8"))
print("W221 prereg derived OK:", out)
print("bytes:", len(t.encode("utf-8")), "| sha16:", hashlib.sha256(t.encode("utf-8")).hexdigest()[:16])
print("W220(upper) refs (upstream, expected 40+):", t.count("W220"), "| W221 self:", t.count("W221"))
