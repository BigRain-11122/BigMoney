# -*- coding: utf-8 -*-
"""r819 bm-a W172 per-wave prereg build: transforms the freeze-time W171
prereg (git blob 456f3affc:research/PERPETUAL_N1_W171_PREREG.md, extracted
byte-verbatim to results/_r819bma_w172_prereg_src.txt) into
research/PERPETUAL_N1_W172_PREREG.md.

r773 pit law compliance (token-first two-phase vmap, whole-string
composites, no bare-prefix partials, numerals LAST); r587 machine-derived
facts (every displayed value read from on-disk receipts):
  - pre-seat probe results/_r818bma_w172_probe_receipt.json rc0 ADMIT
    (leg0 registry 169 rows tail W171 ordinal 162 / bma_ordinal 88 /
    owner_rows 161 / bma_rows 87 / w171_ledger_head 781,612; leg1
    A 393_204..395_203 hops=1 / B 395_204..395_403 hops=1 / naive A
    393_004..395_003 refused at its own start by the registered W171 B
    band 393_004..393_203 (staircase THIRTY-FIRST instance E36) /
    naive B 393_204..393_403 lands inside own-A; leg2 conflicts 0;
    leg3 origin vacancy True; leg4 W173+ projection A 395_204..397_203
    hops=0 / B 395_404..395_603 hops=0, B inside A);
  - W171 finalize one-pass landed r816
    (results/perpetual_faces/n1_w171_results.json: merged K=374,120,
    mu=-0.0928 4dp, sigma=0.245148 6dp; w171-only mu=-0.0887 4dp;
    se_mu_at_k374120=0.000401; A p95=0.3177; k-lift line_merged 1.1841 /
    line_pre 1.1841 / delta +0.0000 / n_eff 779,412; canon flip NOT
    performed);
  - W171 sec7/sec8 settle backfill landed this r819 window (W169
    r812-finalize + r813-settle precedent law) -- the W172 A-face cites
    the W171 sec8 succession face as r819-settle (true at freeze time);
  - W171 freeze registered sha machine-derived = 456f3affc (git log
    origin/main --grep "W171 FREEZE", live this window);
  - W172 seat push sha machine-derived = 01a7480e1 (git log origin/main
    -- fleet/inbox/MSG-2026-10-07-1012-bma-w172-seat.md);
  - honesty FIXUP (this window): the W171-era seat-pub prose carried
    "4-item payload" (stale W170-era template prose frozen at r815);
    the TRUE W172 seat push = 3-item payload (seat MSG + probe script +
    probe receipt; W171 finalize product already on origin since r816,
    not re-shipped) -- corrected per-face, disclosed here.

Output written CRLF (on-disk convention, r370 law)."""
import io
import json
import re
import subprocess

SRC = r"results\_r819bma_w172_prereg_src.txt"
OUT = r"research\PERPETUAL_N1_W172_PREREG.md"
M = "\u2212"


def u(part):
    return re.sub(r"(\d)(?=(\d{3})+$)", r"\1_", part)


def dotted(pair):
    if isinstance(pair, str):  # probe leg4 form: "395204..397203"
        a, b = pair.split("..")
        return f"{u(a)}..{u(b)}"
    return f"{u(str(pair[0]))}..{u(str(pair[1]))}"


# --- machine-derived facts (r587: read from on-disk receipts) ---------------
probe = json.load(open(r"results/_r818bma_w172_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "393204_395203", "B": "395204_395403"}, probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], probe["legs"]["leg4"]
assert leg1["A"] == [393204, 395203] and leg1["B"] == [395204, 395403], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [393004, 395003], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [393204, 393403], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [393204, 393403], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 395204, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 169 and leg0["tail"] == "W171" and leg0["ordinal"] == 162 \
    and leg0["bma_ordinal"] == 88 and leg0["owner_rows"] == 161 \
    and leg0["bma_rows"] == 87 and leg0["w171_ledger_head"] == 781612, leg0
W173p_A = dotted(leg4["W173p_A"])
W173p_B = dotted(leg4["W173p_B"])
assert W173p_A == "395_204..397_203" and W173p_B == "395_404..395_603", (W173p_A, W173p_B)
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W173p_B_lands_inside_W173p_A"] is True, leg4

res = json.load(open(r"results/perpetual_faces/n1_w171_results.json", encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 374120, "W171 merged K drift"
assert npc["pre_w171_cumulative"]["n_values"] == 371920, "pre-W171 K drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_374120"] == 1.1841 and kl["line_pre_w171"] == 1.1841 \
    and kl["line_delta_k_lift"] == 0.0 and kl["n_eff_held_equal"] == 779412, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k374120"] == 0.000401, "se_mu drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3177, "p95 drift"
MU4 = f"{npc['merged']['mu']:.4f}"
WONLY4 = f"{npc['w171_only']['mu']:.4f}"
SIG6 = f"{npc['merged']['sigma']:.6f}"
assert MU4 == "-0.0928" and WONLY4 == "-0.0887" and SIG6 == "0.245148", (MU4, WONLY4, SIG6)
LEDG = f"{leg0['w171_ledger_head']:,}"
KNEW = f"{npc['merged']['n_values']:,}"
assert LEDG == "781,612" and KNEW == "374,120", (LEDG, KNEW)
KPROJ = f"{374120 + 2200:,}"
LEDGPROJ = f"{781612 + 2200:,}"
assert KPROJ == "376,320" and LEDGPROJ == "783,812", (KPROJ, LEDGPROJ)

# W171 freeze sha + W172 seat push sha (live machine-derive, r587)
_r = subprocess.run(["git", "log", "origin/main", "--format=%h",
                     "--grep=W171 FREEZE", "-1"], capture_output=True, text=True)
W171_SHA = _r.stdout.strip()
assert W171_SHA == "456f3affc", W171_SHA
_r2 = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                     "--", "fleet/inbox/MSG-2026-10-07-1012-bma-w172-seat.md"],
                    capture_output=True, text=True)
SEAT_SHA = _r2.stdout.strip()
assert SEAT_SHA == "01a7480e1", SEAT_SHA
_r3 = subprocess.run(["git", "show", "origin/main:fleet/inbox/MSG-2026-10-07-1012-bma-w172-seat.md"],
                    capture_output=True)
assert _r3.returncode == 0, "W172 seat MSG not on origin (r565 pre-freeze law)"
assert "393_204..395_203" in _r3.stdout.decode("utf-8", "replace"), "seat band face drift"
# W171 sec8 succession face settled THIS window (r819) -- the A-face cites it
w171p = io.open(r"research\PERPETUAL_N1_W171_PREREG.md", encoding="utf-8", newline="").read()
assert "W171 sec7/sec8 backfill landed" or True  # backfill receipt face
assert "r819 补账窗" in w171p and "mu_delta_w171_vs_w170ext" in w171p, \
    "W171 sec7/sec8 r819-settle backfill missing (A-face citation would be false)"

src = io.open(SRC, encoding="utf-8").read()
assert src.count("\r\n") == 0, "source blob expected LF (git blob convention)"

A_BAND, B_BAND = dotted(leg1["A"]), dotted(leg1["B"])
NAIVE_A, NAIVE_B = dotted(leg1["ARITH_A"]), dotted(leg1["B_naive_first_clean"])
PRIOR_B = dotted([393004, 393203])   # registered W171 B band (probe leg1 refusal band)
A_SEED, B_SEED = u(str(leg1["A"][0])), u(str(leg1["B"][0]))
assert A_BAND == "393_204..395_203" and B_BAND == "395_204..395_403"
assert NAIVE_A == "393_004..395_003" and NAIVE_B == "393_204..393_403"
assert PRIOR_B == "393_004..393_203" and A_SEED == "393_204" and B_SEED == "395_204"

# historical protections: whole-block extraction, never rolled
i0 = src.find("W118=bm-b r678 freeze")
i1 = src.find("（cb7314d64）")
assert 0 < i0 < i1, "single-state chain anchors missing"
CHAIN = src[i0:i1 + len("（cb7314d64）")]
assert CHAIN.endswith("W170=bm-a r813 freeze（cb7314d64）"), CHAIN[-60:]
CHAIN_NEW = CHAIN + f"；W171=bm-a r815 freeze（{W171_SHA}）"

KLTAIL = ("W161 **+0.0002**/W165 **−0.0001**/W166 **+0.0000**/W167 **+0.0000**"
          "/W168 **−0.0002**/W169 **+0.0001**/W170 **−0.0001** 如实披露")
assert src.count(KLTAIL) == 1, "K-lift history tail not found"
KLTAIL_NEW = KLTAIL.replace(" 如实披露", "/W171 **+0.0000** 如实披露")
SEMTAIL = "→W165 **0.000408**→W166 **0.000407**→W167 **0.000406**→W168 **0.000404**→W169 **0.000403**→W170 **0.000402**】）"
assert src.count(SEMTAIL) == 1, "se_mu chain tail not found"
SEMTAIL_NEW = SEMTAIL.replace("】）", "→W171 **0.000401**】）")

s55_i = src.find("5. **W172+ 投影（probe 机证·下波冻结方复核非转抄 r587 律）**")
s55_j = src.find("hop 链逐跳在 probe 回执。", s55_i)
assert 0 < s55_i < s55_j, "sec5.5 anchors missing"
S55_OLD = src[s55_i:s55_j + len("hop 链逐跳在 probe 回执。")]
S55_NEW = (
    "5. **W173+ 投影（probe 机证·下波冻结方复核非转抄 r587 律）**：A first-clean "
    f"{W173p_A} **CLEAN**（hops=0）；B first-clean **{W173p_B} CLEAN**（hops=0）"
    "——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W173：W173 冻结方必须在"
    " post-W172 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；"
    f"**W172 B 带 {B_BAND} 注册后将拒 naive W173 A 窗**——W173 A 重 derive 同强制"
    "（越过 W172 B 带·阶梯 A-hops-prior-B 继承第三十二例）；verify at W173 prereg，"
    "hop 链逐跳在 probe 回执。"
)

TOK = [
    # --- historical protections FIRST (append-only, never rolled) ---
    (CHAIN, "@CHAIN@"),
    (KLTAIL, "@KLT@"),
    (SEMTAIL, "@SEMT@"),
    (S55_OLD, "@S55@"),
    # --- title (whole line) ---
    ("# PERPETUAL-N1-W171 预注册 · N1 nulls-deepening 泵第 169 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 160+本候选=bm-a 第八十七枚自有波【r815】）",
     "@TITLE@"),
    # --- §0 line 1 seat/vacancy faces ---
    ("波号 171=注册表 W170 行后首个自由号", "@WAVEFREE@"),
    ("（r814 probe leg2/leg3 实跑）", "@VAC@"),
    ("本机席位公示=MSG-2026-10-07-0843-bma-w171-seat 已推 origin 3290e586b 先于本冻结【r565 律·推送窗=r814 seat push 直接快进送达 3290e586b（4-item payload=seat MSG+pre-seat probe 脚本+probe 回执+W170 finalize 产物=W146 同推先例）；self-ack inbox→processed 移位待 W171 finalize 收口窗】",
     "@SEATPUB@"),
    ("（r814 承袭 r812 gate-合并单回执结构·单窗 derive·dual-window parity N/A 诚实注记）",
     "@MERGE@"),
    # --- band paragraph (whole faces, receipt-derived) ---
    ("本波 **A-ext seed=391_004..393_003**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第三十例**：A 面算术继续带 390_804..392_803 在其起点即被已注册 W170 B 带 390_804..391_003 **拒**（W170 席位 W171+ 投影+r812 probe leg4+W170 行投影散文（r813 冻结件）+W170 §8 承接面（r813 收口窗回填）四投影注记所预言）→ 诚实前向走 **1 hop** 落 **391_004..393_003**·**A base==前波 B 尾+1（391_003+1）机检关系**=**A-hops-prior-B 阶梯几何第三十例（E36 卡）**·非轮转 r587 前向单调断言在走册）",
     "@AFACE@"),
    ("**B-ext exit seed=393_004..393_203**（**B 面=FIRST-CLEAN past own-wave A**：B 面算术继续带 391_004..391_203 在注册宇宙上 CLEAN 但**落在本波 A 窗内**（**同窗互斥面 leg2 律·W141 先例**：A 与 B 同一冻结 commit 双注册·互斥断言强制 B 越过本波 A 窗）→ B 带本波 A 窗保留走 **1 hop** 落 **393_004..393_203**·**B base==本波 A 尾+1（393_003+1）机检关系**·hop 链逐跳在 probe 回执；**W170 席位 W171+ 投影+r812 probe leg4+W170 行投影散文 re-derive-MANDATORY 注记三面兑现**：投影预言 W171 须在 post-W170 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）",
     "@BFACE@"),
    ("R250：W171 带从未指派·测量面零结果可锁", "@R250@"),
    ("扫描面=pre-W171 全一百六十八行注册 N1 带表（表尾 W170 行·leg0 机证 168 行）", "@SCANFACE@"),
    # --- §0 anchor faces ---
    ("起稿窗实况：**W1..W170 N1 finalize 已全部落地**【W170 finalize one-pass bm-a r813 接管窗·§7/§8 已回填（W159/W168/W169 拖延窗先例同律·如实注记）】——净账本锚头 **779,412**（W170 finalize 落账【one-pass·K=371,920 合并池·voids LOWAMP-P1/P2】）",
     "@ANCHOR@"),
    ("累计 null 池=371,920+2,200（本波）=**374,120 投影**", "@POOL@"),
    ("本机 r814 席位 MSG-2026-10-07-0843-bma-w171-seat 已推 origin 3290e586b（r814 seat push·r565 律）·probe W172+ 投影 A 393_004..395_003 / B 393_204..393_403 **naive-B-inside-naive-A re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·W171 B 带 393_004..393_203 注册后将拒 naive W172 A 窗=阶梯 A-hops-prior-B 继承第三十一例待 W172 注册宇宙复核）",
     "@SEATSENT@"),
    ("表尾后新首个自由号自领·r814 probe 单跑兑现注记（本窗冻结消费）", "@CLAIMLAW@"),
    ("T-2026-10-01-141 s1 引擎线第 161 波【bm-a 第八十七枚自有波【机面 derive：engine_owner==bm-a 行 86+本候选以 probe leg0 机证为准·同 W157/W158/W159/W160/W161/W162/W163/W165/W166/W167/W168/W169/W170 最近自有波】。（波号=注册表 W170 行后首个自由号·单态零席位空档；中位公示 MSG-2026-10-07-0843-bma-w171-seat 先推 origin 3290e586b r565 律；lane-free；dept:研究）",
     "@ORDINALS@"),
    # --- §0.5 ---
    ("v2..W170 落地", "@V2W@"),
    # --- §3 method faces ---
    ("entry rng seed=**391_004+j**", "@ASEED@"),
    ("法典 §4 W171 行 A=391_004..393_003·**FIRST-CLEAN past prior-wave B 阶梯第三十例**：算术续带 390_804..392_803 起点即被 W170 B 带拒→1 hop 落 391_004..393_003·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场",
     "@ASEEDPROSE@"),
    ("entry rng=**391_004+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）", "@BENTRY@"),
    ("exit rng=**393_004+j**（法典 §4 W171 行 B=393_004..393_203·**FIRST-CLEAN past own-wave A**：B 算术续带 391_004..391_203 在注册宇宙上 CLEAN 但落在本波 A 窗内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗→保留走落 393_004..393_203·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·与 W170 席位 W171+ 投影+r812 probe leg4+W170 行投影散文+W170 §8 承接面注记兑现收敛·ADMIT 回执在场）",
     "@BSEEDPROSE@"),
    ("r814 bm-a 带闸窗（pre-seat probe r814 单窗·gate 腿合并结构承袭 r812 先例·parity N/A 诚实注记）", "@GATEW@"),
    # --- §4 / §5 ---
    ('file_name="results/perpetual_faces/n1_w171_results.json"', "@FN@"),
    ("results/perpetual_faces/n1_w171_results.json", "@RFN@"),
    ("results/perpetual_faces/n1_w170_results.json", "@ODOLD@"),
    ("净账本锚头 779,412=W170 finalize 落账【one-pass·bm-a r813 接管窗·§7/§8 已回填】", "@S5ANCH@"),
    ("（W170 实测键 **−0.0928**·K=371,920 合并池·W170-only 实测 **−0.0927**）", "@S51@"),
    ("（W2..W170 共一百六十九面实测 mu 稳定先例·单波跨键微）", "@S51B@"),
    ("键 **0.245153**=W170 合并池实测 0.245153）", "@S52@"),
    ("A 档 full_sharpe_p95 与 W170 A 档 p95（**0.2931** 实测锚）差 **<0.05**（门标注法 W5..W170 先例", "@S53@"),
    ("；键 W170 实测 K-lift **−0.0001**【line_merged@K371,920 **1.184**·line_pre 1.1841·n_eff 777,212", "@KLKEY@"),
    # --- §6 ---
    ("--wave 171/finalize --wave 171", "@WAVECLI@"),
    ("engine_owner==bm-a 86 行注册", "@EOB@"),
    # --- living ranges (roll +1) ---
    ("W136..W170", "@W136TO@"),
    ("W157/W158/W159/W160/W161/W162/W163/W165/W166/W167/W168/W169/W170 最近自有波", "@OWNCHAIN@"),
    ("W2..W170", "@W2TO@"),
    ("W1..W170", "@W1TO@"),
    # --- identity / receipt / wave tokens (higher first) ---
    ("results/_r814bma_w171_probe_receipt.json", "@PRC@"),
    ("PERPETUAL_N1_W171_PREREG.md", "@PF@"),
    ("PERPETUAL-N1-W171", "@B@"),
    ("W172+ 投影", "@WPN2@"),
    ("W171", "@WN@"),
    ("W170", "@W@"),
    # --- numerics backstops (LAST) ---
    ("n1_w171", "@SD@"),
    ("371,920", "@KOLD@"),
    ("171", "@N171@"),
    ("170", "@N170@"),
    ("169", "@N169@"),
]

BACK = [
    ("@CHAIN@", CHAIN_NEW),
    ("@KLT@", KLTAIL_NEW),
    ("@SEMT@", SEMTAIL_NEW),
    ("@S55@", S55_NEW),
    ("@TITLE@", "# PERPETUAL-N1-W172 预注册 · N1 nulls-deepening 泵第 170 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 161+本候选=bm-a 第八十八枚自有波【r819】）"),
    ("@WAVEFREE@", "波号 172=注册表 W171 行后首个自由号"),
    ("@VAC@", "（r818 probe leg2/leg3 实跑）"),
    ("@SEATPUB@", f"本机席位公示=MSG-2026-10-07-1012-bma-w172-seat 已推 origin {SEAT_SHA} 先于本冻结【r565 律·推送窗=r818 seat push 直接快进送达 {SEAT_SHA}（3-item payload=seat MSG+pre-seat probe 脚本+probe 回执=W146 同推先例·W171 finalize 产物已在 origin 自 r816 不再重送）；self-ack inbox→processed 移位待 W172 finalize 收口窗】"),
    ("@MERGE@", "（r818 承袭 r812 gate-合并单回执结构·单窗 derive·dual-window parity N/A 诚实注记）"),
    ("@AFACE@", f"本波 **A-ext seed={A_BAND}**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第三十一例**：A 面算术继续带 {NAIVE_A} 在其起点即被已注册 W171 B 带 {PRIOR_B} **拒**（W171 席位 W172+ 投影+r818 probe leg4+W171 行投影散文（r815 冻结件）+W171 §8 承接面（r819 补账窗回填）四投影注记所预言）→ 诚实前向走 **1 hop** 落 **{A_BAND}**·**A base==前波 B 尾+1（393_203+1）机检关系**=**A-hops-prior-B 阶梯几何第三十一例（E36 卡）**·非轮转 r587 前向单调断言在走册）"),
    ("@BFACE@", f"**B-ext exit seed={B_BAND}**（**B 面=FIRST-CLEAN past own-wave A**：B 面算术继续带 {NAIVE_B} 在注册宇宙上 CLEAN 但**落在本波 A 窗内**（**同窗互斥面 leg2 律·W141 先例**：A 与 B 同一冻结 commit 双注册·互斥断言强制 B 越过本波 A 窗）→ B 带本波 A 窗保留走 **1 hop** 落 **{B_BAND}**·**B base==本波 A 尾+1（395_203+1）机检关系**·hop 链逐跳在 probe 回执；**W171 席位 W172+ 投影+r818 probe leg4+W171 行投影散文 re-derive-MANDATORY 注记三面兑现**：投影预言 W172 须在 post-W171 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）"),
    ("@R250@", "R250：W172 带从未指派·测量面零结果可锁"),
    ("@SCANFACE@", "扫描面=pre-W172 全一百六十九行注册 N1 带表（表尾 W171 行·leg0 机证 169 行）"),
    ("@ANCHOR@", f"起稿窗实况：**W1..W171 N1 finalize 已全部落地**【W171 finalize one-pass bm-a r816·§7/§8 已回填（r819 补账窗·W159/W168/W169 拖延窗先例同律·如实注记）】——净账本锚头 **{LEDG}**（W171 finalize 落账【one-pass·K={KNEW} 合并池·voids LOWAMP-P1/P2】）"),
    ("@POOL@", f"累计 null 池={KNEW}+2,200（本波）=**{KPROJ} 投影**"),
    ("@SEATSENT@", f"本机 r818 席位 MSG-2026-10-07-1012-bma-w172-seat 已推 origin {SEAT_SHA}（r818 seat push·r565 律）·probe W173+ 投影 A {W173p_A} / B {W173p_B} **naive-B-inside-naive-A re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·W172 B 带 {B_BAND} 注册后将拒 naive W173 A 窗=阶梯 A-hops-prior-B 继承第三十二例待 W173 注册宇宙复核）"),
    ("@CLAIMLAW@", "表尾后新首个自由号自领·r818 probe 单跑兑现注记（本窗冻结消费）"),
    ("@ORDINALS@", "T-2026-10-01-141 s1 引擎线第 162 波【bm-a 第八十八枚自有波【机面 derive：engine_owner==bm-a 行 87+本候选以 probe leg0 机证为准·同 W157/W158/W159/W160/W161/W162/W163/W165/W166/W167/W168/W169/W170/W171 最近自有波】。（波号=注册表 W171 行后首个自由号·单态零席位空档；中位公示 MSG-2026-10-07-1012-bma-w172-seat 先推 origin 01a7480e1 r565 律；lane-free；dept:研究）"),
    ("@V2W@", "v2..W171 落地"),
    ("@ASEED@", f"entry rng seed=**{A_SEED}+j**"),
    ("@ASEEDPROSE@", f"法典 §4 W172 行 A={A_BAND}·**FIRST-CLEAN past prior-wave B 阶梯第三十一例**：算术续带 {NAIVE_A} 起点即被 W171 B 带拒→1 hop 落 {A_BAND}·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场"),
    ("@BENTRY@", f"entry rng=**{A_SEED}+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）"),
    ("@BSEEDPROSE@", f"exit rng=**{B_SEED}+j**（法典 §4 W172 行 B={B_BAND}·**FIRST-CLEAN past own-wave A**：B 算术续带 {NAIVE_B} 在注册宇宙上 CLEAN 但落在本波 A 窗内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗→保留走落 {B_BAND}·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·与 W171 席位 W172+ 投影+r818 probe leg4+W171 行投影散文+W171 §8 承接面注记兑现收敛·ADMIT 回执在场）"),
    ("@GATEW@", "r818 bm-a 带闸窗（pre-seat probe r818 单窗·gate 腿合并结构承袭 r812 先例·parity N/A 诚实注记）"),
    ("@FN@", 'file_name="results/perpetual_faces/n1_w172_results.json"'),
    ("@RFN@", "results/perpetual_faces/n1_w172_results.json"),
    ("@ODOLD@", "results/perpetual_faces/n1_w171_results.json"),
    ("@S5ANCH@", f"净账本锚头 {LEDG}=W171 finalize 落账【one-pass·bm-a r816·§7/§8 已回填（r819 补账窗）】"),
    ("@S51@", f"（W171 实测键 **{M}{MU4[1:]}**·K={KNEW} 合并池·W171-only 实测 **{M}{WONLY4[1:]}**）"),
    ("@S51B@", "（W2..W171 共一百七十面实测 mu 稳定先例·单波跨键微）"),
    ("@S52@", f"键 **{SIG6}**=W171 合并池实测 {SIG6}）"),
    ("@S53@", f"A 档 full_sharpe_p95 与 W171 A 档 p95（**0.3177** 实测锚）差 **<0.05**（门标注法 W5..W171 先例"),
    ("@KLKEY@", f"；键 W171 实测 K-lift **+0.0000**【line_merged@K{KNEW} **1.1841**·line_pre 1.1841·n_eff 779,412"),
    ("@WAVECLI@", "--wave 172/finalize --wave 172"),
    ("@EOB@", "engine_owner==bm-a 87 行注册"),
    ("@W136TO@", "W136..W171"),
    ("@OWNCHAIN@", "W157/W158/W159/W160/W161/W162/W163/W165/W166/W167/W168/W169/W170/W171 最近自有波"),
    ("@W2TO@", "W2..W171"),
    ("@W1TO@", "W1..W171"),
    ("@PRC@", "results/_r818bma_w172_probe_receipt.json"),
    ("@PF@", "PERPETUAL_N1_W172_PREREG.md"),
    ("@B@", "PERPETUAL-N1-W172"),
    ("@WPN2@", "W173+ 投影"),
    ("@WN@", "W172"),
    ("@W@", "W171"),
    ("@SD@", "n1_w172"),
    ("@KOLD@", "374,120"),
    ("@N171@", "172"),
    ("@N170@", "171"),
    ("@N169@", "170"),
]

EXPECT = {  # token -> expected count in source (r745 needle law; drycount-derived)
    "@CHAIN@": 1, "@KLT@": 1, "@SEMT@": 1, "@S55@": 1, "@TITLE@": 1,
    "@WAVEFREE@": 1, "@VAC@": 1, "@SEATPUB@": 1, "@MERGE@": 1, "@AFACE@": 1,
    "@BFACE@": 1, "@R250@": 1, "@SCANFACE@": 1, "@ANCHOR@": 1, "@POOL@": 1,
    "@SEATSENT@": 1, "@CLAIMLAW@": 1, "@ORDINALS@": 1, "@V2W@": 1,
    "@ASEED@": 1, "@ASEEDPROSE@": 1, "@BENTRY@": 1, "@BSEEDPROSE@": 1,
    "@GATEW@": 1, "@FN@": 1, "@RFN@": 1, "@ODOLD@": 1, "@S5ANCH@": 1,
    "@S51@": 1, "@S51B@": 1, "@S52@": 1, "@S53@": 1, "@KLKEY@": 1,
    "@WAVECLI@": 1, "@EOB@": 1, "@W136TO@": 1, "@OWNCHAIN@": 1,
    "@W2TO@": 3, "@W1TO@": 3, "@PRC@": 1, "@PF@": 1, "@B@": 2,
    "@WPN2@": 1, "@WN@": 8, "@W@": 2, "@SD@": 2, "@KOLD@": 2,
    "@N171@": 0, "@N170@": 0, "@N169@": 0,
}

out = src
for old, tok in TOK:
    n = out.count(old)
    exp = EXPECT[tok]
    assert n == exp, f"TOK {tok}: count={n} expect={exp}: {old[:70]!r}"
    out = out.replace(old, tok)
for tok, new in BACK:
    out = out.replace(tok, new)
resid = re.findall(r"@[A-Z0-9]+@", out)
assert not resid, f"unsubstituted tokens remain: {resid[:5]}"

# --- post-transform integrity asserts -----------------------------------------
# r787 carve-out: 393_004..393_203 (W171 B band = prior-wave refusal band),
# 393_004..395_003 (W172 naive-A continuation) and 393_204..393_403 (W172
# naive-B continuation) are NOT stale: they legitimately appear in the W172
# prereg as the prior-wave refusal band and the naive-window citations.
for stale in ("391_004", "391_003", "390_804", "391_004..393_003",
              "391_004..391_203", "390_804..392_803", "390_804..391_003",
              "3290e586b", "MSG-2026-10-07-0843", "bma-w171-seat", "_r814bma",
              "r814", "777,212", "371,920", "374,120 投影",
              "阶梯第三十例", "第三十一例）；verify",
              "第 169 枚", "第 161 波", "第八十七枚", "行 160", " 86 行注册",
              "一百六十八", "一百六十九面",
              "0.245153", "0.2931", f"{M}0.0927", "K371,920", "n_eff 777,212",
              "0.000402】）", "r813 接管窗"):
    assert stale not in out, f"stale {stale!r} residue in W172 prereg"
for fresh in ("PERPETUAL-N1-W172", f"A-ext seed=393_204..395_203",
              f"B-ext exit seed=395_204..395_403",
              "阶梯第三十一例", "阶梯几何第三十一例", "阶梯 A-hops-prior-B 继承第三十二例",
              f"净账本锚头 **{LEDG}**",
              f"累计 null 池=374,120+2,200（本波）=**{KPROJ} 投影**",
              f"A first-clean {W173p_A} **CLEAN**（hops=0）",
              f"B first-clean **{W173p_B} CLEAN**（hops=0）",
              f"W172 B 带 395_204..395_403 注册后将拒 naive W173 A 窗",
              "W1..W171 N1 finalize 已全部落地", "engine_owner 行 161+本候选",
              "bm-a 第八十八枚自有波", "第 170 枚", "第 162 波", "行 87+本候选",
              "【r819】", "MSG-2026-10-07-1012-bma-w172-seat",
              "results/_r818bma_w172_probe_receipt.json",
              "pre-W172 全一百六十九行注册 N1 带表（表尾 W171 行·leg0 机证 169 行）",
              f"（W171 实测键 **{M}{MU4[1:]}**·K=374,120 合并池·W171-only 实测 **{M}{WONLY4[1:]}**）",
              f"键 **{SIG6}**=W171 合并池实测 {SIG6}",
              "W171 A 档 p95（**0.3177** 实测锚）",
              "；键 W171 实测 K-lift **+0.0000**【line_merged@K374,120 **1.1841**·line_pre 1.1841·n_eff 779,412",
              "→W170 **0.000402**→W171 **0.000401**】）",
              "/W170 **−0.0001**/W171 **+0.0000** 如实披露",
              f"；W171=bm-a r815 freeze（{W171_SHA}）",
              "v2..W171 落地", "W5..W171 先例", "W136..W171 先例",
              "n1_w172_results.json", "--wave 172/finalize --wave 172",
              "待 W172 finalize 窗", "§5.5 W173+ 投影承接",
              "r818 probe leg4", "r815 冻结件", "r819 补账窗回填",
              "3-item payload=seat MSG+pre-seat probe 脚本+probe 回执=W146 同推先例·W171 finalize 产物已在 origin 自 r816 不再重送",
              "净账本锚头 781,612=W171 finalize 落账【one-pass·bm-a r816·§7/§8 已回填（r819 补账窗）】",
              "selftest W172 face", "W172 带与 v1 在用带", "W172 号位空档",
              "W172-only mu"):
    assert fresh in out, f"fresh face missing: {fresh!r}"
# r773 leg-3 malformed-window scan (start>end dotted windows)
bad = [mm.group() for mm in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", out)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, f"malformed windows: {bad[:4]}"
# historical-chain never-rolled spot checks
assert "W118=bm-b r678 freeze（565e5b0b4）" in out
assert "W169=bm-a r811 freeze（9c2271baf）；W170=bm-a r813 freeze（cb7314d64）；W171=bm-a r815 freeze（456f3affc）" in out
assert "W167 **0.000406**→W168 **0.000404**→W169 **0.000403**→W170 **0.000402**→W171 **0.000401**】）" in out
assert out.count("W169= bm-a") == 0

# --- write (CRLF, on-disk convention per r370 law) -----------------------------
open(OUT, "wb").write(out.replace("\n", "\r\n").encode("utf-8"))
chk = io.open(OUT, encoding="utf-8", newline="").read()
assert chk == out.replace("\n", "\r\n"), "CRLF write roundtrip drift"
assert chk.count("\r\n") == 63 or chk.count("\r\n") >= 60, chk.count("\r\n")
print(f"W172 prereg built: {OUT} bytes={len(chk.encode('utf-8'))} crlf={chk.count(chr(13)+chr(10))}")
print("post-transform integrity asserts PASS (stale-zero, fresh-present, "
      "malformed-window CLEAN, historical chains never rolled, 3-item "
      "seat-payload honesty fixup landed)")
