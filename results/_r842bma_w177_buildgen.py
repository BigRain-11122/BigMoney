# -*- coding: utf-8 -*-
"""r842 bm-a generator: builds results/_r842bma_w177_prereg_build.py by
AST-extracting the r833 W176 build script's BACK176/EXPECT pairs (all values
machine-read, zero exec side effects -- the r833 script's live git asserts are
time-locked to r833 and must NOT be re-run), then deriving the W177 pairs as
(BACK176 value, token) with new sides = the S77 W177 fact map applied to that
W176 text (r773 pit law compliance inherited: token-first two-phase vmap,
whole-string composites, numerals LAST; r735 substring-order law = BACK list
order preserved, long composite values precede their short substrings).

r587 machine-derived facts (every displayed value read from on-disk receipts
this window):
  - pre-seat probe results/_r841bma_w177_probe_receipt.json rc0 ADMIT
    (leg0 registry 174 rows tail W176 ordinal 167 / bma_ordinal 93 /
    owner_rows 166 / bma_rows 92 / w176_ledger_head 793,105; leg1
    A 404_204..406_203 hops=1 / B 406_204..406_403 hops=1 / naive A
    404_004..406_003 refused at its own start by the registered W176 B
    band 404_004..404_203 (staircase THIRTY-SEVENTH instance E36 per receipt
    A_semantics; W176 sec5.5 anticipated 37th -- projection and receipt
    ordinals MATCH, no divergence face this wave); naive B 404_204..404_403
    lands inside own-A 404_204..406_203; leg2 conflicts 0; leg3 origin
    vacancy True; leg4 W178+ projection A 406_204..408_203 hops=0 / B
    406_404..406_603 hops=0, B inside A;)
  - W176 finalize one-pass landed r839
    (results/perpetual_faces/n1_w176_results.json: merged K=385,120,
    mu=-0.092727 -> 4dp -0.0927, sigma=0.245060 6dp; w176-only mu=-0.0889
    4dp; se_mu_at_k385120=0.000395; A p95=0.3118; k-lift line_merged 1.1845 /
    line_pre 1.1846 / delta -0.0001 / n_eff 790,905; canon flip NOT
    performed; mu_delta_w176_vs_w175ext=+0.000773);
  - W176 sec7/sec8 settle backfill landed r839 one-pass window -- the W177
    A-face cites the W176 sec8 succession face as r839-one-pass-settle
    (true at build time, per on-disk backfill text "finalize=r839 窗收口");
  - W176 freeze registered sha machine-derived = 15ec44ea6 (git log
    origin/main --grep "W176 FREEZE"); W177 seat push sha machine-derived =
    780a0cd30 (git log --diff-filter=A on the seat MSG inbox path); seat
    self-ack archive move landed r841 window (processed/ path
    live-asserted).

E41 law compliance: DRY full-file transform gate runs in-memory BEFORE the
build script is emitted (zero writes until every count assert passes).
"""
import ast
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- 0. extract the freeze-time W176 prereg blob (LF, byte-verbatim) --------
_r = subprocess.run(
    ["git", "show", "15ec44ea6:research/PERPETUAL_N1_W176_PREREG.md"],
    capture_output=True)
assert _r.returncode == 0, "W176 freeze-time blob not reachable"
blob = _r.stdout
assert b"\r\n" not in blob, "blob expected LF (git convention)"
io.open(r"results\_r842bma_w177_prereg_src.txt", "wb").write(blob)
print("W177 src extracted:", len(blob), "bytes (W176 freeze-time blob 15ec44ea6)")

# --- 1. AST-extract the r833 build script's BACK176 + EXPECT ---------------
src833 = io.open(r"results\_r833bma_w176_prereg_build.py", encoding="utf-8").read()
tree = ast.parse(src833)
BACK176 = None
EXPECT = None
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        tg = node.targets[0]
        if isinstance(tg, ast.Name) and tg.id == "BACK176" and isinstance(node.value, ast.List):
            BACK176 = []
            for el in node.value.elts:
                assert isinstance(el, ast.Tuple) and len(el.elts) == 2, "BACK176 pair shape"
                assert isinstance(el.elts[0], ast.Constant) and isinstance(el.elts[1], ast.Constant), "BACK176 consts"
                BACK176.append((el.elts[0].value, el.elts[1].value))
        if isinstance(tg, ast.Name) and tg.id == "EXPECT" and isinstance(node.value, ast.Dict):
            EXPECT = {}
            for k, v in zip(node.value.keys, node.value.values):
                assert isinstance(k, ast.Constant) and isinstance(v, ast.Constant), "EXPECT consts"
                EXPECT[k.value] = v.value
assert BACK176 is not None and EXPECT is not None, "BACK176/EXPECT not extracted"
print("r833 BACK176 entries:", len(BACK176), "EXPECT entries:", len(EXPECT))
back_map = dict(BACK176)
assert len(back_map) == len(BACK176)

# --- 2. W177 facts (machine-read this window) ------------------------------
probe = json.load(open(r"results/_r841bma_w177_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "404204_406203", "B": "406204_406403"}, probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], probe["legs"]["leg4"]
assert leg1["A"] == [404204, 406203] and leg1["B"] == [406204, 406403], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [404004, 406003], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [404204, 404403], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [404204, 404403], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 406204, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 174 and leg0["tail"] == "W176" and leg0["ordinal"] == 167 \
    and leg0["bma_ordinal"] == 93 and leg0["owner_rows"] == 166 \
    and leg0["bma_rows"] == 92 and leg0["w176_ledger_head"] == 793105, leg0
W178p_A = "406_204..408_203"
W178p_B = "406_404..406_603"
assert leg4["W178p_A"] == "406204..408203" and leg4["W178p_B"] == "406404..406603", leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W178p_B_lands_inside_W178p_A"] is True, leg4
assert "THIRTY-SEVENTH" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w176_results.json", encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 385120, "W176 merged K drift"
assert npc["pre_w176_cumulative"]["n_values"] == 382920, "pre-W176 K drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_385120"] == 1.1845 and kl["line_pre_w176"] == 1.1846 \
    and kl["line_delta_k_lift"] == -0.0001 and kl["n_eff_held_equal"] == 790905, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k385120"] == 0.000395, "se_mu drift"
assert npc["mu_delta_w176_vs_w175ext"] == 0.000773, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3118, "p95 drift"
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w176_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
assert MU4 == "-0.0927" and WONLY4 == "-0.0889" and SIG6 == "0.245060", (MU4, WONLY4, SIG6)
LEDG = "{:,}".format(leg0["w176_ledger_head"])
KNEW = "{:,}".format(npc["merged"]["n_values"])
assert LEDG == "793,105" and KNEW == "385,120", (LEDG, KNEW)
KPROJ = "{:,}".format(385120 + 2200)
LEDGPROJ = "{:,}".format(793105 + 2200)
assert KPROJ == "387,320" and LEDGPROJ == "795,305", (KPROJ, LEDGPROJ)

# W176 freeze sha + W177 seat push sha (live machine-derive, r587)
_r_ = subprocess.run(["git", "log", "origin/main", "--format=%h",
                     "--grep=W176 FREEZE", "-1"], capture_output=True, text=True)
W176_SHA = _r_.stdout.strip()
assert W176_SHA == "15ec44ea6", W176_SHA
_r2 = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                     "--diff-filter=A",
                     "--", "fleet/inbox/MSG-2026-10-07-2031-bma-w177-seat.md"],
                    capture_output=True, text=True)
SEAT_SHA = _r2.stdout.strip()
assert SEAT_SHA == "780a0cd30", SEAT_SHA
_r3 = subprocess.run(["git", "show",
                     "origin/main:fleet/inbox/processed/MSG-2026-10-07-2031-bma-w177-seat.md"],
                    capture_output=True)
assert _r3.returncode == 0, "W177 seat MSG not on origin processed/ (r565 pre-freeze law)"
assert "404_204..406_203" in _r3.stdout.decode("utf-8", "replace"), "seat band face drift"
# W176 sec8 succession face settled r839 one-pass window -- A-face cites it
w176p = io.open(r"research\PERPETUAL_N1_W176_PREREG.md", encoding="utf-8", newline="").read()
assert "mu_delta_w176_vs_w175ext" in w176p and "finalize=r839 窗收口" in w176p, \
    "W176 sec7/sec8 settle backfill missing (A-face citation would be false)"

A_BAND = "404_204..406_203"
B_BAND = "406_204..406_403"
NAIVE_A = "404_004..406_003"
NAIVE_B = "404_204..404_403"
PRIOR_B = "404_004..404_203"     # registered W176 B band (refusal band)
A_SEED, B_SEED = "404_204", "406_204"
SEAT_MSG = "MSG-2026-10-07-2031-bma-w177-seat"
MIN = "\u2212"

# --- 3. BACK177 = S77 W177 fact map applied to the W176 text ---------------
BACK177 = {
    "@CHAIN@": back_map["@CHAIN@"] + "；W176=bm-a r834 freeze（" + W176_SHA + "）",
    "@KLT@": back_map["@KLT@"].replace(" 如实披露", "/W176 **" + MIN + "0.0001** 如实披露"),
    "@SEMT@": back_map["@SEMT@"].replace("】）", "→W176 **0.000395**】）"),
    "@S55@": (
        "5. **W178+ 投影（probe 机证·下波冻结方复核非转抄 r587 律）**：A first-clean "
        + W178p_A + " **CLEAN**（hops=0）；B first-clean **" + W178p_B + " CLEAN**（hops=0）"
        "——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W178：W178 冻结方必须在"
        " post-W177 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；"
        "**W177 B 带 " + B_BAND + " 注册后将拒 naive W178 A 窗**——W178 A 重 derive 同强制"
        "（越过 W177 B 带·阶梯 A-hops-prior-B 继承第三十八例）；verify at W178 prereg，"
        "hop 链逐跳在 probe 回执。"
    ),
    "@TITLE@": "# PERPETUAL-N1-W177 预注册 · N1 nulls-deepening 泵第 175 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 166+本候选=bm-a 第九十三枚自有波【r842】）",
    "@WAVEFREE@": "波号 177=注册表 W176 行后首个自由号",
    "@VAC@": "（r841 probe leg2/leg3 实跑）",
    "@SEATPUB@": (
        "本机席位公示=" + SEAT_MSG + " 已推 origin " + SEAT_SHA
        + " 先于本冻结【r565 律·推送窗=r841 seat push 直接快进送达 " + SEAT_SHA
        + "（3-item payload=seat MSG+pre-seat probe 脚本+probe 回执=W146 同推先例·W176 finalize 产物已在 origin 自 r839 投送不再重送）；"
        "self-ack inbox→processed 移位已收档（r841 同窗·r828 先例·如实注记）】"
    ),
    "@MERGE@": "（r841 承袭 r812/r820/r823 gate-合并单回执结构·单窗 derive·dual-window parity N/A 诚实注记）",
    "@AFACE@": (
        "本波 **A-ext seed=" + A_BAND + "**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第三十七例**："
        "A 面算术继续带 " + NAIVE_A + " 在其起点即被已注册 W176 B 带 " + PRIOR_B + " **拒**"
        "（W176 席位 W177+ 投影+r832 probe leg4+W176 行投影散文（r834 冻结件）+W176 §8 承接面注记所预言）"
        "→ 诚实前向走 **1 hop** 落 **" + A_BAND + "**·**A base==前波 B 尾+1（404_203+1）机检关系**"
        "=**A-hops-prior-B 阶梯几何第三十七例（E36 卡）**·非轮转 r587 前向单调断言在走册；"
        "序数面如实披露：W176 §5.5 投影预告第三十七例·r841 probe 回执 A_semantics 机读序数=THIRTY-SEVENTH（第三十七例）·"
        "本件按回执序数面记载非转抄（r587）·投影与回执两读法恒同）"
    ),
    "@BFACE@": (
        "**B-ext exit seed=" + B_BAND + "**（**B 面=FIRST-CLEAN past own-wave A**："
        "B 面算术继续带 " + NAIVE_B + " 在注册宇宙上 CLEAN 但**落在本波 A 窗 " + A_BAND + " 内**"
        "（**同窗互斥面 leg2 律·W141 先例**：A 与 B 同一冻结 commit 双注册·互斥断言强制 B 越过本波 A 窗）"
        "→ B 带本波 A 窗保留走 **1 hop** 落 **" + B_BAND + "**·**B base==本波 A 尾+1（406_203+1）机检关系**·hop 链逐跳在 probe 回执；"
        "**W176 席位 W177+ 投影+r832 probe leg4+W176 行投影散文 re-derive-MANDATORY 注记三面兑现**："
        "投影预言 W177 须在 post-W176 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）"
    ),
    "@R250@": "R250：W177 带从未指派·测量面零结果可锁",
    "@SCANFACE@": "扫描面=pre-W177 全一百七十四行注册 N1 带表（表尾 W176 行·leg0 机证 174 行）",
    "@ANCHOR@": (
        "起稿窗实况：**W1..W176 N1 finalize 已全部落地**【W176 finalize one-pass bm-a r839 承袭收口窗"
        "·§7/§8 已回填（r839 one-pass 窗·W159/W168/W169 拖延窗先例同律·如实注记）】"
        "——净账本锚头 **793,105**（W176 finalize 落账【one-pass·K=385,120 合并池】）"
    ),
    "@POOL@": "累计 null 池=385,120+2,200（本波）=**387,320 投影**",
    "@SEATSENT@": (
        "本机 r841 席位 " + SEAT_MSG + " 已推 origin " + SEAT_SHA
        + "（r841 seat push·r565 律）·probe W178+ 投影 A " + W178p_A + " / B " + W178p_B
        + " **naive-B-inside-naive-A re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·"
        "W177 B 带 " + B_BAND + " 注册后将拒 naive W178 A 窗=阶梯 A-hops-prior-B 继承第三十八例待 W178 注册宇宙复核）"
    ),
    "@CLAIMLAW@": "表尾后新首个自由号自领·r841 probe 单跑兑现注记（本窗冻结消费）",
    "@ORDINALS@": (
        "T-2026-10-01-141 s1 引擎线第 167 波【bm-a 第九十三枚自有波【机面 derive：engine_owner==bm-a 行 92+本候选以 probe leg0 机证为准·"
        "同 W157/W158/W159/W160/W161/W162/W163/W165/W166/W167/W168/W169/W170/W171/W172/W173/W174/W175/W176 最近自有波】。"
        "（波号=注册表 W176 行后首个自由号·单态零席位空档；中位公示 " + SEAT_MSG + " 先推 origin "
        + SEAT_SHA + " r565 律；lane-free；dept:研究）"
    ),
    "@V2W@": "v2..W176 落地",
    "@ASEED@": "entry rng seed=**" + A_SEED + "+j**",
    "@ASEEDPROSE@": (
        "法典 §4 W177 行 A=" + A_BAND + "·**FIRST-CLEAN past prior-wave B 阶梯第三十七例**："
        "算术续带 " + NAIVE_A + " 起点即被 W176 B 带拒→1 hop 落 " + A_BAND
        + "·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场"
    ),
    "@BENTRY@": "entry rng=**" + A_SEED + "+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）",
    "@BSEEDPROSE@": (
        "exit rng=**" + B_SEED + "+j**（法典 §4 W177 行 B=" + B_BAND
        + "·**FIRST-CLEAN past own-wave A**：B 算术续带 " + NAIVE_B
        + " 在注册宇宙上 CLEAN 但落在本波 A 窗 " + A_BAND + " 内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗"
        "→保留走落 " + B_BAND + "·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·"
        "与 W176 席位 W177+ 投影+r832 probe leg4+W176 行投影散文+W176 §8 承接面注记兑现收敛·ADMIT 回执在场）"
    ),
    "@GATEW@": "r841 bm-a 带闸窗（pre-seat probe r841 单窗·gate 腿合并结构承袭 r812/r820/r823 先例·parity N/A 诚实注记）",
    "@FN@": 'file_name="results/perpetual_faces/n1_w177_results.json"',
    "@RFN@": "results/perpetual_faces/n1_w177_results.json",
    "@ODOLD@": "results/perpetual_faces/n1_w176_results.json",
    "@S5ANCH@": "净账本锚头 793,105=W176 finalize 落账【one-pass·bm-a r839 承袭收口窗·§7/§8 已回填（r839 one-pass 窗）】",
    "@S51@": "（W176 实测键 **" + MU4.replace("-", MIN) + "**·K=385,120 合并池·W176-only 实测 **" + WONLY4.replace("-", MIN) + "**）",
    "@S51B@": "（W2..W176 共一百七十五面实测 mu 稳定先例·单波跨键微）",
    "@S52@": "键 **" + SIG6 + "**=W176 合并池实测 " + SIG6 + "）",
    "@S53@": "A 档 full_sharpe_p95 与 W176 A 档 p95（**0.3118** 实测锚）差 **<0.05**（门标注法 W5..W176 先例",
    "@KLKEY@": "；键 W176 实测 K-lift **" + MIN + "0.0001**【line_merged@K385,120 **1.1845**·line_pre 1.1846·n_eff 790,905",
    "@WAVECLI@": "--wave 177/finalize --wave 177",
    "@EOB@": "engine_owner==bm-a 92 行注册",
    "@W136TO@": "W136..W176",
    "@OWNCHAIN@": "W157/W158/W159/W160/W161/W162/W163/W165/W166/W167/W168/W169/W170/W171/W172/W173/W174/W175/W176 最近自有波",
    "@W2TO@": "W2..W176",
    "@W1TO@": "W1..W176",
    "@PRC@": "results/_r841bma_w177_probe_receipt.json",
    "@PF@": "PERPETUAL_N1_W177_PREREG.md",
    "@B@": "PERPETUAL-N1-W177",
    "@WPN2@": "W178+ 投影",
    "@WN@": "W177",
    "@W@": "W176",
    "@SD@": "n1_w177",
    "@KOLD@": "385,120",
    "@N171@": "177",
    "@N170@": "176",
    "@N169@": "175",
}
missing = [t for (t, _v) in BACK176 if t not in BACK177]
assert not missing, missing

# --- 4. TOK177 = reversed BACK176 pairs + DRY full-file gate (E41) ----------
TOK177 = [(val, tok) for (tok, val) in BACK176]

src = blob.decode("utf-8")
out_t = src
for old, tok in TOK177:
    n = out_t.count(old)
    exp = EXPECT[tok]
    assert n == exp, "DRY TOK %s: count=%d expect=%d: %r" % (tok, n, exp, old[:70])
    out_t = out_t.replace(old, tok)
for tok, new in [(t, BACK177[t]) for (t, _v) in BACK176]:
    out_t = out_t.replace(tok, new)
resid = re.findall(r"@[A-Z0-9]+@", out_t)
assert not resid, "DRY unsubstituted tokens remain: %r" % (resid[:5],)
bad = [mm.group() for mm in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", out_t)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, "DRY malformed windows: %r" % (bad[:4],)
stale_wave = sorted(set(re.findall(r"波号 17[0-9]", out_t)))
assert stale_wave == ["波号 177"], "DRY stale bare wave numbers: %r" % (stale_wave,)
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w176", "n1_w177"], "DRY unexpected n1_w1xx forms: %r" % (low_forms,)
# post-wave stale sweep: this-wave identity must be consistent (@B@ token
# instances + the one inside the @TITLE@ composite = EXPECT+1)
assert out_t.count("PERPETUAL-N1-W177") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W177 freeze" not in out_t.replace("；W176=bm-a r834 freeze", ""), "unexpected W177-freeze text"
print("DRY GATE PASS: all %d TOK counts, residue-zero, malformed-window CLEAN, r754 two-form CLEAN" % len(TOK177))

# --- 5. emit the build script ----------------------------------------------
out = []
out.append('# -*- coding: utf-8 -*-')
out.append('"""r842 bm-a W177 per-wave prereg build: transforms the freeze-time W176')
out.append('prereg (git blob 15ec44ea6:research/PERPETUAL_N1_W176_PREREG.md, extracted')
out.append('byte-verbatim to results/_r842bma_w177_prereg_src.txt) into')
out.append('research/PERPETUAL_N1_W177_PREREG.md.')
out.append('')
out.append('Generated by results/_r842bma_w177_buildgen.py (TOK/BACK pairs AST-extracted')
out.append('from the r833 build script -- no exec of its time-locked live asserts;')
out.append('r773 pit law compliance inherited: token-first two-phase vmap,')
out.append('whole-string composites, numerals LAST; r735 substring-order law = BACK list')
out.append('order preserved (long composite values precede their short substrings)).')
out.append('r587 machine-derived facts (every displayed value read from on-disk receipts):')
out.append('  - pre-seat probe results/_r841bma_w177_probe_receipt.json rc0 ADMIT')
out.append('    (leg0 registry 174 rows tail W176 ordinal 167 / bma_ordinal 93 /')
out.append('    owner_rows 166 / bma_rows 92 / w176_ledger_head 793,105; leg1')
out.append('    A 404_204..406_203 hops=1 / B 406_204..406_403 hops=1 / naive A')
out.append('    404_004..406_003 refused at its own start by the registered W176 B')
out.append('    band 404_004..404_203 (staircase THIRTY-SEVENTH instance E36 per receipt')
out.append('    A_semantics; W176 sec5.5 anticipated 37th -- projection and receipt')
out.append('    ordinals MATCH, no divergence face this wave); naive B 404_204..404_403')
out.append('    lands inside own-A 404_204..406_203; leg2 conflicts 0; leg3 origin')
out.append('    vacancy True; leg4 W178+ projection A 406_204..408_203 hops=0 / B')
out.append('    406_404..406_603 hops=0, B inside A;)')
out.append('  - W176 finalize one-pass landed r839')
out.append('    (results/perpetual_faces/n1_w176_results.json: merged K=385,120,')
out.append('    mu=-0.092727 -> 4dp -0.0927, sigma=0.245060 6dp; w176-only mu=-0.0889')
out.append('    4dp; se_mu_at_k385120=0.000395; A p95=0.3118; k-lift line_merged 1.1845 /')
out.append('    line_pre 1.1846 / delta -0.0001 / n_eff 790,905; canon flip NOT')
out.append('    performed; mu_delta_w176_vs_w175ext=+0.000773);')
out.append('  - W176 sec7/sec8 settle backfill landed r839 one-pass window -- the W177')
out.append('    A-face cites the W176 sec8 succession face (on-disk text')
out.append('    "finalize=r839 窗收口" live-asserted);')
out.append('  - W176 freeze registered sha machine-derived = 15ec44ea6 (git log')
out.append('    origin/main --grep "W176 FREEZE"); W177 seat push sha machine-derived =')
out.append('    780a0cd30 (git log --diff-filter=A on the seat MSG inbox path); seat')
out.append('    self-ack archive move landed r841 window (processed/ path')
out.append('    live-asserted).')
out.append('')
out.append('Output written CRLF (on-disk convention, r370 law)."""')
out.append('import io')
out.append('import json')
out.append('import re')
out.append('import subprocess')
out.append('')
out.append('SRC = r"results\\_r842bma_w177_prereg_src.txt"')
out.append('OUT = r"research\\PERPETUAL_N1_W177_PREREG.md"')
out.append('')
out.append('')
out.append('# --- machine-derived facts (r587: read from on-disk receipts) ----------')
out.append('probe = json.load(open(r"results/_r841bma_w177_probe_receipt.json", encoding="utf-8"))')
out.append('assert probe["verdict"] == "ADMIT", probe["verdict"]')
out.append('assert probe["bands"] == {"A": "404204_406203", "B": "406204_406403"}, probe["bands"]')
out.append('leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]')
out.append('leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], probe["legs"]["leg4"]')
out.append('assert leg1["A"] == [404204, 406203] and leg1["B"] == [406204, 406403], leg1')
out.append('assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1')
out.append('assert leg1["ARITH_A"] == [404004, 406003], leg1["ARITH_A"]')
out.append('assert leg1["ARITH_B"] == [404204, 404403], leg1["ARITH_B"]')
out.append('assert leg1["B_naive_first_clean"] == [404204, 404403], leg1')
out.append('assert leg1["B_hop_chain"][0]["jump_to"] == 406204, leg1["B_hop_chain"]')
out.append('assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)')
out.append('assert leg0["rows"] == 174 and leg0["tail"] == "W176" and leg0["ordinal"] == 167 \\')
out.append('    and leg0["bma_ordinal"] == 93 and leg0["owner_rows"] == 166 \\')
out.append('    and leg0["bma_rows"] == 92 and leg0["w176_ledger_head"] == 793105, leg0')
out.append('assert leg4["W178p_A"] == "406204..408203" and leg4["W178p_B"] == "406404..406603", leg4')
out.append('assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4')
out.append('assert leg4["W178p_B_lands_inside_W178p_A"] is True, leg4')
out.append('assert "THIRTY-SEVENTH" in leg1["A_semantics"], leg1["A_semantics"]')
out.append('')
out.append('res = json.load(open(r"results/perpetual_faces/n1_w176_results.json", encoding="utf-8"))')
out.append('npc = res["null_pool_cumulative"]')
out.append('assert npc["merged"]["n_values"] == 385120, "W176 merged K drift"')
out.append('assert npc["pre_w176_cumulative"]["n_values"] == 382920, "pre-W176 K drift"')
out.append('kl = res["skill_line_v2_k_lift"]')
out.append('assert kl["line_merged_385120"] == 1.1845 and kl["line_pre_w176"] == 1.1846 \\')
out.append('    and kl["line_delta_k_lift"] == -0.0001 and kl["n_eff_held_equal"] == 790905, kl')
out.append('assert kl["canon_flip"].startswith("NOT performed"), kl')
out.append('assert npc["se_mu_at_k385120"] == 0.000395, "se_mu drift"')
out.append('assert npc["mu_delta_w176_vs_w175ext"] == 0.000773, "mu_delta drift"')
out.append('assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3118, "p95 drift"')
out.append('MU4 = "%.4f" % npc["merged"]["mu"]')
out.append('WONLY4 = "%.4f" % npc["w176_only"]["mu"]')
out.append('SIG6 = "%.6f" % npc["merged"]["sigma"]')
out.append('assert MU4 == "-0.0927" and WONLY4 == "-0.0889" and SIG6 == "0.245060", (MU4, WONLY4, SIG6)')
out.append('LEDG = "{:,}".format(leg0["w176_ledger_head"])')
out.append('KNEW = "{:,}".format(npc["merged"]["n_values"])')
out.append('assert LEDG == "793,105" and KNEW == "385,120", (LEDG, KNEW)')
out.append('KPROJ = "{:,}".format(385120 + 2200)')
out.append('LEDGPROJ = "{:,}".format(793105 + 2200)')
out.append('assert KPROJ == "387,320" and LEDGPROJ == "795,305", (KPROJ, LEDGPROJ)')
out.append('')
out.append('# W176 freeze sha + W177 seat push sha (live machine-derive, r587)')
out.append('_r = subprocess.run(["git", "log", "origin/main", "--format=%h",')
out.append('                     "--grep=W176 FREEZE", "-1"], capture_output=True, text=True)')
out.append('W176_SHA = _r.stdout.strip()')
out.append('assert W176_SHA == "15ec44ea6", W176_SHA')
out.append('_r2 = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",')
out.append('                     "--diff-filter=A",')
out.append('                     "--", "fleet/inbox/MSG-2026-10-07-2031-bma-w177-seat.md"],')
out.append('                    capture_output=True, text=True)')
out.append('SEAT_SHA = _r2.stdout.strip()')
out.append('assert SEAT_SHA == "780a0cd30", SEAT_SHA')
out.append('_r3 = subprocess.run(["git", "show",')
out.append('                     "origin/main:fleet/inbox/processed/MSG-2026-10-07-2031-bma-w177-seat.md"],')
out.append('                    capture_output=True)')
out.append('assert _r3.returncode == 0, "W177 seat MSG not on origin (r565 pre-freeze law)"')
out.append('assert "404_204..406_203" in _r3.stdout.decode("utf-8", "replace"), "seat band face drift"')
out.append('# W176 sec8 succession face settled r839 one-pass window -- A-face cites it')
out.append('w176p = io.open(r"research\\PERPETUAL_N1_W176_PREREG.md", encoding="utf-8", newline="").read()')
out.append('assert "mu_delta_w176_vs_w175ext" in w176p and "finalize=r839 窗收口" in w176p, \\')
out.append('    "W176 sec7/sec8 settle backfill missing (A-face citation would be false)"')
out.append('')
out.append('src = io.open(SRC, encoding="utf-8").read()')
out.append('assert src.count("\\r\\n") == 0, "source blob expected LF (git blob convention)"')
out.append('')
out.append('TOK177 = ' + repr(TOK177))
out.append('BACK177 = ' + repr([(t, BACK177[t]) for (t, _v) in BACK176]))
out.append('')
out.append('EXPECT = ' + repr(EXPECT))
out.append('')
out.append('out_t = src')
out.append('for old, tok in TOK177:')
out.append('    n = out_t.count(old)')
out.append('    exp = EXPECT[tok]')
out.append('    assert n == exp, f"TOK {tok}: count={n} expect={exp}: {old[:70]!r}"')
out.append('    out_t = out_t.replace(old, tok)')
out.append('for tok, new in BACK177:')
out.append('    out_t = out_t.replace(tok, new)')
out.append('resid = re.findall(r"@[A-Z0-9]+@", out_t)')
out.append('assert not resid, f"unsubstituted tokens remain: {resid[:5]}"')
out.append('')
out.append('# r773 leg-3 malformed-window scan (start>end dotted windows)')
out.append('bad = [mm.group() for mm in re.finditer(r"(\\d{3})_(\\d{3})\\.\\.(\\d{3})_(\\d{3})", out_t)')
out.append('       if int(mm.group(3)) < int(mm.group(1))]')
out.append('assert not bad, f"malformed windows: {bad[:4]}"')
out.append('')
out.append('# r754 two-form stale-face checklist (bare wave numbers + lowercase n1_w1xx)')
out.append('stale_wave = sorted(set(re.findall(r"波号 17[0-9]", out_t)))')
out.append('assert stale_wave == ["波号 177"], f"stale bare wave numbers: {stale_wave}"')
out.append('low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))')
out.append('assert low_forms == ["n1_w176", "n1_w177"], f"unexpected n1_w1xx forms: {low_forms}"')
out.append('assert out_t.count("PERPETUAL-N1-W177") == EXPECT["@B@"] + 1, "batch id count drift"')
out.append('assert "W177 freeze" not in out_t.replace("；W176=bm-a r834 freeze", ""), \\')
out.append('    "unexpected W177-freeze text"')
out.append('')
out.append('open(OUT, "wb").write(out_t.replace("\\n", "\\r\\n").encode("utf-8"))')
out.append('chk = io.open(OUT, encoding="utf-8", newline="").read()')
out.append('assert chk == out_t.replace("\\n", "\\r\\n"), "CRLF write roundtrip drift"')
out.append('assert chk.count("\\r\\n") >= 60, chk.count("\\r\\n")')
out.append('print(f"W177 prereg built: {OUT} bytes={len(chk.encode(\'utf-8\'))} crlf={chk.count(chr(13)+chr(10))}")')
out.append('print("post-transform asserts PASS (token counts, residue-zero, malformed-window CLEAN, r754 two-form CLEAN)")')

new_script = "\n".join(out) + "\n"
io.open(r"results\_r842bma_w177_prereg_build.py", "w", encoding="utf-8", newline="\n").write(new_script)
print("W177 build script written:", len(new_script), "bytes")
