# -*- coding: utf-8 -*-
"""r815 bm-a W171 per-wave prereg build: transforms the freeze-time W170
prereg (git blob cb7314d64:research/PERPETUAL_N1_W170_PREREG.md, extracted
byte-verbatim to results/_r815bma_w171_prereg_src.txt) into
research/PERPETUAL_N1_W171_PREREG.md.

r773 pit law compliance (token-first vmap, whole-string composites, no
bare-prefix partials, backstops run LAST); r587 machine-derived facts:
  - pre-seat probe results/_r814bma_w171_probe_receipt.json rc0 ADMIT
    (leg0 registry 168 rows tail W170 ordinal 161 / bma_ordinal 87 /
    owner_rows 160 / bma_rows 86 / w170_ledger_head 779,412; leg1
    A 391_004..393_003 hops=1 / B 393_004..393_203 hops=1 / naive A
    390_804..392_803 refused by the registered W170 B band 390_804..391_003
    (staircase THIRTIETH instance E36) / naive B 391_004..391_203 lands
    inside own-A; leg2 conflicts 0; leg3 origin vacancy True; leg4
    W172+ projection A 393_004..395_003 hops=0 / B 393_204..393_403
    hops=0, B inside A);
  - W170 finalize one-pass landed in the r813-labeled takeover window
    (results/perpetual_faces/n1_w170_results.json: merged K=371,920,
    mu=-0.092848, sigma=0.245153; w170-only mu=-0.092667; A p95=0.2931;
    se_mu_at_k371920=0.000402; k-lift line_merged 1.184 / line_pre
    1.1841 / delta -0.0001 / n_eff_held_equal 777,212);
  - W170 freeze registered sha machine-derived = cb7314d64 (git log
    origin/main --grep "W170 FREEZE", live this window);
  - W171 seat push sha machine-derived = 3290e586b (git log origin/main
    -- fleet/inbox/MSG-2026-10-07-0843-bma-w171-seat.md; the state file
    carried 1aab5daf7 = stale pre-rebase artifact, r812 honest-note
    precedent);
  - lineage constants disclosed (r795 precedent): the historical
    K-lift/se_mu chains + the single-state freeze-sha chain are
    tokenized WHOLE and never rolled (history is append-only); the
    W171+ -> W172+ projection faces are rebuilt from probe leg4.

Output written CRLF (on-disk W170 prereg convention, r370 EOL law)."""
import io
import json
import re
import subprocess

SRC = r"results\_r815bma_w171_prereg_src.txt"
OUT = r"research\PERPETUAL_N1_W171_PREREG.md"
CRLF = "\r\n"
M = "\u2212"  # U+2212 minus, the source convention


def u(part):
    return re.sub(r"(\d)(?=(\d{3})+$)", r"\1_", part)


def dotted(pair):
    if isinstance(pair, str):  # probe leg4 form: "393004..395003"
        a, b = pair.split("..")
        return f"{u(a)}..{u(b)}"
    return f"{u(str(pair[0]))}..{u(str(pair[1]))}"


# --- machine-derived facts (r587: read from on-disk receipts) ---------------
probe = json.load(open(r"results\_r814bma_w171_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "391004_393003", "B": "393004_393203"}, probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], probe["legs"]["leg4"]
assert leg1["A"] == [391004, 393003] and leg1["B"] == [393004, 393203], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [390804, 392803], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [391004, 391203], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [391004, 391203], leg1
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 168 and leg0["tail"] == "W170" and leg0["ordinal"] == 161 \
    and leg0["bma_ordinal"] == 87 and leg0["owner_rows"] == 160 \
    and leg0["bma_rows"] == 86 and leg0["w170_ledger_head"] == 779412, leg0
W172p_A = dotted(leg4["W172p_A"])
W172p_B = dotted(leg4["W172p_B"])
assert W172p_A == "393_004..395_003" and W172p_B == "393_204..393_403", (W172p_A, W172p_B)
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W172p_B_lands_inside_W172p_A"] is True, leg4

res = json.load(open(r"results/perpetual_faces/n1_w170_results.json", encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 371920, "W170 merged K drift"
assert npc["pre_w170_cumulative"]["n_values"] == 369720, "pre-W170 K drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_371920"] == 1.184 and kl["line_pre_w170"] == 1.1841 \
    and kl["line_delta_k_lift"] == -0.0001 and kl["n_eff_held_equal"] == 777212, kl
assert npc["se_mu_at_k371920"] == 0.000402, "se_mu drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.2931, "p95 drift"
MU4 = f"{npc['merged']['mu']:.4f}"
WONLY4 = f"{npc['w170_only']['mu']:.4f}"
SIG6 = f"{npc['merged']['sigma']:.6f}"
assert MU4 == "-0.0928" and WONLY4 == "-0.0927" and SIG6 == "0.245153", (MU4, WONLY4, SIG6)
LEDG = f"{leg0['w170_ledger_head']:,}"
KOLD = f"{npc['pre_w170_cumulative']['n_values']:,}"
KNEW = f"{npc['merged']['n_values']:,}"
assert LEDG == "779,412" and KOLD == "369,720" and KNEW == "371,920", (LEDG, KOLD, KNEW)
KPROJ = f"{371920 + 2200:,}"
LEDGPROJ = f"{779412 + 2200:,}"
assert KPROJ == "374,120" and LEDGPROJ == "781,612", (KPROJ, LEDGPROJ)

# W170 freeze sha + W171 seat push sha (live machine-derive, r587)
_r = subprocess.run(["git", "log", "origin/main", "--format=%h",
                     "--grep=W170 FREEZE", "-1"], capture_output=True, text=True)
W170_SHA = _r.stdout.strip()
assert W170_SHA == "cb7314d64", W170_SHA
_r2 = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                     "--", "fleet/inbox/MSG-2026-10-07-0843-bma-w171-seat.md"],
                    capture_output=True, text=True)
SEAT_SHA = _r2.stdout.strip()
assert SEAT_SHA == "3290e586b", SEAT_SHA
_r3 = subprocess.run(["git", "show", "origin/main:fleet/inbox/MSG-2026-10-07-0843-bma-w171-seat.md"],
                     capture_output=True)
assert _r3.returncode == 0, "W171 seat MSG not on origin (r565 pre-freeze law)"
assert "391_004..393_003" in _r3.stdout.decode("utf-8", "replace"), "seat band face drift"

src = io.open(SRC, encoding="utf-8", newline="").read()
assert src.count("\r\n") == 0, "source blob expected LF (git blob convention)"

# historical protections: extract the single-state chain + frozen value
# chains WHOLE (never rolled; append-only)
i0 = src.find("W118=bm-b r678 freeze")
i1 = src.find("（9c2271baf）")
assert 0 < i0 < i1, "single-state chain anchors missing"
CHAIN = src[i0:i1 + len("（9c2271baf）")]
assert CHAIN.endswith("W169=bm-a r811 freeze（9c2271baf）"), CHAIN[-60:]
CHAIN_NEW = CHAIN + f"；W170=bm-a r813 freeze（{W170_SHA}）"

KLTAIL = ("W161 **+0.0002**/W165 **−0.0001**/W166 **+0.0000**/W167 **+0.0000**"
          "/W168 **−0.0002**/W169 **+0.0001** 如实披露")
assert src.count(KLTAIL) == 1, "K-lift history tail not found"
KLTAIL_NEW = KLTAIL.replace(" 如实披露", "/W170 **−0.0001** 如实披露")
SEMTAIL = "→W165 0.000409→W165 **0.000408**→W166 **0.000407**→W167 **0.000406**→W168 **0.000404**→W169 **0.000403**】）"
assert src.count(SEMTAIL) == 1, "se_mu chain tail not found"
SEMTAIL_NEW = SEMTAIL.replace("】）", "→W170 **0.000402**】）")

A_BAND, B_BAND = dotted(leg1["A"]), dotted(leg1["B"])
NAIVE_A, NAIVE_B = dotted(leg1["ARITH_A"]), dotted(leg1["B_naive_first_clean"])
PRIOR_B = dotted([390804, 391003])   # registered W170 B band (probe leg1 refusal band)
A_SEED, B_SEED = u(str(leg1["A"][0])), u(str(leg1["B"][0]))
assert A_BAND == "391_004..393_003" and B_BAND == "393_004..393_203"
assert NAIVE_A == "390_804..392_803" and NAIVE_B == "391_004..391_203"
assert PRIOR_B == "390_804..391_003" and A_SEED == "391_004" and B_SEED == "393_004"

S55_OLD_LO = "5. **W171+ 投影（probe 机证·下波冻结方复核非转抄 r587 律）**"
s55_i = src.find(S55_OLD_LO)
assert s55_i > 0, "sec5.5 head not found"
s55_j = src.find("hop 链逐跳在 probe 回执。", s55_i)
assert s55_j > s55_i, "sec5.5 tail not found"
S55_OLD = src[s55_i:s55_j + len("hop 链逐跳在 probe 回执。")]
S55_NEW = (
    "5. **W172+ 投影（probe 机证·下波冻结方复核非转抄 r587 律）**：A first-clean "
    f"{W172p_A} **CLEAN**（hops=0）；B first-clean **{W172p_B} CLEAN**（hops=0）"
    "——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W172：W172 冻结方必须在"
    " post-W171 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；"
    f"**W171 B 带 {B_BAND} 注册后将拒 naive W172 A 窗**——W172 A 重 derive 同强制"
    "（越过 W171 B 带·阶梯 A-hops-prior-B 继承第三十一例）；verify at W172 prereg，"
    "hop 链逐跳在 probe 回执。"
)

TOK = [
    # --- historical protections FIRST (append-only, never rolled) ---
    (CHAIN, "@CHAIN@"),
    (KLTAIL, "@KLT@"),
    (SEMTAIL, "@SEMT@"),
    # --- title (whole line) ---
    ("# PERPETUAL-N1-W170 预注册 · N1 nulls-deepening 泵第 168 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 159+本候选=bm-a 第八十六枚自有波【r813】）",
     "@TITLE@"),
    # --- §0 line 1 seat/vacancy faces ---
    ("波号 170=注册表 W169 行后首个自由号", "@WAVEFREE@"),
    ("（r812 probe leg2/leg3 实跑）", "@VAC@"),
    ("本机席位公示=MSG-2026-10-07-0738-bma-w170-seat 已推 origin 0f00fa424 先于本冻结【r565 律·推送窗=r812 seat push 直接快进送达 0f00fa424（4-item payload=seat MSG+pre-seat probe 脚本+probe 回执+W169 finalize 产物=W146 同推先例）；self-ack inbox→processed 移位待 W170 finalize 收口窗",
     "@SEATPUB@"),
    ("（r812 把 gate 腿合并入 pre-seat probe·单窗 derive·dual-window parity N/A 诚实注记）",
     "@MERGE@"),
    # --- band paragraph (whole faces, receipt-derived) ---
    ("本波 **A-ext seed=388_804..390_803**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第二十九例**：A 面算术继续带 388_604..390_603 在其起点即被已注册 W169 B 带 388_604..388_803 **拒**（W169 席位 W170+ 投影+r810 gate leg3+W169 行投影散文（r811 冻结件）+W169 §8 承接面（r813 补账窗回填）四投影注记所预言）→ 诚实前向走 **1 hop** 落 **388_804..390_803**·**A base==前波 B 尾+1（388_803+1）机检关系**=**A-hops-prior-B 阶梯几何第二十九例（E36 卡）**·非轮转 r587 前向单调断言在走册）",
     "@AFACE@"),
    ("**B-ext exit seed=390_804..391_003**（**B 面=FIRST-CLEAN past own-wave A**：B 面算术继续带 388_804..389_003 在注册宇宙上 CLEAN 但**落在本波 A 窗内**（**同窗互斥面 leg2 律·W141 先例**：A 与 B 同一冻结 commit 双注册·互斥断言强制 B 越过本波 A 窗）→ B 带本波 A 窗保留走 **1 hop** 落 **390_804..391_003**·**B base==本波 A 尾+1（390_803+1）机检关系**·hop 链逐跳在 probe 回执；**W169 席位 W170+ 投影+r810 gate leg3+W169 行投影散文 re-derive-MANDATORY 注记三面兑现**：投影预言 W170 须在 post-W169 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）",
     "@BFACE@"),
    ("扫描面=pre-W170 全一百六十七行注册 N1 带表（表尾 W169 行·leg0 机证 167 行）", "@SCANFACE@"),
    # --- §0 anchor faces ---
    ("起稿窗实况：**W1..W169 N1 finalize 已全部落地**【W169 finalize one-pass bm-a r812·§7/§8 已回填（r813 补账窗收口·W159/W168 拖延窗先例同律·如实注记）】——净账本锚头 **777,212**（W169 finalize 落账【one-pass·K=369,720 合并池·voids LOWAMP-P1/P2】）",
     "@ANCHOR@"),
    ("累计 null 池=369,720+2,200（本波）=**371,920 投影**", "@POOL@"),
    ("本机 r812 席位 MSG-2026-10-07-0738-bma-w170-seat 已推 origin 0f00fa424（r812 seat push·r565 律）·probe W171+ 投影 A 390_804..392_803 / B 391_004..391_203",
     "@SEATSENT@"),
    ("（投影 B 落投影 A 窗内·W170 B 带 390_804..391_003 注册后将拒 naive W171 A 窗=阶梯 A-hops-prior-B 继承第三十例待 W171 注册宇宙复核）",
     "@PROJ0B@"),
    ("表尾后新首个自由号自领·r812 probe 单跑兑现注记（本窗冻结消费）", "@CLAIMLAW@"),
    ("T-2026-10-01-141 s1 引擎线第 160 波【bm-a 第八十六枚自有波【机面 derive：engine_owner==bm-a 行 85+本候选以 probe leg0 机证为准·同 W157/W158/W159/W160/W161/W162/W163/W165/W166/W167/W168/W169 最近自有波】。（波号=注册表 W169 行后首个自由号·单态零席位空档；中位公示 MSG-2026-10-07-0738-bma-w170-seat 先推 origin 0f00fa424 r565 律；lane-free；dept:研究）",
     "@ORDINALS@"),
    # --- §0.5 ---
    ("v2..W169 落地", "@V2W@"),
    # --- §3 method faces ---
    ("entry rng seed=**388_804+j**", "@ASEED@"),
    ("法典 §4 W170 行 A=388_804..390_803·**FIRST-CLEAN past prior-wave B 阶梯第二十九例**：算术续带 388_604..390_603 起点即被 W169 B 带拒→1 hop 落 388_804..390_803·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场",
     "@ASEEDPROSE@"),
    ("entry rng=**388_804+j**", "@BENTRY@"),
    ("exit rng=**390_804+j**（法典 §4 W170 行 B=390_804..391_003·**FIRST-CLEAN past own-wave A**：B 算术续带 388_804..389_003 在注册宇宙上 CLEAN 但落在本波 A 窗内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗→保留走落 390_804..391_003·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 gate 回执·与 W169 席位 W170+ 投影+r810 gate leg3+W169 行投影散文+W169 §8 承接面注记兑现收敛·ADMIT 回执在场）",
     "@BSEEDPROSE@"),
    ("r812 bm-a 带闸窗（pre-seat probe r812 单窗·gate 腿合并·parity N/A 诚实注记）", "@GATEW@"),
    # --- §4 / §5 ---
    ("file_name=\"results/perpetual_faces/n1_w170_results.json\"", "@FN@"),
    ("results/perpetual_faces/n1_w170_results.json", "@RFN@"),
    ("results/perpetual_faces/n1_w169_results.json", "@ODOLD@"),
    ("净账本锚头 777,212=W169 finalize 落账【one-pass·bm-a r812·§7/§8 已回填（r813 补账窗）】", "@S5ANCH@"),
    ("（W169 实测键 **−0.0928**·K=369,720 合并池·W169-only 实测 **−0.0870**）", "@S51@"),
    ("（W2..W169 共一百六十八面实测 mu 稳定先例·单波跨键微）", "@S51B@"),
    ("键 **0.245165**=W169 合并池实测 0.245165）", "@S52@"),
    ("A 档 full_sharpe_p95 与 W169 A 档 p95（**0.3289** 实测锚）差 **<0.05**（门标注法 W5..W169 先例", "@S53@"),
    ("；键 W169 实测 K-lift **+0.0001**【line_merged@K369,720 **1.1839**·line_pre 1.1838·n_eff 775,012", "@KLKEY@"),
    # --- §5.5 wholesale (rebuilt from probe leg4) ---
    (S55_OLD, "@S55@"),
    # --- §6 ---
    ("--wave 170/finalize --wave 170", "@WAVECLI@"),
    ("engine_owner==bm-a 85 行注册", "@EOB85@"),
    # --- living ranges (roll +1) ---
    ("W2..W169", "@W2TO@"),
    ("W1..W169", "@W1TO@"),
    ("W136..W169", "@W136TO@"),
    ("W166/W167/W168/W169 最近自有波", "@OWNCHAIN@"),
    # --- wave tokens (higher first) ---
    ("results/_r812bma_w170_probe_receipt.json", "@PRC@"),
    ("W171+ 投影", "@WPN@"),
    ("W170", "@W2@"),
    ("W169", "@W1@"),
    # --- numerics backstops (LAST) ---
    ("n1_w170", "@SD@"),
    ("369,720", "@KOLD@"),
    ("371,920", "@KPROJ@"),
    ("777,212", "@LEDG@"),
    ("170", "@N170@"),
    ("169", "@N169@"),
]

BACK = [
    ("@CHAIN@", CHAIN_NEW),
    ("@KLT@", KLTAIL_NEW),
    ("@SEMT@", SEMTAIL_NEW),
    ("@TITLE@", "# PERPETUAL-N1-W171 预注册 · N1 nulls-deepening 泵第 169 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 160+本候选=bm-a 第八十七枚自有波【r815】）"),
    ("@WAVEFREE@", "波号 171=注册表 W170 行后首个自由号"),
    ("@VAC@", "（r814 probe leg2/leg3 实跑）"),
    ("@SEATPUB@", f"本机席位公示=MSG-2026-10-07-0843-bma-w171-seat 已推 origin {SEAT_SHA} 先于本冻结【r565 律·推送窗=r814 seat push 直接快进送达 {SEAT_SHA}（4-item payload=seat MSG+pre-seat probe 脚本+probe 回执+W170 finalize 产物=W146 同推先例）；self-ack inbox→processed 移位待 W171 finalize 收口窗"),
    ("@MERGE@", "（r814 承袭 r812 gate-合并单回执结构·单窗 derive·dual-window parity N/A 诚实注记）"),
    ("@AFACE@", f"本波 **A-ext seed={A_BAND}**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第三十例**：A 面算术继续带 {NAIVE_A} 在其起点即被已注册 W170 B 带 {PRIOR_B} **拒**（W170 席位 W171+ 投影+r812 probe leg4+W170 行投影散文（r813 冻结件）+W170 §8 承接面（r813 收口窗回填）四投影注记所预言）→ 诚实前向走 **1 hop** 落 **{A_BAND}**·**A base==前波 B 尾+1（391_003+1）机检关系**=**A-hops-prior-B 阶梯几何第三十例（E36 卡）**·非轮转 r587 前向单调断言在走册）"),
    ("@BFACE@", f"**B-ext exit seed={B_BAND}**（**B 面=FIRST-CLEAN past own-wave A**：B 面算术继续带 {NAIVE_B} 在注册宇宙上 CLEAN 但**落在本波 A 窗内**（**同窗互斥面 leg2 律·W141 先例**：A 与 B 同一冻结 commit 双注册·互斥断言强制 B 越过本波 A 窗）→ B 带本波 A 窗保留走 **1 hop** 落 **{B_BAND}**·**B base==本波 A 尾+1（393_003+1）机检关系**·hop 链逐跳在 probe 回执；**W170 席位 W171+ 投影+r812 probe leg4+W170 行投影散文 re-derive-MANDATORY 注记三面兑现**：投影预言 W171 须在 post-W170 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）"),
    ("@SCANFACE@", "扫描面=pre-W171 全一百六十八行注册 N1 带表（表尾 W170 行·leg0 机证 168 行）"),
    ("@ANCHOR@", f"起稿窗实况：**W1..W170 N1 finalize 已全部落地**【W170 finalize one-pass bm-a r813 接管窗·§7/§8 已回填（W159/W168/W169 拖延窗先例同律·如实注记）】——净账本锚头 **{LEDG}**（W170 finalize 落账【one-pass·K={KNEW} 合并池·voids LOWAMP-P1/P2】）"),
    ("@POOL@", f"累计 null 池={KNEW}+2,200（本波）=**{KPROJ} 投影**"),
    ("@SEATSENT@", f"本机 r814 席位 MSG-2026-10-07-0843-bma-w171-seat 已推 origin {SEAT_SHA}（r814 seat push·r565 律）·probe W172+ 投影 A {W172p_A} / B {W172p_B}"),
    ("@PROJ0B@", f"（投影 B 落投影 A 窗内·W171 B 带 {B_BAND} 注册后将拒 naive W172 A 窗=阶梯 A-hops-prior-B 继承第三十一例待 W172 注册宇宙复核）"),
    ("@CLAIMLAW@", "表尾后新首个自由号自领·r814 probe 单跑兑现注记（本窗冻结消费）"),
    ("@ORDINALS@", "T-2026-10-01-141 s1 引擎线第 161 波【bm-a 第八十七枚自有波【机面 derive：engine_owner==bm-a 行 86+本候选以 probe leg0 机证为准·同 W157/W158/W159/W160/W161/W162/W163/W165/W166/W167/W168/W169/W170 最近自有波】。（波号=注册表 W170 行后首个自由号·单态零席位空档；中位公示 MSG-2026-10-07-0843-bma-w171-seat 先推 origin 3290e586b r565 律；lane-free；dept:研究）"),
    ("@V2W@", "v2..W170 落地"),
    ("@ASEED@", f"entry rng seed=**{A_SEED}+j**"),
    ("@ASEEDPROSE@", f"法典 §4 W171 行 A={A_BAND}·**FIRST-CLEAN past prior-wave B 阶梯第三十例**：算术续带 {NAIVE_A} 起点即被 W170 B 带拒→1 hop 落 {A_BAND}·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场"),
    ("@BENTRY@", f"entry rng=**{A_SEED}+j**"),
    ("@BSEEDPROSE@", f"exit rng=**{B_SEED}+j**（法典 §4 W171 行 B={B_BAND}·**FIRST-CLEAN past own-wave A**：B 算术续带 {NAIVE_B} 在注册宇宙上 CLEAN 但落在本波 A 窗内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗→保留走落 {B_BAND}·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·与 W170 席位 W171+ 投影+r812 probe leg4+W170 行投影散文+W170 §8 承接面注记兑现收敛·ADMIT 回执在场）"),
    ("@GATEW@", "r814 bm-a 带闸窗（pre-seat probe r814 单窗·gate 腿合并结构承袭 r812 先例·parity N/A 诚实注记）"),
    ("@FN@", "file_name=\"results/perpetual_faces/n1_w171_results.json\""),
    ("@RFN@", "results/perpetual_faces/n1_w171_results.json"),
    ("@ODOLD@", "results/perpetual_faces/n1_w170_results.json"),
    ("@S5ANCH@", f"净账本锚头 {LEDG}=W170 finalize 落账【one-pass·bm-a r813 接管窗·§7/§8 已回填】"),
    ("@S51@", f"（W170 实测键 **{M}{MU4[1:]}**·K={KNEW} 合并池·W170-only 实测 **{M}{WONLY4[1:]}**）"),
    ("@S51B@", "（W2..W170 共一百六十九面实测 mu 稳定先例·单波跨键微）"),
    ("@S52@", f"键 **{SIG6}**=W170 合并池实测 {SIG6}）"),
    ("@S53@", f"A 档 full_sharpe_p95 与 W170 A 档 p95（**0.2931** 实测锚）差 **<0.05**（门标注法 W5..W170 先例"),
    ("@KLKEY@", f"；键 W170 实测 K-lift **{M}0.0001**【line_merged@K{KNEW} **1.184**·line_pre 1.1841·n_eff 777,212"),
    ("@S55@", S55_NEW),
    ("@WAVECLI@", "--wave 171/finalize --wave 171"),
    ("@EOB85@", "engine_owner==bm-a 86 行注册"),
    ("@W2TO@", "W2..W170"),
    ("@W1TO@", "W1..W170"),
    ("@W136TO@", "W136..W170"),
    ("@OWNCHAIN@", "W166/W167/W168/W169/W170 最近自有波"),
    ("@WPN@", "W172+ 投影"),
    ("@PRC@", "results/_r814bma_w171_probe_receipt.json"),
    ("@W2@", "W171"),
    ("@W1@", "W170"),
    ("@SD@", "n1_w171"),
    ("@KOLD@", "371,920"),
    ("@KPROJ@", "374,120"),
    ("@LEDG@", "779,412"),
    ("@N170@", "171"),
    ("@N169@", "170"),
]

EXPECT = {  # token -> expected occurrence count in source (r745 needle law)
    "@CHAIN@": 1, "@KLT@": 1, "@SEMT@": 1, "@TITLE@": 1, "@WAVEFREE@": 1,
    "@VAC@": 1, "@SEATPUB@": 1, "@MERGE@": 1, "@AFACE@": 1, "@BFACE@": 1,
    "@SCANFACE@": 1, "@ANCHOR@": 1, "@POOL@": 1, "@SEATSENT@": 1,
    "@PROJ0B@": 1, "@CLAIMLAW@": 1, "@ORDINALS@": 1, "@V2W@": 1,
    "@ASEED@": 1, "@ASEEDPROSE@": 1, "@BENTRY@": 1, "@BSEEDPROSE@": 1,
    "@GATEW@": 1, "@FN@": 1, "@RFN@": 1, "@ODOLD@": 1, "@S5ANCH@": 1,
    "@S51@": 1, "@S51B@": 1, "@S52@": 1, "@S53@": 1, "@KLKEY@": 1,
    "@S55@": 1, "@WAVECLI@": 1, "@EOB85@": 1,
    "@W2TO@": 3, "@W1TO@": 3, "@W136TO@": 1, "@OWNCHAIN@": 1,
    "@PRC@": 1, "@WPN@": 1,
    "@SD@": 2, "@KOLD@": 2, "@KPROJ@": 0, "@LEDG@": 0,
    "@N170@": 0, "@N169@": 0, "@W2@": None, "@W1@": None,
}

out = src
for old, tok in TOK:
    n = out.count(old)
    exp = EXPECT[tok]
    if exp is None:
        assert n > 0, f"TOK {tok}: count={n} expect>0: {old[:70]!r}"
    else:
        assert n == exp, f"TOK {tok}: count={n} expect={exp}: {old[:70]!r}"
    out = out.replace(old, tok)
for tok, new in BACK:
    out = out.replace(tok, new)
assert "@" not in re.sub(r"[a-zA-Z0-9_@.:/\-]+@?", "", "") or True  # placeholder no-op
resid = re.findall(r"@[A-Z0-9]+@", out)
assert not resid, f"unsubstituted tokens remain: {resid[:5]}"

# --- post-transform integrity asserts -----------------------------------------
# r787 carve-out note: 390_804..391_003 (W170 B band), 390_804..392_803
# (naive-A continuation) and 391_004..391_203 (naive-B continuation) are
# NOT stale: they legitimately appear in the W171 prereg as the prior-wave
# refusal band and the naive-window citations.
for stale in ("388_604", "386_604", "388_804..390_803", "388_804..389_003",
              "0f00fa424", "MSG-2026-10-07-0738", "bma-w170-seat", "_r812bma",
              "775,012", "369,720", "371,920 投影", "第二十九例",
              "第 168 枚", "第八十六枚", "第 160 波", "rows 159", "行 159+",
              "1.1839", "1.1838", "0.245165", "0.3289", "0.0870",
              "r810 gate leg3", "r812 seat push", "本机 r812 席位",
              "W169 finalize one-pass bm-a r812", "净账本锚头 777,212",
              "n_eff 775,012"):    assert stale not in out, f"stale {stale!r} residue in W171 prereg"
for fresh in ("PERPETUAL-N1-W171", f"A-ext seed=391_004..393_003",
              f"B-ext exit seed=393_004..393_203",
              "阶梯第三十例", "阶梯几何第三十例", "阶梯 A-hops-prior-B 继承第三十一例",
              f"净账本锚头 **779,412**", f"累计 null 池=371,920+2,200（本波）=**374,120 投影**",
              f"A first-clean {W172p_A} **CLEAN**（hops=0）",
              f"B first-clean **{W172p_B} CLEAN**（hops=0）",
              f"W171 B 带 393_004..393_203 注册后将拒 naive W172 A 窗",
              "W1..W170 N1 finalize 已全部落地", "engine_owner 行 160+本候选",
              "bm-a 第八十七枚自有波", "第 169 枚", "第 161 波", "行 86+本候选",
              "【r815】", "MSG-2026-10-07-0843-bma-w171-seat",
              "results/_r814bma_w171_probe_receipt.json",
              "pre-W171 全一百六十八行注册 N1 带表（表尾 W170 行·leg0 机证 168 行）",
              "（W170 实测键 **−0.0928**·K=371,920 合并池·W170-only 实测 **−0.0927**）",
              "键 **0.245153**=W170 合并池实测 0.245153",
              "W170 A 档 p95（**0.2931** 实测锚）",
              "；键 W170 实测 K-lift **−0.0001**【line_merged@K371,920 **1.184**·line_pre 1.1841·n_eff 777,212",
              "→W168 **0.000404**→W169 **0.000403**→W170 **0.000402**】）",
              "/W169 **+0.0001**/W170 **−0.0001** 如实披露",
              f"；W170=bm-a r813 freeze（{W170_SHA}）",
              "v2..W170 落地", "W5..W170 先例", "W136..W170 先例",
              "n1_w171_results.json", "--wave 171/finalize --wave 171",
              "待 W171 finalize 窗", "§5.5 W172+ 投影承接",
              "r812 probe leg4", "r813 sec8" if False else "r812 probe leg4+W170 行投影散文"):
    assert fresh in out, f"fresh face missing: {fresh!r}"
# r773 leg-3 malformed-window scan (start>end dotted windows)
bad = [mm.group() for mm in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", out)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, f"malformed windows: {bad[:4]}"
# historical-chain never-rolled spot checks
assert "W118=bm-b r678 freeze（565e5b0b4）" in out
assert "W168=bm-a r809 freeze（8d8842b61）；W169=bm-a r811 freeze（9c2271baf）" in out
assert "W167 **0.000406**→W168 **0.000404**→W169 **0.000403**→W170 **0.000402**】）" in out
assert out.count("W169= bm-a") == 0

# --- write (CRLF, on-disk convention per r370 law) -----------------------------
open(OUT, "wb").write(out.replace("\n", "\r\n").encode("utf-8"))
chk = io.open(OUT, encoding="utf-8", newline="").read()
assert chk == out.replace("\n", "\r\n"), "CRLF write roundtrip drift"
assert chk.count("\r\n") == 63 or chk.count("\r\n") >= 60, chk.count("\r\n")
print(f"W171 prereg built: {OUT} bytes={len(chk.encode('utf-8'))} crlf={chk.count(chr(13)+chr(10))}")
print("post-transform integrity asserts PASS (stale-zero, fresh-present, "
      "malformed-window CLEAN, historical chains never rolled)")
