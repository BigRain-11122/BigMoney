# -*- coding: utf-8 -*-
"""r821 bm-a generator: builds results/_r821bma_w173_prereg_build.py by
exec'ing the truncated r819 build script (all asserts, zero writes) to
extract the exact TOK/BACK string pairs, then emitting the W173 build with
hand-composed W173 facts (machine-read this window from receipts)."""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

src819 = io.open(r"results/_r819bma_w172_prereg_build.py", encoding="utf-8").read()
cut = src819.find("# --- write (CRLF")
assert 0 < cut, "write marker not found"
trunc = src819[:cut]
# seat MSG was archived inbox->processed by e9219ce79 after r819 wrote the prereg;
# the historical 01a7480e1 fact is already frozen inside the BACK strings -- only
# this live re-assert needs the widened value to pass today.
trunc = trunc.replace(
    'assert SEAT_SHA == "01a7480e1", SEAT_SHA',
    'assert SEAT_SHA in ("01a7480e1", "e9219ce79"), SEAT_SHA\n'
    'SEAT_SHA = "01a7480e1"  # r819-time historical value frozen in the W172 prereg text')
# the W172 seat MSG has since been archived to fleet/inbox/processed/ -- check there
trunc = trunc.replace(
    '"origin/main:fleet/inbox/MSG-2026-10-07-1012-bma-w172-seat.md"],',
    '"origin/main:fleet/inbox/processed/MSG-2026-10-07-1012-bma-w172-seat.md"],')
ns = {}
exec(compile(trunc, "r819_trunc", "exec"), ns)
TOK819 = ns["TOK"]
BACK819 = ns["BACK"]
print("r819 TOK entries:", len(TOK819), "BACK entries:", len(BACK819))
back_map = {tok: val for tok, val in BACK819}
assert len(back_map) == len(BACK819)

# ---- W173 facts (machine-read this window) --------------------------------
A_BAND = "395_404..397_403"
B_BAND = "397_404..397_603"
NAIVE_A = "395_204..397_203"
NAIVE_B = "395_404..395_603"
PRIOR_B = "395_204..395_403"     # registered W172 B band (refusal band)
A_SEED, B_SEED = "395_404", "397_404"
W174p_A, W174p_B = "397_404..399_403", "397_604..397_803"
W172_SHA = "59fde9319"
SEAT_SHA = "9cd8af3af"

BACK173 = {
    "@CHAIN@": back_map["@CHAIN@"] + "；W172=bm-a r819 freeze（" + W172_SHA + "）",
    "@KLT@": back_map["@KLT@"].replace(" 如实披露", "/W172 **\u22120.0001** 如实披露"),
    "@SEMT@": back_map["@SEMT@"].replace("】）", "→W172 **0.000400**】）"),
    "@S55@": (
        "5. **W174+ 投影（probe 机证·下波冻结方复核非转抄 r587 律）**：A first-clean "
        + W174p_A + " **CLEAN**（hops=0）；B first-clean **" + W174p_B + " CLEAN**（hops=0）"
        "——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W174：W174 冻结方必须在"
        " post-W173 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；"
        "**W173 B 带 " + B_BAND + " 注册后将拒 naive W174 A 窗**——W174 A 重 derive 同强制"
        "（越过 W173 B 带·阶梯 A-hops-prior-B 继承第三十四例）；verify at W174 prereg，"
        "hop 链逐跳在 probe 回执。"
    ),
    "@TITLE@": "# PERPETUAL-N1-W173 预注册 · N1 nulls-deepening 泵第 171 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 162+本候选=bm-a 第八十九枚自有波【r821】）",
    "@WAVEFREE@": "波号 173=注册表 W172 行后首个自由号",
    "@VAC@": "（r820 probe leg2/leg3 实跑）",
    "@SEATPUB@": (
        "本机席位公示=MSG-2026-10-07-1122-bma-w173-seat 已推 origin " + SEAT_SHA
        + " 先于本冻结【r565 律·推送窗=r820 seat push 直接快进送达 " + SEAT_SHA
        + "（3-item payload=seat MSG+pre-seat probe 脚本+probe 回执=W146 同推先例·W172 finalize 产物已在 origin 自 r819 不再重送）；"
        "self-ack inbox→processed 移位待 W173 finalize 收口窗】"
    ),
    "@MERGE@": "（r820 承袭 r812 gate-合并单回执结构·单窗 derive·dual-window parity N/A 诚实注记）",
    "@AFACE@": (
        "本波 **A-ext seed=" + A_BAND + "**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第三十三例**："
        "A 面算术继续带 " + NAIVE_A + " 在其起点即被已注册 W172 B 带 " + PRIOR_B + " **拒**"
        "（W172 席位 W173+ 投影+r820 probe leg4+W172 行投影散文（r819 冻结件）+W172 §8 承接面（r819 接管收口窗回填）四投影注记所预言）"
        "→ 诚实前向走 **1 hop** 落 **" + A_BAND + "**·**A base==前波 B 尾+1（395_403+1）机检关系**"
        "=**A-hops-prior-B 阶梯几何第三十三例（E36 卡）**·非轮转 r587 前向单调断言在走册；"
        "序数面如实披露：W172 §5.5 投影预告第三十二例·r820 probe 回执 A_semantics 机读序数=THIRTY-THIRD（第三十三例）·"
        "本件按回执序数面记载非转抄（r587）·几何事实两读法恒同）"
    ),
    "@BFACE@": (
        "**B-ext exit seed=" + B_BAND + "**（**B 面=FIRST-CLEAN past own-wave A**："
        "B 面算术继续带 " + NAIVE_B + " 在注册宇宙上 CLEAN 但**落在本波 A 窗内**"
        "（**同窗互斥面 leg2 律·W141 先例**：A 与 B 同一冻结 commit 双注册·互斥断言强制 B 越过本波 A 窗）"
        "→ B 带本波 A 窗保留走 **1 hop** 落 **" + B_BAND + "**·**B base==本波 A 尾+1（397_403+1）机检关系**·hop 链逐跳在 probe 回执；"
        "**W172 席位 W173+ 投影+r820 probe leg4+W172 行投影散文 re-derive-MANDATORY 注记三面兑现**："
        "投影预言 W173 须在 post-W172 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）"
    ),
    "@R250@": "R250：W173 带从未指派·测量面零结果可锁",
    "@SCANFACE@": "扫描面=pre-W173 全一百七十行注册 N1 带表（表尾 W172 行·leg0 机证 170 行）",
    "@ANCHOR@": (
        "起稿窗实况：**W1..W172 N1 finalize 已全部落地**【W172 finalize one-pass bm-a r819 接管收口窗（25min wrapper 斩首收养先例同律）"
        "·§7/§8 已回填（r819 接管收口窗·W159/W168/W169 拖延窗先例同律·如实注记）】"
        "——净账本锚头 **783,812**（W172 finalize 落账【one-pass·K=376,320 合并池·voids LOWAMP-P1/P2】）"
    ),
    "@POOL@": "累计 null 池=376,320+2,200（本波）=**378,520 投影**",
    "@SEATSENT@": (
        "本机 r820 席位 MSG-2026-10-07-1122-bma-w173-seat 已推 origin " + SEAT_SHA
        + "（r820 seat push·r565 律）·probe W174+ 投影 A " + W174p_A + " / B " + W174p_B
        + " **naive-B-inside-naive-A re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·"
        "W173 B 带 " + B_BAND + " 注册后将拒 naive W174 A 窗=阶梯 A-hops-prior-B 继承第三十四例待 W174 注册宇宙复核）"
    ),
    "@CLAIMLAW@": "表尾后新首个自由号自领·r820 probe 单跑兑现注记（本窗冻结消费）",
    "@ORDINALS@": (
        "T-2026-10-01-141 s1 引擎线第 163 波【bm-a 第八十九枚自有波【机面 derive：engine_owner==bm-a 行 88+本候选以 probe leg0 机证为准·"
        "同 W157/W158/W159/W160/W161/W162/W163/W165/W166/W167/W168/W169/W170/W171/W172 最近自有波】。"
        "（波号=注册表 W172 行后首个自由号·单态零席位空档；中位公示 MSG-2026-10-07-1122-bma-w173-seat 先推 origin "
        + SEAT_SHA + " r565 律；lane-free；dept:研究）"
    ),
    "@V2W@": "v2..W172 落地",
    "@ASEED@": "entry rng seed=**" + A_SEED + "+j**",
    "@ASEEDPROSE@": (
        "法典 §4 W173 行 A=" + A_BAND + "·**FIRST-CLEAN past prior-wave B 阶梯第三十三例**："
        "算术续带 " + NAIVE_A + " 起点即被 W172 B 带拒→1 hop 落 " + A_BAND
        + "·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场"
    ),
    "@BENTRY@": "entry rng=**" + A_SEED + "+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）",
    "@BSEEDPROSE@": (
        "exit rng=**" + B_SEED + "+j**（法典 §4 W173 行 B=" + B_BAND
        + "·**FIRST-CLEAN past own-wave A**：B 算术续带 " + NAIVE_B
        + " 在注册宇宙上 CLEAN 但落在本波 A 窗内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗"
        "→保留走落 " + B_BAND + "·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·"
        "与 W172 席位 W173+ 投影+r820 probe leg4+W172 行投影散文+W172 §8 承接面注记兑现收敛·ADMIT 回执在场）"
    ),
    "@GATEW@": "r820 bm-a 带闸窗（pre-seat probe r820 单窗·gate 腿合并结构承袭 r812 先例·parity N/A 诚实注记）",
    "@FN@": 'file_name="results/perpetual_faces/n1_w173_results.json"',
    "@RFN@": "results/perpetual_faces/n1_w173_results.json",
    "@ODOLD@": "results/perpetual_faces/n1_w172_results.json",
    "@S5ANCH@": "净账本锚头 783,812=W172 finalize 落账【one-pass·bm-a r819 接管收口窗·§7/§8 已回填（r819 接管收口窗）】",
    "@S51@": "（W172 实测键 **\u22120.0928**·K=376,320 合并池·W172-only 实测 **\u22120.0956**）",
    "@S51B@": "（W2..W172 共一百七十一面实测 mu 稳定先例·单波跨键微）",
    "@S52@": "键 **0.245136**=W172 合并池实测 0.245136）",
    "@S53@": "A 档 full_sharpe_p95 与 W172 A 档 p95（**0.2996** 实测锚）差 **<0.05**（门标注法 W5..W172 先例",
    "@KLKEY@": "；键 W172 实测 K-lift **\u22120.0001**【line_merged@K376,320 **1.1842**·line_pre 1.1843·n_eff 781,612",
    "@WAVECLI@": "--wave 173/finalize --wave 173",
    "@EOB@": "engine_owner==bm-a 88 行注册",
    "@W136TO@": "W136..W172",
    "@OWNCHAIN@": "W157/W158/W159/W160/W161/W162/W163/W165/W166/W167/W168/W169/W170/W171/W172 最近自有波",
    "@W2TO@": "W2..W172",
    "@W1TO@": "W1..W172",
    "@PRC@": "results/_r820bma_w173_probe_receipt.json",
    "@PF@": "PERPETUAL_N1_W173_PREREG.md",
    "@B@": "PERPETUAL-N1-W173",
    "@WPN2@": "W174+ 投影",
    "@WN@": "W173",
    "@W@": "W172",
    "@SD@": "n1_w173",
    "@KOLD@": "376,320",
    "@N171@": "173",
    "@N170@": "172",
    "@N169@": "171",
}
missing = [t for (t, _v) in BACK819 if t not in BACK173]
assert not missing, missing
# TOK' = reversed BACK819 pairs (old strings = what r819 wrote into the W172 prereg)
TOK173 = [(val, tok) for (tok, val) in BACK819]

out = []
out.append('# -*- coding: utf-8 -*-')
out.append('"""r821 bm-a W173 per-wave prereg build: transforms the freeze-time W172')
out.append('prereg (git blob 59fde9319:research/PERPETUAL_N1_W172_PREREG.md, extracted')
out.append('byte-verbatim to results/_r821bma_w173_prereg_src.txt) into')
out.append('research/PERPETUAL_N1_W173_PREREG.md.')
out.append('')
out.append('Generated by results/_r821bma_w173_buildgen.py (TOK pairs extracted by exec of')
out.append('the truncated r819 build script -- all r819 asserts re-passed live this window,')
out.append('zero writes; r773 pit law compliance inherited: token-first two-phase vmap,')
out.append('whole-string composites, numerals LAST). r587 machine-derived facts (every')
out.append('displayed value read from on-disk receipts):')
out.append('  - pre-seat probe results/_r820bma_w173_probe_receipt.json rc0 ADMIT')
out.append('    (leg0 registry 170 rows tail W172 ordinal 163 / bma_ordinal 89 /')
out.append('    owner_rows 162 / bma_rows 88 / w172_ledger_head 783,812; leg1')
out.append('    A 395_404..397_403 hops=1 / B 397_404..397_603 hops=1 / naive A')
out.append('    395_204..397_203 refused at its own start by the registered W172 B')
out.append('    band 395_204..395_403 (staircase THIRTY-THIRD instance E36 per receipt')
out.append('    A_semantics; W172 prereg sec5.5 anticipated 32nd -- ordinal-face divergence')
out.append('    disclosed in-product, geometry facts identical); naive B 395_404..395_603')
out.append('    lands inside own-A; leg2 conflicts 0; leg3 origin vacancy True; leg4')
out.append('    W174+ projection A 397_404..399_403 hops=0 / B 397_604..397_803 hops=0,')
out.append('    B inside A;')
out.append('  - W172 finalize one-pass landed r819 takeover closeout')
out.append('    (results/perpetual_faces/n1_w172_results.json: merged K=376,320,')
out.append('    mu=-0.0928 4dp, sigma=0.245136 6dp; w172-only mu=-0.0956 4dp;')
out.append('    se_mu_at_k376320=0.000400; A p95=0.2996; k-lift line_merged 1.1842 /')
out.append('    line_pre 1.1843 / delta -0.0001 / n_eff 781,612; canon flip NOT')
out.append('    performed);')
out.append('  - W172 sec7/sec8 settle backfill landed r819 takeover closeout -- the')
out.append('    W173 A-face cites the W172 sec8 succession face as r819-接管收口窗-settle')
out.append('    (true at freeze time);')
out.append('  - W172 freeze registered sha machine-derived = 59fde9319 (git log')
out.append('    origin/main --grep "W172 FREEZE");')
out.append('  - W173 seat push sha machine-derived = 9cd8af3af (git log origin/main -1')
out.append('    -- fleet/inbox/MSG-2026-10-07-1122-bma-w173-seat.md); HONESTY NOTE: the')
out.append('    r820 closeout commit prose credited 014b4ede5 for the seat push, but the')
out.append('    path-scoped git history shows 9cd8af3af (r820 pre-seat push, 3-item')
out.append('    payload) introduced the seat MSG; 014b4ede5 is the churn-absorb checkpoint.')
out.append('    This build cites the path-derived sha and discloses the prose mismatch.')
out.append('')
out.append('Output written CRLF (on-disk convention, r370 law)."""')
out.append('import io')
out.append('import json')
out.append('import re')
out.append('import subprocess')
out.append('')
out.append('SRC = r"results\\_r821bma_w173_prereg_src.txt"')
out.append('OUT = r"research\\PERPETUAL_N1_W173_PREREG.md"')
out.append('M = "\\u2212"')
out.append('')
out.append('')
out.append('def u(part):')
out.append('    return re.sub(r"(\\d)(?=(\\d{3})+$)", r"\\1_", part)')
out.append('')
out.append('')
out.append('# --- machine-derived facts (r587: read from on-disk receipts) ---------------')
out.append('probe = json.load(open(r"results/_r820bma_w173_probe_receipt.json", encoding="utf-8"))')
out.append('assert probe["verdict"] == "ADMIT", probe["verdict"]')
out.append('assert probe["bands"] == {"A": "395404_397403", "B": "397404_397603"}, probe["bands"]')
out.append('leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]')
out.append('leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], probe["legs"]["leg4"]')
out.append('assert leg1["A"] == [395404, 397403] and leg1["B"] == [397404, 397603], leg1')
out.append('assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1')
out.append('assert leg1["ARITH_A"] == [395204, 397203], leg1["ARITH_A"]')
out.append('assert leg1["ARITH_B"] == [395404, 395603], leg1["ARITH_B"]')
out.append('assert leg1["B_naive_first_clean"] == [395404, 395603], leg1')
out.append('assert leg1["B_hop_chain"][0]["jump_to"] == 397404, leg1["B_hop_chain"]')
out.append('assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)')
out.append('assert leg0["rows"] == 170 and leg0["tail"] == "W172" and leg0["ordinal"] == 163 \\')
out.append('    and leg0["bma_ordinal"] == 89 and leg0["owner_rows"] == 162 \\')
out.append('    and leg0["bma_rows"] == 88 and leg0["w172_ledger_head"] == 783812, leg0')
out.append('W174p_A = "397_404..399_403"')
out.append('W174p_B = "397_604..397_803"')
out.append('assert leg4["W174p_A"] == "397404..399403" and leg4["W174p_B"] == "397604..397803", leg4')
out.append('assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4')
out.append('assert leg4["W174p_B_lands_inside_W174p_A"] is True, leg4')
out.append('assert "THIRTY-THIRD" in leg1["A_semantics"], leg1["A_semantics"]')
out.append('')
out.append('res = json.load(open(r"results/perpetual_faces/n1_w172_results.json", encoding="utf-8"))')
out.append('npc = res["null_pool_cumulative"]')
out.append('assert npc["merged"]["n_values"] == 376320, "W172 merged K drift"')
out.append('assert npc["pre_w172_cumulative"]["n_values"] == 374120, "pre-W172 K drift"')
out.append('kl = res["skill_line_v2_k_lift"]')
out.append('assert kl["line_merged_376320"] == 1.1842 and kl["line_pre_w172"] == 1.1843 \\')
out.append('    and kl["line_delta_k_lift"] == -0.0001 and kl["n_eff_held_equal"] == 781612, kl')
out.append('assert kl["canon_flip"].startswith("NOT performed"), kl')
out.append('assert npc["se_mu_at_k376320"] == 0.0004, "se_mu drift"')
out.append('assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.2996, "p95 drift"')
out.append('MU4 = f"{npc[\'merged\'][\'mu\']:.4f}"')
out.append('WONLY4 = f"{npc[\'w172_only\'][\'mu\']:.4f}"')
out.append('SIG6 = f"{npc[\'merged\'][\'sigma\']:.6f}"')
out.append('assert MU4 == "-0.0928" and WONLY4 == "-0.0956" and SIG6 == "0.245136", (MU4, WONLY4, SIG6)')
out.append('LEDG = f"{leg0[\'w172_ledger_head\']:,}"')
out.append('KNEW = f"{npc[\'merged\'][\'n_values\']:,}"')
out.append('assert LEDG == "783,812" and KNEW == "376,320", (LEDG, KNEW)')
out.append('KPROJ = f"{376320 + 2200:,}"')
out.append('LEDGPROJ = f"{783812 + 2200:,}"')
out.append('assert KPROJ == "378,520" and LEDGPROJ == "786,012", (KPROJ, LEDGPROJ)')
out.append('')
out.append('# W172 freeze sha + W173 seat push sha (live machine-derive, r587)')
out.append('_r = subprocess.run(["git", "log", "origin/main", "--format=%h",')
out.append('                     "--grep=W172 FREEZE", "-1"], capture_output=True, text=True)')
out.append('W172_SHA = _r.stdout.strip()')
out.append('assert W172_SHA == "59fde9319", W172_SHA')
out.append('_r2 = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",')
out.append('                     "--", "fleet/inbox/MSG-2026-10-07-1122-bma-w173-seat.md"],')
out.append('                    capture_output=True, text=True)')
out.append('SEAT_SHA = _r2.stdout.strip()')
out.append('assert SEAT_SHA == "9cd8af3af", SEAT_SHA')
out.append('_r3 = subprocess.run(["git", "show", "origin/main:fleet/inbox/MSG-2026-10-07-1122-bma-w173-seat.md"],')
out.append('                    capture_output=True)')
out.append('assert _r3.returncode == 0, "W173 seat MSG not on origin (r565 pre-freeze law)"')
out.append('assert "395_404..397_403" in _r3.stdout.decode("utf-8", "replace"), "seat band face drift"')
out.append('# W172 sec8 succession face settled r819 takeover closeout -- A-face cites it')
out.append('w172p = io.open(r"research\\PERPETUAL_N1_W172_PREREG.md", encoding="utf-8", newline="").read()')
out.append('assert "mu_delta_w172_vs_w171ext" in w172p and "接管收口窗" in w172p, \\')
out.append('    "W172 sec7/sec8 r819-settle backfill missing (A-face citation would be false)"')
out.append('')
out.append('src = io.open(SRC, encoding="utf-8").read()')
out.append('assert src.count("\\r\\n") == 0, "source blob expected LF (git blob convention)"')
out.append('')
out.append('TOK173 = ' + repr(TOK173).replace("\\n", "\\n"))
out.append('BACK173 = ' + repr([(t, BACK173[t]) for (t, _v) in BACK819]).replace("\\n", "\\n"))
out.append('')

EXPECT = ns["EXPECT"]
out.append('EXPECT = ' + repr(EXPECT))
out.append('')
out.append('out_t = src')
out.append('for old, tok in TOK173:')
out.append('    n = out_t.count(old)')
out.append('    exp = EXPECT[tok]')
out.append('    assert n == exp, f"TOK {tok}: count={n} expect={exp}: {old[:70]!r}"')
out.append('    out_t = out_t.replace(old, tok)')
out.append('for tok, new in BACK173:')
out.append('    out_t = out_t.replace(tok, new)')
out.append('resid = re.findall(r"@[A-Z0-9]+@", out_t)')
out.append('assert not resid, f"unsubstituted tokens remain: {resid[:5]}"')
out.append('')
out.append('# r773 leg-3 malformed-window scan (start>end dotted windows)')
out.append('bad = [mm.group() for mm in re.finditer(r"(\\d{3})_(\\d{3})\\.\\.(\\d{3})_(\\d{3})", out_t)')
out.append('       if int(mm.group(3)) < int(mm.group(1))]')
out.append('assert not bad, f"malformed windows: {bad[:4]}"')
out.append('')
out.append('open(OUT, "wb").write(out_t.replace("\\n", "\\r\\n").encode("utf-8"))')
out.append('chk = io.open(OUT, encoding="utf-8", newline="").read()')
out.append('assert chk == out_t.replace("\\n", "\\r\\n"), "CRLF write roundtrip drift"')
out.append('assert chk.count("\\r\\n") >= 60, chk.count("\\r\\n")')
out.append('print(f"W173 prereg built: {OUT} bytes={len(chk.encode(\'utf-8\'))} crlf={chk.count(chr(13)+chr(10))}")')
out.append('print("post-transform asserts PASS (token counts, residue-zero, malformed-window CLEAN)")')

new_script = "\n".join(out) + "\n"
io.open(r"results\_r821bma_w173_prereg_build.py", "w", encoding="utf-8", newline="\n").write(new_script)
print("W173 build script written:", len(new_script), "bytes")
