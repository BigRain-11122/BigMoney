# -*- coding: utf-8 -*-
"""r829 bm-a generator: builds results/_r829bma_w175_prereg_build.py by
exec'ing the truncated r825 W174 build script (all asserts, zero writes) to
extract the exact TOK174/BACK174/EXPECT pairs, then emitting the W175 build
with machine-read W175 facts (probe receipt + W174 finalize results, all read
from on-disk receipts this window per r587)."""
import io
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- 0. extract the freeze-time W174 prereg blob (LF, byte-verbatim) -------
_r = subprocess.run(
    ["git", "show", "db42a0d46:research/PERPETUAL_N1_W174_PREREG.md"],
    capture_output=True)
assert _r.returncode == 0, "W174 freeze-time blob not reachable"
blob = _r.stdout
assert b"\r\n" not in blob, "blob expected LF (git convention)"
io.open(r"results\_r829bma_w175_prereg_src.txt", "wb").write(blob)
print("W175 src extracted:", len(blob), "bytes (W174 freeze-time blob db42a0d46)")

# --- 1. exec truncated r825 build script: TOK174/BACK174/EXPECT ------------
src825 = io.open(r"results/_r825bma_w174_prereg_build.py", encoding="utf-8").read()
cut = src825.find("out_t = src")
assert 0 < cut, "cut marker (out_t = src) not found"
trunc = src825[:cut]
# W175 seat MSG archived inbox->processed (9bfe4a892, r828 closeout) before
# this build window -- the r825 script's own live re-assert paths already
# read the processed/ location for the W174 seat; the W173-era asserts all
# hold on disk; zero patches needed this lineage step (verified pre-window).
ns = {}
exec(compile(trunc, "r825_trunc", "exec"), ns)
BACK174 = ns["BACK174"]
EXPECT = ns["EXPECT"]
print("r825 BACK entries:", len(BACK174), "EXPECT entries:", len(EXPECT))
back_map = {tok: val for (tok, val) in BACK174}
assert len(back_map) == len(BACK174)

# --- 2. W175 facts (machine-read this window) ------------------------------
A_BAND = "399_804..401_803"
B_BAND = "401_804..402_003"
NAIVE_A = "399_604..401_603"
NAIVE_B = "399_804..400_003"
PRIOR_B = "399_604..399_803"     # registered W174 B band (refusal band)
A_SEED, B_SEED = "399_804", "401_804"
W176p_A, W176p_B = "401_804..403_803", "402_004..402_203"
W174_SHA = "db42a0d46"
SEAT_SHA = "25c414e95"
SEAT_MSG = "MSG-2026-10-07-1434-bma-w175-seat"

BACK175 = {
    "@CHAIN@": back_map["@CHAIN@"] + "；W174=bm-a r826 freeze（" + W174_SHA + "）",
    "@KLT@": back_map["@KLT@"].replace(" 如实披露", "/W174 **+0.0000** 如实披露"),
    "@SEMT@": back_map["@SEMT@"].replace("】）", "→W174 **0.000397**】）"),
    "@S55@": (
        "5. **W176+ 投影（probe 机证·下波冻结方复核非转抄 r587 律）**：A first-clean "
        + W176p_A + " **CLEAN**（hops=0）；B first-clean **" + W176p_B + " CLEAN**（hops=0）"
        "——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W176：W176 冻结方必须在"
        " post-W175 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；"
        "**W175 B 带 " + B_BAND + " 注册后将拒 naive W176 A 窗**——W176 A 重 derive 同强制"
        "（越过 W175 B 带·阶梯 A-hops-prior-B 继承第三十六例）；verify at W176 prereg，"
        "hop 链逐跳在 probe 回执。"
    ),
    "@TITLE@": "# PERPETUAL-N1-W175 预注册 · N1 nulls-deepening 泵第 173 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 164+本候选=bm-a 第九十一枚自有波【r829】）",
    "@WAVEFREE@": "波号 175=注册表 W174 行后首个自由号",
    "@VAC@": "（r828 probe leg2/leg3 实跑）",
    "@SEATPUB@": (
        "本机席位公示=" + SEAT_MSG + " 已推 origin " + SEAT_SHA
        + " 先于本冻结【r565 律·推送窗=r828 seat push 直接快进送达 " + SEAT_SHA
        + "（3-item payload=seat MSG+pre-seat probe 脚本+probe 回执=W146 同推先例·W174 finalize 产物已在 origin 自 r827 不再重送）；"
        "self-ack inbox→processed 移位已收档（r828 同窗）】"
    ),
    "@MERGE@": "（r828 承袭 r812/r820/r823 gate-合并单回执结构·单窗 derive·dual-window parity N/A 诚实注记）",
    "@AFACE@": (
        "本波 **A-ext seed=" + A_BAND + "**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第三十五例**："
        "A 面算术继续带 " + NAIVE_A + " 在其起点即被已注册 W174 B 带 " + PRIOR_B + " **拒**"
        "（W174 席位 W175+ 投影+r823 probe leg4+W174 行投影散文（r826 冻结件）+W174 §8 承接面注记所预言）"
        "→ 诚实前向走 **1 hop** 落 **" + A_BAND + "**·**A base==前波 B 尾+1（399_803+1）机检关系**"
        "=**A-hops-prior-B 阶梯几何第三十五例（E36 卡）**·非轮转 r587 前向单调断言在走册；"
        "序数面如实披露：W174 §5.5 投影预告第三十五例·r828 probe 回执 A_semantics 机读序数=THIRTY-FIFTH（第三十五例）·"
        "本件按回执序数面记载非转抄（r587）·投影与回执两读法恒同）"
    ),
    "@BFACE@": (
        "**B-ext exit seed=" + B_BAND + "**（**B 面=FIRST-CLEAN past own-wave A**："
        "B 面算术继续带 " + NAIVE_B + " 在注册宇宙上 CLEAN 但**落在本波 A 窗 " + A_BAND + " 内**"
        "（**同窗互斥面 leg2 律·W141 先例**：A 与 B 同一冻结 commit 双注册·互斥断言强制 B 越过本波 A 窗）"
        "→ B 带本波 A 窗保留走 **1 hop** 落 **" + B_BAND + "**·**B base==本波 A 尾+1（401_803+1）机检关系**·hop 链逐跳在 probe 回执；"
        "**W174 席位 W175+ 投影+r823 probe leg4+W174 行投影散文 re-derive-MANDATORY 注记三面兑现**："
        "投影预言 W175 须在 post-W174 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）"
    ),
    "@R250@": "R250：W175 带从未指派·测量面零结果可锁",
    "@SCANFACE@": "扫描面=pre-W175 全一百七十二行注册 N1 带表（表尾 W174 行·leg0 机证 172 行）",
    "@ANCHOR@": (
        "起稿窗实况：**W1..W174 N1 finalize 已全部落地**【W174 finalize one-pass bm-a r827 承袭收口窗"
        "·§7/§8 已回填（r826 one-pass 窗·dead-r826 estate 承袭·W159/W168/W169 拖延窗先例同律·如实注记）】"
        "——净账本锚头 **788,212**（W174 finalize 落账【one-pass·K=380,720 合并池】）"
    ),
    "@POOL@": "累计 null 池=380,720+2,200（本波）=**382,920 投影**",
    "@SEATSENT@": (
        "本机 r828 席位 " + SEAT_MSG + " 已推 origin " + SEAT_SHA
        + "（r828 seat push·r565 律）·probe W176+ 投影 A " + W176p_A + " / B " + W176p_B
        + " **naive-B-inside-naive-A re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·"
        "W175 B 带 " + B_BAND + " 注册后将拒 naive W176 A 窗=阶梯 A-hops-prior-B 继承第三十六例待 W176 注册宇宙复核）"
    ),
    "@CLAIMLAW@": "表尾后新首个自由号自领·r828 probe 单跑兑现注记（本窗冻结消费）",
    "@ORDINALS@": (
        "T-2026-10-01-141 s1 引擎线第 165 波【bm-a 第九十一枚自有波【机面 derive：engine_owner==bm-a 行 90+本候选以 probe leg0 机证为准·"
        "同 W157/W158/W159/W160/W161/W162/W163/W165/W166/W167/W168/W169/W170/W171/W172/W173/W174 最近自有波】。"
        "（波号=注册表 W174 行后首个自由号·单态零席位空档；中位公示 " + SEAT_MSG + " 先推 origin "
        + SEAT_SHA + " r565 律；lane-free；dept:研究）"
    ),
    "@V2W@": "v2..W174 落地",
    "@ASEED@": "entry rng seed=**" + A_SEED + "+j**",
    "@ASEEDPROSE@": (
        "法典 §4 W175 行 A=" + A_BAND + "·**FIRST-CLEAN past prior-wave B 阶梯第三十五例**："
        "算术续带 " + NAIVE_A + " 起点即被 W174 B 带拒→1 hop 落 " + A_BAND
        + "·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场"
    ),
    "@BENTRY@": "entry rng=**" + A_SEED + "+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）",
    "@BSEEDPROSE@": (
        "exit rng=**" + B_SEED + "+j**（法典 §4 W175 行 B=" + B_BAND
        + "·**FIRST-CLEAN past own-wave A**：B 算术续带 " + NAIVE_B
        + " 在注册宇宙上 CLEAN 但落在本波 A 窗 " + A_BAND + " 内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗"
        "→保留走落 " + B_BAND + "·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·"
        "与 W174 席位 W175+ 投影+r823 probe leg4+W174 行投影散文+W174 §8 承接面注记兑现收敛·ADMIT 回执在场）"
    ),
    "@GATEW@": "r828 bm-a 带闸窗（pre-seat probe r828 单窗·gate 腿合并结构承袭 r812/r820/r823 先例·parity N/A 诚实注记）",
    "@FN@": 'file_name="results/perpetual_faces/n1_w175_results.json"',
    "@RFN@": "results/perpetual_faces/n1_w175_results.json",
    "@ODOLD@": "results/perpetual_faces/n1_w174_results.json",
    "@S5ANCH@": "净账本锚头 788,212=W174 finalize 落账【one-pass·bm-a r827 承袭收口窗·§7/§8 已回填（r826 one-pass 窗）】",
    "@S51@": "（W174 实测键 **−0.0928**·K=380,720 合并池·W174-only 实测 **−0.0895**）",
    "@S51B@": "（W2..W174 共一百七十三面实测 mu 稳定先例·单波跨键微）",
    "@S52@": "键 **0.245114**=W174 合并池实测 0.245114）",
    "@S53@": "A 档 full_sharpe_p95 与 W174 A 档 p95（**0.3231** 实测锚）差 **<0.05**（门标注法 W5..W174 先例",
    "@KLKEY@": "；键 W174 实测 K-lift **+0.0000**【line_merged@K380,720 **1.1844**·line_pre 1.1844·n_eff 786,012",
    "@WAVECLI@": "--wave 175/finalize --wave 175",
    "@EOB@": "engine_owner==bm-a 90 行注册",
    "@W136TO@": "W136..W174",
    "@OWNCHAIN@": "W157/W158/W159/W160/W161/W162/W163/W165/W166/W167/W168/W169/W170/W171/W172/W173/W174 最近自有波",
    "@W2TO@": "W2..W174",
    "@W1TO@": "W1..W174",
    "@PRC@": "results/_r828bma_w175_probe_receipt.json",
    "@PF@": "PERPETUAL_N1_W175_PREREG.md",
    "@B@": "PERPETUAL-N1-W175",
    "@WPN2@": "W176+ 投影",
    "@WN@": "W175",
    "@W@": "W174",
    "@SD@": "n1_w175",
    "@KOLD@": "380,720",
    "@N171@": "175",
    "@N170@": "174",
    "@N169@": "173",
}
missing = [t for (t, _v) in BACK174 if t not in BACK175]
assert not missing, missing
# TOK' = reversed BACK174 pairs (old strings = what r825 wrote into the W174 prereg)
TOK175 = [(val, tok) for (tok, val) in BACK174]

out = []
out.append('# -*- coding: utf-8 -*-')
out.append('"""r829 bm-a W175 per-wave prereg build: transforms the freeze-time W174')
out.append('prereg (git blob db42a0d46:research/PERPETUAL_N1_W174_PREREG.md, extracted')
out.append('byte-verbatim to results/_r829bma_w175_prereg_src.txt) into')
out.append('research/PERPETUAL_N1_W175_PREREG.md.')
out.append('')
out.append('Generated by results/_r829bma_w175_buildgen.py (TOK pairs extracted by exec of')
out.append('the truncated r825 build script -- all r825 asserts re-passed live this window,')
out.append('zero writes; r773 pit law compliance inherited: token-first two-phase vmap,')
out.append('whole-string composites, numerals LAST; r735 substring-order law = BACK list')
out.append('order preserved (long composite values precede their short substrings)).')
out.append('r587 machine-derived facts (every displayed value read from on-disk receipts):')
out.append('  - pre-seat probe results/_r828bma_w175_probe_receipt.json rc0 ADMIT')
out.append('    (leg0 registry 172 rows tail W174 ordinal 165 / bma_ordinal 91 /')
out.append('    owner_rows 164 / bma_rows 90 / w174_ledger_head 788,212; leg1')
out.append('    A 399_804..401_803 hops=1 / B 401_804..402_003 hops=1 / naive A')
out.append('    399_604..401_603 refused at its own start by the registered W174 B')
out.append('    band 399_604..399_803 (staircase THIRTY-FIFTH instance E36 per receipt')
out.append('    A_semantics; W174 sec5.5 anticipated 35th -- projection and receipt')
out.append('    ordinals MATCH, no divergence face this wave); naive B 399_804..400_003')
out.append('    lands inside own-A 399_804..401_803; leg2 conflicts 0; leg3 origin')
out.append('    vacancy True; leg4 W176+ projection A 401_804..403_803 hops=0 / B')
out.append('    402_004..402_203 hops=0, B inside A;)')
out.append('  - W174 finalize one-pass landed r827 adoption closeout')
out.append('    (results/perpetual_faces/n1_w174_results.json: merged K=380,720,')
out.append('    mu=-0.092767 -> 4dp -0.0928, sigma=0.245114 6dp; w174-only mu=-0.0895')
out.append('    4dp; se_mu_at_k380720=0.000397; A p95=0.3231; k-lift line_merged 1.1844 /')
out.append('    line_pre 1.1844 / delta +0.0000 / n_eff 786,012; canon flip NOT')
out.append('    performed);')
out.append('  - W174 sec7/sec8 settle backfill landed r826 one-pass window (dead-r826')
out.append('    estate, delivered r827 adoption closeout) -- the W175 A-face cites the')
out.append('    W174 sec8 succession face as r826-one-pass-settle')
out.append('    (true at build time, mu_delta_w174_vs_w173ext=-0.005987 in the audit face);')
out.append('  - W174 freeze registered sha machine-derived = db42a0d46 (git log')
out.append('    origin/main --grep "W174 FREEZE");')
out.append('  - W175 seat push sha machine-derived = 25c414e95 (git log --diff-filter=A')
out.append('    -1 -- fleet/inbox/MSG-2026-10-07-1434-bma-w175-seat.md); seat MSG already')
out.append('    archived inbox->processed same round (9bfe4a892, r828 closeout) -- live')
out.append('    re-asserts read the processed/ path.')
out.append('')
out.append('Output written CRLF (on-disk convention, r370 law)."""')
out.append('import io')
out.append('import json')
out.append('import re')
out.append('import subprocess')
out.append('')
out.append('SRC = r"results\\_r829bma_w175_prereg_src.txt"')
out.append('OUT = r"research\\PERPETUAL_N1_W175_PREREG.md"')
out.append('M = "\\u2212"')
out.append('')
out.append('')
out.append('def u(part):')
out.append('    return re.sub(r"(\\d)(?=(\\d{3})+$)", r"\\1_", part)')
out.append('')
out.append('')
out.append('# --- machine-derived facts (r587: read from on-disk receipts) ---------------')
out.append('probe = json.load(open(r"results/_r828bma_w175_probe_receipt.json", encoding="utf-8"))')
out.append('assert probe["verdict"] == "ADMIT", probe["verdict"]')
out.append('assert probe["bands"] == {"A": "399804_401803", "B": "401804_402003"}, probe["bands"]')
out.append('leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]')
out.append('leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], probe["legs"]["leg4"]')
out.append('assert leg1["A"] == [399804, 401803] and leg1["B"] == [401804, 402003], leg1')
out.append('assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1')
out.append('assert leg1["ARITH_A"] == [399604, 401603], leg1["ARITH_A"]')
out.append('assert leg1["ARITH_B"] == [399804, 400003], leg1["ARITH_B"]')
out.append('assert leg1["B_naive_first_clean"] == [399804, 400003], leg1')
out.append('assert leg1["B_hop_chain"][0]["jump_to"] == 401804, leg1["B_hop_chain"]')
out.append('assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)')
out.append('assert leg0["rows"] == 172 and leg0["tail"] == "W174" and leg0["ordinal"] == 165 \\')
out.append('    and leg0["bma_ordinal"] == 91 and leg0["owner_rows"] == 164 \\')
out.append('    and leg0["bma_rows"] == 90 and leg0["w174_ledger_head"] == 788212, leg0')
out.append('W176p_A = "401_804..403_803"')
out.append('W176p_B = "402_004..402_203"')
out.append('assert leg4["W176p_A"] == "401804..403803" and leg4["W176p_B"] == "402004..402203", leg4')
out.append('assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4')
out.append('assert leg4["W176p_B_lands_inside_W176p_A"] is True, leg4')
out.append('assert "THIRTY-FIFTH" in leg1["A_semantics"], leg1["A_semantics"]')
out.append('')
out.append('res = json.load(open(r"results/perpetual_faces/n1_w174_results.json", encoding="utf-8"))')
out.append('npc = res["null_pool_cumulative"]')
out.append('assert npc["merged"]["n_values"] == 380720, "W174 merged K drift"')
out.append('assert npc["pre_w174_cumulative"]["n_values"] == 378520, "pre-W174 K drift"')
out.append('kl = res["skill_line_v2_k_lift"]')
out.append('assert kl["line_merged_380720"] == 1.1844 and kl["line_pre_w174"] == 1.1844 \\')
out.append('    and kl["line_delta_k_lift"] == 0.0 and kl["n_eff_held_equal"] == 786012, kl')
out.append('assert kl["canon_flip"].startswith("NOT performed"), kl')
out.append('assert npc["se_mu_at_k380720"] == 0.000397, "se_mu drift"')
out.append('assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3231, "p95 drift"')
out.append('MU4 = f"{npc[\'merged\'][\'mu\']:.4f}"')
out.append('WONLY4 = f"{npc[\'w174_only\'][\'mu\']:.4f}"')
out.append('SIG6 = f"{npc[\'merged\'][\'sigma\']:.6f}"')
out.append('assert MU4 == "-0.0928" and WONLY4 == "-0.0895" and SIG6 == "0.245114", (MU4, WONLY4, SIG6)')
out.append('LEDG = f"{leg0[\'w174_ledger_head\']:,}"')
out.append('KNEW = f"{npc[\'merged\'][\'n_values\']:,}"')
out.append('assert LEDG == "788,212" and KNEW == "380,720", (LEDG, KNEW)')
out.append('KPROJ = f"{380720 + 2200:,}"')
out.append('LEDGPROJ = f"{788212 + 2200:,}"')
out.append('assert KPROJ == "382,920" and LEDGPROJ == "790,412", (KPROJ, LEDGPROJ)')
out.append('')
out.append('# W174 freeze sha + W175 seat push sha (live machine-derive, r587)')
out.append('_r = subprocess.run(["git", "log", "origin/main", "--format=%h",')
out.append('                     "--grep=W174 FREEZE", "-1"], capture_output=True, text=True)')
out.append('W174_SHA = _r.stdout.strip()')
out.append('assert W174_SHA == "db42a0d46", W174_SHA')
out.append('_r2 = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",')
out.append('                     "--diff-filter=A",')
out.append('                     "--", "fleet/inbox/MSG-2026-10-07-1434-bma-w175-seat.md"],')
out.append('                    capture_output=True, text=True)')
out.append('SEAT_SHA = _r2.stdout.strip()')
out.append('assert SEAT_SHA == "25c414e95", SEAT_SHA')
out.append('_r3 = subprocess.run(["git", "show",')
out.append('                     "origin/main:fleet/inbox/processed/MSG-2026-10-07-1434-bma-w175-seat.md"],')
out.append('                    capture_output=True)')
out.append('assert _r3.returncode == 0, "W175 seat MSG not on origin (r565 pre-freeze law)"')
out.append('assert "399_804..401_803" in _r3.stdout.decode("utf-8", "replace"), "seat band face drift"')
out.append('# W174 sec8 succession face settled r826 one-pass window -- A-face cites it')
out.append('w174p = io.open(r"research\\PERPETUAL_N1_W174_PREREG.md", encoding="utf-8", newline="").read()')
out.append('assert "mu_delta_w174_vs_w173ext" in w174p and "r826 one-pass 窗" in w174p, \\')
out.append('    "W174 sec7/sec8 settle backfill missing (A-face citation would be false)"')
out.append('')
out.append('src = io.open(SRC, encoding="utf-8").read()')
out.append('assert src.count("\\r\\n") == 0, "source blob expected LF (git blob convention)"')
out.append('')
out.append('TOK175 = ' + repr(TOK175))
out.append('BACK175 = ' + repr([(t, BACK175[t]) for (t, _v) in BACK174]))
out.append('')
out.append('EXPECT = ' + repr(EXPECT))
out.append('')
out.append('out_t = src')
out.append('for old, tok in TOK175:')
out.append('    n = out_t.count(old)')
out.append('    exp = EXPECT[tok]')
out.append('    assert n == exp, f"TOK {tok}: count={n} expect={exp}: {old[:70]!r}"')
out.append('    out_t = out_t.replace(old, tok)')
out.append('for tok, new in BACK175:')
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
out.append('stale_wave = sorted(set(re.findall(r"\u6ce2\u53f7 17[0-9]", out_t)))')
out.append('assert stale_wave == ["\u6ce2\u53f7 175"], f"stale bare wave numbers: {stale_wave}"')
out.append('low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))')
out.append('assert low_forms == ["n1_w174", "n1_w175"], f"unexpected n1_w1xx forms: {low_forms}"')
out.append('')
out.append('open(OUT, "wb").write(out_t.replace("\\n", "\\r\\n").encode("utf-8"))')
out.append('chk = io.open(OUT, encoding="utf-8", newline="").read()')
out.append('assert chk == out_t.replace("\\n", "\\r\\n"), "CRLF write roundtrip drift"')
out.append('assert chk.count("\\r\\n") >= 60, chk.count("\\r\\n")')
out.append('print(f"W175 prereg built: {OUT} bytes={len(chk.encode(\'utf-8\'))} crlf={chk.count(chr(13)+chr(10))}")')
out.append('print("post-transform asserts PASS (token counts, residue-zero, malformed-window CLEAN, r754 two-form CLEAN)")')

new_script = "\n".join(out) + "\n"
io.open(r"results\_r829bma_w175_prereg_build.py", "w", encoding="utf-8", newline="\n").write(new_script)
print("W175 build script written:", len(new_script), "bytes")
