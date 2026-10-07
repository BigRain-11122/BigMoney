# -*- coding: utf-8 -*-
"""r825 bm-a generator: builds results/_r825bma_w174_prereg_build.py by
exec'ing the truncated r821 W173 build script (all asserts, zero writes) to
extract the exact TOK173/BACK173/EXPECT pairs, then emitting the W174 build
with machine-read W174 facts (probe receipt + W173 finalize results, all read
from on-disk receipts this window per r587)."""
import io
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- 0. extract the freeze-time W173 prereg blob (LF, byte-verbatim) -------
_r = subprocess.run(
    ["git", "show", "04e95748a:research/PERPETUAL_N1_W173_PREREG.md"],
    capture_output=True)
assert _r.returncode == 0, "W173 freeze-time blob not reachable"
blob = _r.stdout
assert b"\r\n" not in blob, "blob expected LF (git convention)"
io.open(r"results\_r825bma_w174_prereg_src.txt", "wb").write(blob)
print("W174 src extracted:", len(blob), "bytes (W173 freeze-time blob 04e95748a)")

# --- 1. exec truncated r821 build script: TOK173/BACK173/EXPECT ------------
src821 = io.open(r"results/_r821bma_w173_prereg_build.py", encoding="utf-8").read()
cut = src821.find("out_t = src")
assert 0 < cut, "cut marker (out_t = src) not found"
trunc = src821[:cut]
# W173 seat MSG archived inbox->processed (cef586bd3) before W173 freeze --
# patch the two live re-assert paths; the historical 9cd8af3af fact is frozen
# inside the W173 prereg text and stays authoritative.
p1 = '"fleet/inbox/MSG-2026-10-07-1122-bma-w173-seat.md"'
p1n = '"fleet/inbox/processed/MSG-2026-10-07-1122-bma-w173-seat.md"'
assert trunc.count(p1) == 1, trunc.count(p1)
trunc = trunc.replace(p1, p1n)
p2 = '"origin/main:fleet/inbox/MSG-2026-10-07-1122-bma-w173-seat.md"'
p2n = '"origin/main:fleet/inbox/processed/MSG-2026-10-07-1122-bma-w173-seat.md"'
assert trunc.count(p2) == 1, trunc.count(p2)
trunc = trunc.replace(p2, p2n)
old_assert = 'assert SEAT_SHA == "9cd8af3af", SEAT_SHA'
assert old_assert in trunc
trunc = trunc.replace(
    old_assert,
    'assert SEAT_SHA in ("9cd8af3af", "cef586bd3"), SEAT_SHA\n'
    'SEAT_SHA = "9cd8af3af"  # r820-time historical value frozen in the W173 text')
ns = {}
exec(compile(trunc, "r821_trunc", "exec"), ns)
BACK173 = ns["BACK173"]
EXPECT = ns["EXPECT"]
print("r821 BACK entries:", len(BACK173), "EXPECT entries:", len(EXPECT))
back_map = {tok: val for (tok, val) in BACK173}
assert len(back_map) == len(BACK173)

# --- 2. W174 facts (machine-read this window) ------------------------------
A_BAND = "397_604..399_603"
B_BAND = "399_604..399_803"
NAIVE_A = "397_404..399_403"
NAIVE_B = "397_604..397_803"
PRIOR_B = "397_404..397_603"     # registered W173 B band (refusal band)
A_SEED, B_SEED = "397_604", "399_604"
W175p_A, W175p_B = "399_604..401_603", "399_804..400_003"
W173_SHA = "04e95748a"
SEAT_SHA = "9b0e1cb29"

BACK174 = {
    "@CHAIN@": back_map["@CHAIN@"] + "；W173=bm-a r822 freeze（" + W173_SHA + "）",
    "@KLT@": back_map["@KLT@"].replace(" 如实披露", "/W173 **+0.0000** 如实披露"),
    "@SEMT@": back_map["@SEMT@"].replace("】）", "→W173 **0.000398**】）"),
    "@S55@": (
        "5. **W175+ 投影（probe 机证·下波冻结方复核非转抄 r587 律）**：A first-clean "
        + W175p_A + " **CLEAN**（hops=0）；B first-clean **" + W175p_B + " CLEAN**（hops=0）"
        "——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W175：W175 冻结方必须在"
        " post-W174 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；"
        "**W174 B 带 " + B_BAND + " 注册后将拒 naive W175 A 窗**——W175 A 重 derive 同强制"
        "（越过 W174 B 带·阶梯 A-hops-prior-B 继承第三十五例）；verify at W175 prereg，"
        "hop 链逐跳在 probe 回执。"
    ),
    "@TITLE@": "# PERPETUAL-N1-W174 预注册 · N1 nulls-deepening 泵第 172 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 163+本候选=bm-a 第九十枚自有波【r825】）",
    "@WAVEFREE@": "波号 174=注册表 W173 行后首个自由号",
    "@VAC@": "（r823 probe leg2/leg3 实跑）",
    "@SEATPUB@": (
        "本机席位公示=MSG-2026-10-07-1247-bma-w174-seat 已推 origin " + SEAT_SHA
        + " 先于本冻结【r565 律·推送窗=r823 seat push 直接快进送达 " + SEAT_SHA
        + "（3-item payload=seat MSG+pre-seat probe 脚本+probe 回执=W146 同推先例·W173 finalize 产物已在 origin 自 r822 不再重送）；"
        "self-ack inbox→processed 移位已收档（r823 同窗）】"
    ),
    "@MERGE@": "（r823 承袭 r812/r820 gate-合并单回执结构·单窗 derive·dual-window parity N/A 诚实注记）",
    "@AFACE@": (
        "本波 **A-ext seed=" + A_BAND + "**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第三十四例**："
        "A 面算术继续带 " + NAIVE_A + " 在其起点即被已注册 W173 B 带 " + PRIOR_B + " **拒**"
        "（W173 席位 W174+ 投影+r823 probe leg4+W173 行投影散文（r822 冻结件）+W173 §8 承接面注记所预言）"
        "→ 诚实前向走 **1 hop** 落 **" + A_BAND + "**·**A base==前波 B 尾+1（397_603+1）机检关系**"
        "=**A-hops-prior-B 阶梯几何第三十四例（E36 卡）**·非轮转 r587 前向单调断言在走册；"
        "序数面如实披露：W173 §5.5 投影预告第三十四例·r823 probe 回执 A_semantics 机读序数=THIRTY-FOURTH（第三十四例）·"
        "本件按回执序数面记载非转抄（r587）·投影与回执两读法恒同）"
    ),
    "@BFACE@": (
        "**B-ext exit seed=" + B_BAND + "**（**B 面=FIRST-CLEAN past own-wave A**："
        "B 面算术继续带 " + NAIVE_B + " 在注册宇宙上 CLEAN 但**落在本波 A 窗 " + A_BAND + " 内**"
        "（**同窗互斥面 leg2 律·W141 先例**：A 与 B 同一冻结 commit 双注册·互斥断言强制 B 越过本波 A 窗）"
        "→ B 带本波 A 窗保留走 **1 hop** 落 **" + B_BAND + "**·**B base==本波 A 尾+1（399_603+1）机检关系**·hop 链逐跳在 probe 回执；"
        "**W173 席位 W174+ 投影+r823 probe leg4+W173 行投影散文 re-derive-MANDATORY 注记三面兑现**："
        "投影预言 W174 须在 post-W173 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）"
    ),
    "@R250@": "R250：W174 带从未指派·测量面零结果可锁",
    "@SCANFACE@": "扫描面=pre-W174 全一百七十一行注册 N1 带表（表尾 W173 行·leg0 机证 171 行）",
    "@ANCHOR@": (
        "起稿窗实况：**W1..W173 N1 finalize 已全部落地**【W173 finalize one-pass bm-a r823 接管收口窗"
        "·§7/§8 已回填（r823 接管收口窗·W159/W168/W169 拖延窗先例同律·如实注记）】"
        "——净账本锚头 **786,012**（W173 finalize 落账【one-pass·K=378,520 合并池】）"
    ),
    "@POOL@": "累计 null 池=378,520+2,200（本波）=**380,720 投影**",
    "@SEATSENT@": (
        "本机 r823 席位 MSG-2026-10-07-1247-bma-w174-seat 已推 origin " + SEAT_SHA
        + "（r823 seat push·r565 律）·probe W175+ 投影 A " + W175p_A + " / B " + W175p_B
        + " **naive-B-inside-naive-A re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·"
        "W174 B 带 " + B_BAND + " 注册后将拒 naive W175 A 窗=阶梯 A-hops-prior-B 继承第三十五例待 W175 注册宇宙复核）"
    ),
    "@CLAIMLAW@": "表尾后新首个自由号自领·r823 probe 单跑兑现注记（本窗冻结消费）",
    "@ORDINALS@": (
        "T-2026-10-01-141 s1 引擎线第 164 波【bm-a 第九十枚自有波【机面 derive：engine_owner==bm-a 行 89+本候选以 probe leg0 机证为准·"
        "同 W157/W158/W159/W160/W161/W162/W163/W165/W166/W167/W168/W169/W170/W171/W172/W173 最近自有波】。"
        "（波号=注册表 W173 行后首个自由号·单态零席位空档；中位公示 MSG-2026-10-07-1247-bma-w174-seat 先推 origin "
        + SEAT_SHA + " r565 律；lane-free；dept:研究）"
    ),
    "@V2W@": "v2..W173 落地",
    "@ASEED@": "entry rng seed=**" + A_SEED + "+j**",
    "@ASEEDPROSE@": (
        "法典 §4 W174 行 A=" + A_BAND + "·**FIRST-CLEAN past prior-wave B 阶梯第三十四例**："
        "算术续带 " + NAIVE_A + " 起点即被 W173 B 带拒→1 hop 落 " + A_BAND
        + "·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场"
    ),
    "@BENTRY@": "entry rng=**" + A_SEED + "+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）",
    "@BSEEDPROSE@": (
        "exit rng=**" + B_SEED + "+j**（法典 §4 W174 行 B=" + B_BAND
        + "·**FIRST-CLEAN past own-wave A**：B 算术续带 " + NAIVE_B
        + " 在注册宇宙上 CLEAN 但落在本波 A 窗 " + A_BAND + " 内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗"
        "→保留走落 " + B_BAND + "·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·"
        "与 W173 席位 W174+ 投影+r823 probe leg4+W173 行投影散文+W173 §8 承接面注记兑现收敛·ADMIT 回执在场）"
    ),
    "@GATEW@": "r823 bm-a 带闸窗（pre-seat probe r823 单窗·gate 腿合并结构承袭 r812/r820 先例·parity N/A 诚实注记）",
    "@FN@": 'file_name="results/perpetual_faces/n1_w174_results.json"',
    "@RFN@": "results/perpetual_faces/n1_w174_results.json",
    "@ODOLD@": "results/perpetual_faces/n1_w173_results.json",
    "@S5ANCH@": "净账本锚头 786,012=W173 finalize 落账【one-pass·bm-a r823 接管收口窗·§7/§8 已回填（r823 接管收口窗）】",
    "@S51@": "（W173 实测键 **\u22120.0928**·K=378,520 合并池·W173-only 实测 **\u22120.0835**）",
    "@S51B@": "（W2..W173 共一百七十二面实测 mu 稳定先例·单波跨键微）",
    "@S52@": "键 **0.245122**=W173 合并池实测 0.245122）",
    "@S53@": "A 档 full_sharpe_p95 与 W173 A 档 p95（**0.2986** 实测锚）差 **<0.05**（门标注法 W5..W173 先例",
    "@KLKEY@": "；键 W173 实测 K-lift **+0.0000**【line_merged@K378,520 **1.1843**·line_pre 1.1843·n_eff 783,812",
    "@WAVECLI@": "--wave 174/finalize --wave 174",
    "@EOB@": "engine_owner==bm-a 89 行注册",
    "@W136TO@": "W136..W173",
    "@OWNCHAIN@": "W157/W158/W159/W160/W161/W162/W163/W165/W166/W167/W168/W169/W170/W171/W172/W173 最近自有波",
    "@W2TO@": "W2..W173",
    "@W1TO@": "W1..W173",
    "@PRC@": "results/_r823bma_w174_probe_receipt.json",
    "@PF@": "PERPETUAL_N1_W174_PREREG.md",
    "@B@": "PERPETUAL-N1-W174",
    "@WPN2@": "W175+ 投影",
    "@WN@": "W174",
    "@W@": "W173",
    "@SD@": "n1_w174",
    "@KOLD@": "378,520",
    "@N171@": "174",
    "@N170@": "173",
    "@N169@": "172",
}
missing = [t for (t, _v) in BACK173 if t not in BACK174]
assert not missing, missing
# TOK' = reversed BACK173 pairs (old strings = what r821 wrote into the W173 prereg)
TOK174 = [(val, tok) for (tok, val) in BACK173]

out = []
out.append('# -*- coding: utf-8 -*-')
out.append('"""r825 bm-a W174 per-wave prereg build: transforms the freeze-time W173')
out.append('prereg (git blob 04e95748a:research/PERPETUAL_N1_W173_PREREG.md, extracted')
out.append('byte-verbatim to results/_r825bma_w174_prereg_src.txt) into')
out.append('research/PERPETUAL_N1_W174_PREREG.md.')
out.append('')
out.append('Generated by results/_r825bma_w174_buildgen.py (TOK pairs extracted by exec of')
out.append('the truncated r821 build script -- all r821 asserts re-passed live this window,')
out.append('zero writes; r773 pit law compliance inherited: token-first two-phase vmap,')
out.append('whole-string composites, numerals LAST; r735 substring-order law = BACK list')
out.append('order preserved (long composite values precede their short substrings)).')
out.append('r587 machine-derived facts (every displayed value read from on-disk receipts):')
out.append('  - pre-seat probe results/_r823bma_w174_probe_receipt.json rc0 ADMIT')
out.append('    (leg0 registry 171 rows tail W173 ordinal 164 / bma_ordinal 90 /')
out.append('    owner_rows 163 / bma_rows 89 / w173_ledger_head 786,012; leg1')
out.append('    A 397_604..399_603 hops=1 / B 399_604..399_803 hops=1 / naive A')
out.append('    397_404..399_403 refused at its own start by the registered W173 B')
out.append('    band 397_404..397_603 (staircase THIRTY-FOURTH instance E36 per receipt')
out.append('    A_semantics; W173 sec5.5 anticipated 34th -- projection and receipt')
out.append('    ordinals MATCH, no divergence face this wave); naive B 397_604..397_803')
out.append('    lands inside own-A 397_604..399_603; leg2 conflicts 0; leg3 origin')
out.append('    vacancy True; leg4 W175+ projection A 399_604..401_603 hops=0 / B')
out.append('    399_804..400_003 hops=0, B inside A;)')
out.append('  - W173 finalize one-pass landed r823 takeover closeout')
out.append('    (results/perpetual_faces/n1_w173_results.json: merged K=378,520,')
out.append('    mu=-0.092786 -> 4dp -0.0928, sigma=0.245122 6dp; w173-only mu=-0.0835')
out.append('    4dp; se_mu_at_k378520=0.000398; A p95=0.2986; k-lift line_merged 1.1843 /')
out.append('    line_pre 1.1843 / delta +0.0000 / n_eff 783,812; canon flip NOT')
out.append('    performed);')
out.append('  - W173 sec7/sec8 settle backfill landed r823 takeover closeout -- the')
out.append('    W174 A-face cites the W173 sec8 succession face as r823-settle')
out.append('    (true at build time, mu_delta_w173_vs_w172ext=+0.012103 in the audit face);')
out.append('  - W173 freeze registered sha machine-derived = 04e95748a (git log')
out.append('    origin/main --grep "W173 FREEZE");')
out.append('  - W174 seat push sha machine-derived = 9b0e1cb29 (git log --diff-filter=A')
out.append('    -1 -- fleet/inbox/MSG-2026-10-07-1247-bma-w174-seat.md); seat MSG already')
out.append('    archived inbox->processed same round (69c76e73b, r823 closeout) -- live')
out.append('    re-asserts read the processed/ path.')
out.append('')
out.append('Output written CRLF (on-disk convention, r370 law)."""')
out.append('import io')
out.append('import json')
out.append('import re')
out.append('import subprocess')
out.append('')
out.append('SRC = r"results\\_r825bma_w174_prereg_src.txt"')
out.append('OUT = r"research\\PERPETUAL_N1_W174_PREREG.md"')
out.append('M = "\\u2212"')
out.append('')
out.append('')
out.append('def u(part):')
out.append('    return re.sub(r"(\\d)(?=(\\d{3})+$)", r"\\1_", part)')
out.append('')
out.append('')
out.append('# --- machine-derived facts (r587: read from on-disk receipts) ---------------')
out.append('probe = json.load(open(r"results/_r823bma_w174_probe_receipt.json", encoding="utf-8"))')
out.append('assert probe["verdict"] == "ADMIT", probe["verdict"]')
out.append('assert probe["bands"] == {"A": "397604_399603", "B": "399604_399803"}, probe["bands"]')
out.append('leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]')
out.append('leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], probe["legs"]["leg4"]')
out.append('assert leg1["A"] == [397604, 399603] and leg1["B"] == [399604, 399803], leg1')
out.append('assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1')
out.append('assert leg1["ARITH_A"] == [397404, 399403], leg1["ARITH_A"]')
out.append('assert leg1["ARITH_B"] == [397604, 397803], leg1["ARITH_B"]')
out.append('assert leg1["B_naive_first_clean"] == [397604, 397803], leg1')
out.append('assert leg1["B_hop_chain"][0]["jump_to"] == 399604, leg1["B_hop_chain"]')
out.append('assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)')
out.append('assert leg0["rows"] == 171 and leg0["tail"] == "W173" and leg0["ordinal"] == 164 \\')
out.append('    and leg0["bma_ordinal"] == 90 and leg0["owner_rows"] == 163 \\')
out.append('    and leg0["bma_rows"] == 89 and leg0["w173_ledger_head"] == 786012, leg0')
out.append('W175p_A = "399_604..401_603"')
out.append('W175p_B = "399_804..400_003"')
out.append('assert leg4["W175p_A"] == "399604..401603" and leg4["W175p_B"] == "399804..400003", leg4')
out.append('assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4')
out.append('assert leg4["W175p_B_lands_inside_W175p_A"] is True, leg4')
out.append('assert "THIRTY-FOURTH" in leg1["A_semantics"], leg1["A_semantics"]')
out.append('')
out.append('res = json.load(open(r"results/perpetual_faces/n1_w173_results.json", encoding="utf-8"))')
out.append('npc = res["null_pool_cumulative"]')
out.append('assert npc["merged"]["n_values"] == 378520, "W173 merged K drift"')
out.append('assert npc["pre_w173_cumulative"]["n_values"] == 376320, "pre-W173 K drift"')
out.append('kl = res["skill_line_v2_k_lift"]')
out.append('assert kl["line_merged_378520"] == 1.1843 and kl["line_pre_w173"] == 1.1843 \\')
out.append('    and kl["line_delta_k_lift"] == 0.0 and kl["n_eff_held_equal"] == 783812, kl')
out.append('assert kl["canon_flip"].startswith("NOT performed"), kl')
out.append('assert npc["se_mu_at_k378520"] == 0.000398, "se_mu drift"')
out.append('assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.2986, "p95 drift"')
out.append('MU4 = f"{npc[\'merged\'][\'mu\']:.4f}"')
out.append('WONLY4 = f"{npc[\'w173_only\'][\'mu\']:.4f}"')
out.append('SIG6 = f"{npc[\'merged\'][\'sigma\']:.6f}"')
out.append('assert MU4 == "-0.0928" and WONLY4 == "-0.0835" and SIG6 == "0.245122", (MU4, WONLY4, SIG6)')
out.append('LEDG = f"{leg0[\'w173_ledger_head\']:,}"')
out.append('KNEW = f"{npc[\'merged\'][\'n_values\']:,}"')
out.append('assert LEDG == "786,012" and KNEW == "378,520", (LEDG, KNEW)')
out.append('KPROJ = f"{378520 + 2200:,}"')
out.append('LEDGPROJ = f"{786012 + 2200:,}"')
out.append('assert KPROJ == "380,720" and LEDGPROJ == "788,212", (KPROJ, LEDGPROJ)')
out.append('')
out.append('# W173 freeze sha + W174 seat push sha (live machine-derive, r587)')
out.append('_r = subprocess.run(["git", "log", "origin/main", "--format=%h",')
out.append('                     "--grep=W173 FREEZE", "-1"], capture_output=True, text=True)')
out.append('W173_SHA = _r.stdout.strip()')
out.append('assert W173_SHA == "04e95748a", W173_SHA')
out.append('_r2 = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",')
out.append('                     "--diff-filter=A",')
out.append('                     "--", "fleet/inbox/MSG-2026-10-07-1247-bma-w174-seat.md"],')
out.append('                    capture_output=True, text=True)')
out.append('SEAT_SHA = _r2.stdout.strip()')
out.append('assert SEAT_SHA == "9b0e1cb29", SEAT_SHA')
out.append('_r3 = subprocess.run(["git", "show",')
out.append('                     "origin/main:fleet/inbox/processed/MSG-2026-10-07-1247-bma-w174-seat.md"],')
out.append('                    capture_output=True)')
out.append('assert _r3.returncode == 0, "W174 seat MSG not on origin (r565 pre-freeze law)"')
out.append('assert "397_604..399_603" in _r3.stdout.decode("utf-8", "replace"), "seat band face drift"')
out.append('# W173 sec8 succession face settled r823 takeover closeout -- A-face cites it')
out.append('w173p = io.open(r"research\\PERPETUAL_N1_W173_PREREG.md", encoding="utf-8", newline="").read()')
out.append('assert "mu_delta_w173_vs_w172ext" in w173p and "接管收口窗" in w173p, \\')
out.append('    "W173 sec7/sec8 r823-settle backfill missing (A-face citation would be false)"')
out.append('')
out.append('src = io.open(SRC, encoding="utf-8").read()')
out.append('assert src.count("\\r\\n") == 0, "source blob expected LF (git blob convention)"')
out.append('')
out.append('TOK174 = ' + repr(TOK174))
out.append('BACK174 = ' + repr([(t, BACK174[t]) for (t, _v) in BACK173]))
out.append('')

out.append('EXPECT = ' + repr(EXPECT))
out.append('')
out.append('out_t = src')
out.append('for old, tok in TOK174:')
out.append('    n = out_t.count(old)')
out.append('    exp = EXPECT[tok]')
out.append('    assert n == exp, f"TOK {tok}: count={n} expect={exp}: {old[:70]!r}"')
out.append('    out_t = out_t.replace(old, tok)')
out.append('for tok, new in BACK174:')
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
out.append('assert stale_wave == ["\u6ce2\u53f7 174"], f"stale bare wave numbers: {stale_wave}"')
out.append('low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))')
out.append('assert low_forms == ["n1_w173", "n1_w174"], f"unexpected n1_w1xx forms: {low_forms}"')
out.append('')
out.append('open(OUT, "wb").write(out_t.replace("\\n", "\\r\\n").encode("utf-8"))')
out.append('chk = io.open(OUT, encoding="utf-8", newline="").read()')
out.append('assert chk == out_t.replace("\\n", "\\r\\n"), "CRLF write roundtrip drift"')
out.append('assert chk.count("\\r\\n") >= 60, chk.count("\\r\\n")')
out.append('print(f"W174 prereg built: {OUT} bytes={len(chk.encode(\'utf-8\'))} crlf={chk.count(chr(13)+chr(10))}")')
out.append('print("post-transform asserts PASS (token counts, residue-zero, malformed-window CLEAN, r754 two-form CLEAN)")')

new_script = "\n".join(out) + "\n"
io.open(r"results\_r825bma_w174_prereg_build.py", "w", encoding="utf-8", newline="\n").write(new_script)
print("W174 build script written:", len(new_script), "bytes")
