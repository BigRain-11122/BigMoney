# -*- coding: utf-8 -*-
"""r807 bm-a W168 prereg xform: W167 prereg -> W168 prereg (bloodline r804
W166->W167 xform machinery; r776 needle-count law: every needle asserted
count==1 before replacement; r587 never-transcribe law: every band/sha/
ordinal value re-derived from on-disk gate/probe receipts).

Facts machine-verified BEFORE xform:
  - band gate results/_r806bma_w168_band_gate.json rc0 ADMIT:
    A [384404,386403] hops=1 / B [386404,386603] hops=1,
    ARITH_A [384204,386203], ARITH_B [384404,384603],
    B_naive_first_clean [384404,384603], parity_with_probe True,
    leg0 rows=165 tail=W167 ordinal=158 bma_ordinal=84,
    leg3 W169+ projection A 386404..388403 / B 386604..386803;
  - pre-seat probe results/_r806bma_w168_probe_receipt.json ADMIT;
  - W168 seat published ceaf58908 (r806 pre-seat push, r565 law);
  - W167 finalize one-pass r806: ledger 772,812, K=365,320, merged mu
    -0.09287694 (display -0.0929), W167-only mu -0.09453436 (display
    -0.0945), merged sigma 0.24516431 (display 0.245164), se_mu 0.000406,
    A full_sharpe_p95 0.3141, skill K-lift +0.0000 (1.1836 -> 1.1836),
    voids LOWAMP-P1/P2 (science_gates.ledger.voids_applied);
  - W167 freeze sha f61835690 (r805 session, the REGISTERED W167 row);
  - SEED_REGISTRY live count = 188 numeric seed values (189 keys minus
    policy string key) -- unchanged from W167 prereg face.
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SRC = "research/PERPETUAL_N1_W167_PREREG.md"
DST = "research/PERPETUAL_N1_W168_PREREG.md"

# --- machine-derived facts (r587: read from on-disk receipts) ---------------
gate = json.load(open("results/_r806bma_w168_band_gate.json", encoding="utf-8"))
leg1, leg3 = gate["legs"]["leg1"], gate["legs"]["leg3"]
assert gate["verdict"] == "ADMIT", gate.get("verdict")
assert leg1["A"] == [384404, 386403] and leg1["B"] == [386404, 386603], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
assert leg1["ARITH_A"] == [384204, 386203], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [384404, 384603], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [384404, 384603], leg1["B_naive_first_clean"]
assert leg1["parity_with_probe"] is True
leg0 = gate["legs"]["leg0"]
assert leg0 == {"rows": 165, "tail": "W167", "owner_rows": 157,
                "bma_rows": 83, "ordinal": 158, "bma_ordinal": 84}, leg0
assert gate["legs"]["leg2"] == {"conflicts": 0, "origin_vacancy": True}
assert leg3["W169p_A"] == "386404..388403" and leg3["W169p_B"] == "386604..386803"
assert leg3["W169p_B_lands_inside_W169p_A"] is True

probe = json.load(open("results/_r806bma_w168_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT"
assert probe["bands"] == {"A": "384404_386403", "B": "386404_386603"}, probe.get("bands")

w167 = json.load(open("results/perpetual_faces/n1_w167_results.json", encoding="utf-8"))
npc = w167["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 365320, npc["merged"]
assert round(npc["merged"]["mu"], 4) == -0.0929, npc["merged"]["mu"]
assert round(npc["w167_only"]["mu"], 4) == -0.0945, npc["w167_only"]["mu"]
assert round(npc["merged"]["sigma"], 6) == 0.245164, npc["merged"]["sigma"]
assert npc["se_mu_at_k365320"] == 0.000406
assert w167["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3141
kl = w167["skill_line_v2_k_lift"]
assert kl["line_delta_k_lift"] == 0.0 and kl["line_merged_365320"] == 1.1836
assert w167["science_gates"]["ledger"]["voids_applied"] == ["LOWAMP-P1", "LOWAMP-P2"]
assert w167["science_gates"]["ledger"]["total"] == 772812

txt = open(SRC, encoding="utf-8").read()

REPL = [
# --- L1 title ---
("PERPETUAL-N1-W167 预注册 · N1 nulls-deepening 泵第 165 枚",
 "PERPETUAL-N1-W168 预注册 · N1 nulls-deepening 泵第 166 枚", 1),
("engine_owner 行 156+本候选=bm-a 第八十三枚自有波【r804】",
 "engine_owner 行 157+本候选=bm-a 第八十四枚自有波【r807】", 1),
# --- L3 seat/vacancy/single-state block ---
("波号 167=注册表 W166 行后首个自由号",
 "波号 168=注册表 W167 行后首个自由号", 1),
("本冻结窗 fetch 实核表尾时 W167 号位空档",
 "本冻结窗 fetch 实核表尾时 W168 号位空档", 1),
("（r801 gate leg2 实跑）",
 "（r806 gate leg2 实跑）", 1),
("全 inbox/processed/ W167 席位零外机命中",
 "全 inbox/processed/ W168 席位零外机命中", 1),
("MSG-2026-10-07-0056-bma-w167-seat 已推 origin 982424c5f 先于本冻结【r565 律·推送窗=pre-seat push 直接快进送达 982424c5f（r801 pre-seat push·zero --no-verify）",
 "MSG-2026-10-07-0259-bma-w168-seat 已推 origin ceaf58908 先于本冻结【r565 律·推送窗=pre-seat push 直接快进送达 ceaf58908（r806 pre-seat push·zero --no-verify）", 1),
("self-ack inbox→processed 移位待 W167 finalize 收口窗",
 "self-ack inbox→processed 移位待 W168 finalize 收口窗", 1),
("W166=bm-a r799 freeze（c2d6c5e14·表尾）；**均已注册**（表尾 W166 行）。W167=本波 skip-past-published 号位=表尾 W166 行后首个自由号（波号 167·单态零席位空档·gate leg0 机证 rows 164 tail W166）。",
 "W166=bm-a r799 freeze（c2d6c5e14）；W167=bm-a r805 freeze（f61835690·表尾）；**均已注册**（表尾 W167 行）。W168=本波 skip-past-published 号位=表尾 W167 行后首个自由号（波号 168·单态零席位空档·gate leg0 机证 rows 165 tail W167）。", 1),
# --- L5 band gate/probe refs + A/B face descriptions ---
("results/_r801bma_w167_band_gate.json",
 "results/_r806bma_w168_band_gate.json", 1),
("results/_r801bma_w167_probe.py",
 "results/_r806bma_w168_probe.py", 1),
("本波 **A-ext seed=382_204..384_203**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第二十六例**：A 面算术继续带 382_004..384_003 在其起点即被已注册 W166 B 带 382_004..382_203 **拒**（W166 席位 W167+ 投影+r796 sec8 succession+r799 gate leg3+W166 行投影散文（r799 冻结件）四投影注记所预言）→ 诚实前向走 **1 hop** 落 **382_204..384_203**·**A base==前波 B 尾+1（382_203+1）机检关系**=**A-hops-prior-B 阶梯几何第二十六例（E36 卡）**",
 "本波 **A-ext seed=384_404..386_403**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第二十七例**：A 面算术继续带 384_204..386_203 在其起点即被已注册 W167 B 带 384_204..384_403 **拒**（W167 席位 W168+ 投影+r806 sec8 succession+r801 gate leg3+W167 行投影散文（r805 冻结件）四投影注记所预言）→ 诚实前向走 **1 hop** 落 **384_404..386_403**·**A base==前波 B 尾+1（384_403+1）机检关系**=**A-hops-prior-B 阶梯几何第二十七例（E36 卡）**", 1),
("**B-ext exit seed=384_204..384_403**（**B 面=FIRST-CLEAN past own-wave A**：B 面算术继续带 382_204..382_403 在注册宇宙上 CLEAN 但**落在本波 A 窗内**（**同窗互斥面 leg2 律·W141 先例**：A 与 B 同一冻结 commit 双注册·互斥断言强制 B 越过本波 A 窗）→ B 带本波 A 窗保留走 **1 hop** 落 **384_204..384_403**·**B base==本波 A 尾+1（384_203+1）机检关系**·hop 链逐跳在 gate 回执；**W166 席位 W167+ 投影+r799 gate leg3+W166 行投影散文 re-derive-MANDATORY 注记三面兑现**：投影预言 W167 须在 post-W166 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）",
 "**B-ext exit seed=386_404..386_603**（**B 面=FIRST-CLEAN past own-wave A**：B 面算术继续带 384_404..384_603 在注册宇宙上 CLEAN 但**落在本波 A 窗内**（**同窗互斥面 leg2 律·W141 先例**：A 与 B 同一冻结 commit 双注册·互斥断言强制 B 越过本波 A 窗）→ B 带本波 A 窗保留走 **1 hop** 落 **386_404..386_603**·**B base==本波 A 尾+1（386_403+1）机检关系**·hop 链逐跳在 gate 回执；**W167 席位 W168+ 投影+r801 gate leg3+W167 行投影散文 re-derive-MANDATORY 注记三面兑现**：投影预言 W168 须在 post-W167 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）", 1),
("R250：W167 带从未指派", "R250：W168 带从未指派", 1),
("扫描面=pre-W167 全一百六十四行注册 N1 带表（表尾 W166 行·leg0 机证 164 行）",
 "扫描面=pre-W168 全一百六十五行注册 N1 带表（表尾 W167 行·leg0 机证 165 行）", 1),
# --- L9 reuse domain ---
("（W2..W166 落地 runner 的 wave 参数化复用",
 "（W2..W167 落地 runner 的 wave 参数化复用", 1),
# --- L12 batch identity ---
("批名=**PERPETUAL-N1-W167**", "批名=**PERPETUAL-N1-W168**", 1),
("起稿窗实况：**W1..W166 N1 finalize 已全部落地**【W166 finalize one-pass bm-a r799·§7/§8 已回填】——净账本锚头 **770,612**（W166 finalize 落账【one-pass·K=363,120 合并池·voids LOWAMP-P1/P2】）",
 "起稿窗实况：**W1..W167 N1 finalize 已全部落地**【W167 finalize one-pass bm-a r806·§7/§8 已回填】——净账本锚头 **772,812**（W167 finalize 落账【one-pass·K=365,320 合并池·voids LOWAMP-P1/P2】）", 1),
("累计 null 池=363,120+2,200（本波）=**365,320 投影**",
 "累计 null 池=365,320+2,200（本波）=**367,520 投影**", 1),
# --- L13 claim block ---
("本机 r801 席位 MSG-2026-10-07-0056 投影 W168+ A 384_204..386_203 naive/B 384_404..384_603 naive",
 "本机 r806 席位 MSG-2026-10-07-0259 投影 W169+ A 386_404..388_403 naive/B 386_604..386_803 naive", 1),
("继承待 W168 注册宇宙复核", "继承待 W169 注册宇宙复核", 1),
("T-2026-10-01-141 s1 引擎线第 157 波【bm-a 第八十三枚自有波【机面 derive：engine_owner==bm-a 行 82+本候选以 gate leg0 机证为准·同 W157/W158/W159/W160/W161/W162/W163/W165/W166 最近自有波】",
 "T-2026-10-01-141 s1 引擎线第 158 波【bm-a 第八十四枚自有波【机面 derive：engine_owner==bm-a 行 83+本候选以 gate leg0 机证为准·同 W157/W158/W159/W160/W161/W162/W163/W165/W166/W167 最近自有波】", 1),
("（波号=注册表 W166 行后首个自由号·单态零席位空档；中位公示 MSG-2026-10-07-0056-bma-w167-seat 先推 origin 982424c5f r565 律；lane-free；dept:研究）。",
 "（波号=注册表 W167 行后首个自由号·单态零席位空档；中位公示 MSG-2026-10-07-0259-bma-w168-seat 先推 origin ceaf58908 r565 律；lane-free；dept:研究）。", 1),
# --- L15 materialization tick note ---
("下一 tick 新进程读活栈自见 W167 行并点火自烧",
 "下一 tick 新进程读活栈自见 W168 行并点火自烧", 1),
# --- L19/L20 banned gate + prere-read ---
("--prereg research/PERPETUAL_N1_W167_PREREG.md",
 "--prereg research/PERPETUAL_N1_W168_PREREG.md", 1),
("v1 ext；v2..W166 落地）", "v1 ext；v2..W167 落地）", 1),
# --- L31 A-block ---
("entry rng seed=**382_204+j**（法典 §4 W167 行 A=382_204..384_203·**FIRST-CLEAN past prior-wave B 阶梯第二十六例**：算术续带 382_004..384_003 起点即被 W166 B 带拒→1 hop 落 382_204..384_203·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场）",
 "entry rng seed=**384_404+j**（法典 §4 W168 行 A=384_404..386_403·**FIRST-CLEAN past prior-wave B 阶梯第二十七例**：算术续带 384_204..386_203 起点即被 W167 B 带拒→1 hop 落 384_404..386_403·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场）", 1),
# --- L32 B-block ---
("entry rng=**382_204+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**384_204+j**（法典 §4 W167 行 B=384_204..384_403·**FIRST-CLEAN past own-wave A**：B 算术续带 382_204..382_403 在注册宇宙上 CLEAN 但落在本波 A 窗内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗→保留走落 384_204..384_403·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 gate 回执·与 W166 席位 W167+ 投影+r799 gate leg3+W166 行投影散文 W167+ 投影 re-derive-MANDATORY+同窗互斥预披露注记三面兑现收敛·ADMIT 回执在场）",
 "entry rng=**384_404+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**386_404+j**（法典 §4 W168 行 B=386_404..386_603·**FIRST-CLEAN past own-wave A**：B 算术续带 384_404..384_603 在注册宇宙上 CLEAN 但落在本波 A 窗内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗→保留走落 386_404..386_603·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 gate 回执·与 W167 席位 W168+ 投影+r801 gate leg3+W167 行投影散文 W168+ 投影 re-derive-MANDATORY+同窗互斥预披露注记三面兑现收敛·ADMIT 回执在场）", 1),
# --- L34 probe note ---
("本波设计=W2..W166 逐字复用", "本波设计=W2..W167 逐字复用", 1),
# --- L36 disjoint selftest block ---
("W167 带与 v1 在用带", "W168 带与 v1 在用带", 1),
("W2..W166 在用带（**全注册单态**）", "W2..W167 在用带（**全注册单态**）", 1),
("本波机验 ADMIT 回执在场=r801 bm-a 带闸窗（pre-seat probe r801 先跑·双窗 derive 恒等）；selftest W167 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W166 行 parity 腿【r735 测量-实现分叉族防护面：A/B 窗 set-range 针在场】）",
 "本波机验 ADMIT 回执在场=r806 bm-a 带闸窗（pre-seat probe r806 先跑·双窗 derive 恒等）；selftest W168 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W167 行 parity 腿【r735 测量-实现分叉族防护面：A/B 窗 set-range 针在场】）", 1),
# --- L39/L40 ledger blocks ---
("起草窗实流 W1..W166 已落账 363,120 实测",
 "起草窗实流 W1..W167 已落账 365,320 实测", 1),
('file_name="results/perpetual_faces/n1_w167_results.json"',
 'file_name="results/perpetual_faces/n1_w168_results.json"', 1),
# --- L44 prediction-key preamble ---
("（起草窗实况注记：**W1..W166 N1 finalize 已全部落地**——净账本锚头 770,612=W166 finalize 落账【one-pass·bm-a r799·§7/§8 已回填】·**K=363,120 合并池**·**零在飞上游席位中**（链前置出空波）。本波 §5 预测键=**W166 finalize 实测值**【results/perpetual_faces/n1_w166_results.json·N1 面最新已落账键】。",
 "（起草窗实况注记：**W1..W167 N1 finalize 已全部落地**——净账本锚头 772,812=W167 finalize 落账【one-pass·bm-a r806·§7/§8 已回填】·**K=365,320 合并池**·**零在飞上游席位中**（链前置出空波）。本波 §5 预测键=**W167 finalize 实测值**【results/perpetual_faces/n1_w167_results.json·N1 面最新已落账键】。", 1),
# --- L45-L47 prediction keys 1-3 ---
("1. W167-only mu 与累计池 merged mu（W166 实测键 **−0.0929**·K=363,120 合并池·W166-only 实测 **−0.0912**）差异 **|Δ|<0.02**（W2..W166 共一百六十五面实测 mu 稳定先例·单波跨键微）。",
 "1. W168-only mu 与累计池 merged mu（W167 实测键 **−0.0929**·K=365,320 合并池·W167-only 实测 **−0.0945**）差异 **|Δ|<0.02**（W2..W167 共一百六十六面实测 mu 稳定先例·单波跨键微）。", 1),
("2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.245153**=W166 合并池实测 0.245153）。",
 "2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.245164**=W167 合并池实测 0.245164）。", 1),
("3. A 档 full_sharpe_p95 与 W166 A 档 p95（**0.3005** 实测锚）差 **<0.05**（门标注法 W5..W166 先例",
 "3. A 档 full_sharpe_p95 与 W167 A 档 p95（**0.3141** 实测锚）差 **<0.05**（门标注法 W5..W167 先例", 1),
# --- L48 K-lift chain + se_mu chain ---
("——W136..W166 先例·", "——W136..W167 先例·", 1),
("W165 **−0.0001**/W166 **+0.0000** 如实披露",
 "W165 **−0.0001**/W166 **+0.0000**/W167 **+0.0000** 如实披露", 1),
("键 W166 实测 K-lift **+0.0000**【line_merged@K363,120 **1.1834**·line_pre 1.1834·n_eff 768,412",
 "键 W167 实测 K-lift **+0.0000**【line_merged@K365,320 **1.1836**·line_pre 1.1836·n_eff 770,612", 1),
("W165 **0.000408**→W166 **0.000407**】",
 "W165 **0.000408**→W166 **0.000407**→W167 **0.000406**】", 1),
# --- L49 W169+ projection ---
("5. **W168+ 投影（gate 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 384_204..386_203 **CLEAN**（hops=0）；B first-clean **384_404..384_603 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W168：W168 冻结方必须在 post-W167 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W167 B 带 384_204..384_403 注册后将拒 naive W168 A 窗**——W168 A 重 derive 同强制（越过 W167 B 带·阶梯 A-hops-prior-B 继承第二十七例）；verify at W168 prereg，hop 链逐跳在 probe 回执。",
 "5. **W169+ 投影（gate 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 386_404..388_403 **CLEAN**（hops=0）；B first-clean **386_604..386_803 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W169：W169 冻结方必须在 post-W168 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W168 B 带 386_404..386_603 注册后将拒 naive W169 A 窗**——W169 A 重 derive 同强制（越过 W168 B 带·阶梯 A-hops-prior-B 继承第二十八例）；verify at W169 prereg，hop 链逐跳在 probe 回执。", 1),
# --- L52/L53 runner + deliverables ---
("--wave 167/finalize --wave 167", "--wave 168/finalize --wave 168", 1),
("【n1_w167/ 分片计数增长·唯一点火证据·r325 律】",
 "【n1_w168/ 分片计数增长·唯一点火证据·r325 律】", 1),
("results/p2cal_ext/n1_w167/shard-<k>-of-12.json",
 "results/p2cal_ext/n1_w168/shard-<k>-of-12.json", 1),
("`results/perpetual_faces/n1_w167_results.json`（finalize 合并件",
 "`results/perpetual_faces/n1_w168_results.json`（finalize 合并件", 1),
("起草窗零在飞上游席位（W1..W166 全落账）",
 "起草窗零在飞上游席位（W1..W167 全落账）", 1),
# --- L54 engine ledger block ---
("（engine_owner==bm-a 82 行注册 + 本候选——以 gate leg0 机证为准·同 W157/W158/W159/W160/W161/W162/W163/W165/W166 最近自有波）",
 "（engine_owner==bm-a 83 行注册 + 本候选——以 gate leg0 机证为准·同 W157/W158/W159/W160/W161/W162/W163/W165/W166/W167 最近自有波）", 1),
# --- L57/L60/L61 finalize-window placeholders ---
("【finalize 收口机械回填·待 W167 finalize 窗】",
 "【finalize 收口机械回填·待 W168 finalize 窗】", 1),
("【finalize 同窗回填·待 W167 finalize 窗】",
 "【finalize 同窗回填·待 W168 finalize 窗】", 1),
("（占位·§5.5 W168+ 投影承接+宝藏/方法论捕获问+诚实披露面·finalize 收口窗机械回填。）",
 "（占位·§5.5 W169+ 投影承接+宝藏/方法论捕获问+诚实披露面·finalize 收口窗机械回填。）", 1),
]

for needle, repl, expect in REPL:
    n = txt.count(needle)
    assert n == expect, f"needle count {n} != {expect}: {needle[:60]!r}"
    txt = txt.replace(needle, repl)

# global batch-name flip (L40 append_ledger remains; title/L12 handled above)
n = txt.count("PERPETUAL-N1-W167")
assert n == 1, f"remaining PERPETUAL-N1-W167 = {n} (expect 1: L40 append_ledger)"
txt = txt.replace("PERPETUAL-N1-W167", "PERPETUAL-N1-W168")

# --- residual scans (r773 full-file face hygiene) ---------------------------
# no stray wave-167 OWN band values may survive (the W167 registered B band
# 384_204..384_403 and the W168 naive-A continuation 384_204..386_203 are
# legitimate prior-wave/naive context and stay):
for stray in ("382_204..384_203", "382_004..384_003",
              "382_004..382_203", "382_204..382_403"):
    assert stray not in txt, f"stray W167 band value survived: {stray}"
# 167/168 coherence: batch identity, runner wave, shard dir all 168:
assert txt.count("--wave 168") == 2
assert "n1_w168/shard" in txt and "n1_w168_results.json" in txt
assert "PERPETUAL-N1-W168 预注册" in txt and "第 166 枚" in txt
assert "引擎线第 158 波" in txt and "第八十四枚自有波" in txt
# prior-wave references stay (W167 = prior wave now):
assert "被已注册 W167 B 带 384_204..384_403" in txt
assert "W167-only 实测 **−0.0945**" in txt
assert "键 **0.245164**=W167 合并池实测 0.245164" in txt
assert "**0.3141** 实测锚" in txt
assert "772,812" in txt and "**367,520 投影**" in txt
assert "W167=bm-a r805 freeze（f61835690·表尾）" in txt
assert "ceaf58908" in txt and "MSG-2026-10-07-0259-bma-w168-seat" in txt
assert "results/_r806bma_w168_band_gate.json" in txt
# W169+ projection face (gate leg3 verbatim):
assert "A first-clean 386_404..388_403 **CLEAN**（hops=0）" in txt
assert "B first-clean **386_604..386_803 CLEAN**（hops=0）" in txt
assert "W168 B 带 386_404..386_603 注册后将拒 naive W169 A 窗" in txt

open(DST, "w", encoding="utf-8", newline="").write(txt)
print(f"W168 prereg xform OK: {SRC} -> {DST}")
print(f"bytes: {len(txt.encode('utf-8'))}")
print(f"lines: {len(txt.splitlines())}")
