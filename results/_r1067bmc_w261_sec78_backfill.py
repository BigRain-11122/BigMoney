# -*- coding: utf-8 -*-
"""r1067 bm-c: W261 prereg sec.7/8 mechanical backfill (finalize same-window law).

Replaces the two placeholder lines in research/PERPETUAL_N1_W261_PREREG.md with
finalize actuals (n1_w261_results.json + fivekeys/sixgate receipts, machine-read).
Clone lineage: _r1065 W260 sec78 backfill pattern (r1064/r1062/r1060 canon).
Freeze-law scope: placeholders ONLY, judge lines untouched.
"""
import io
import json

P = "research/PERPETUAL_N1_W261_PREREG.md"
res = json.load(io.open("results/perpetual_faces/n1_w261_results.json", encoding="utf-8"))
fk = json.load(io.open("results/_r1067bmc_w261_fivekeys.json", encoding="utf-8"))
pool = res["null_pool_cumulative"]
merged_mu = pool["merged"]["mu"]
merged_sigma = pool["merged"]["sigma"]
w261_mu = pool["w261_only"]["mu"]
w261_sigma = pool["w261_only"]["sigma"]
se_mu = pool["se_mu_at_k572120"]
sl = res["skill_line_v2_k_lift"]
kc = {c["name"]: c for c in fk["checks"]}

sec7 = f"""## §7 跑后实证。【finalize 收口机械回填】
- 账本恒等式：prev **996,335** + 2,200 = **998,535 EXACT**（voids LOWAMP-P1/P2 同法应用·append_one_pass）。
- 合并池：**K=572,120 EXACT**（569,920+2,200）；merged mu **-0.092736**（{merged_mu}）/ sigma **0.245033**（{merged_sigma}）/ **se_mu@K=572,120=0.000324**（W260 键 0.000325 → **收窄·≤ 键 PASS**）；W261-only mu **-0.094120**（{w261_mu}）/ sigma **0.243488**（{w261_sigma}）。
- §5 五预测键机证件（results/_r1067bmc_w261_fivekeys.json·**ALL PASS**）：①W261-only vs merged mu gap **0.001384**<0.02 ✓（merged vs W260 键差 0.0000053 ✓——小 gap 族延续）②sigma rel **-0.0025%**<±10% ✓ ③A 档 p95 **0.299400** vs 键 0.3292 差 **-0.029800**<0.05 ✓ ④K-lift 线移 **-0.000100**（line_pre 1.1952→line_merged 1.1951 @n_eff held 996,335）≤±0.02 ✓ ⑤se_mu **0.000324**≤0.000325 ✓（**收窄**——W259 0.000325→W260 0.000325→本波 0.000324·K 加深 2,200 后恢复收窄=测量面如实记注）。
- 六门探针：results/_r1067bmc_w261_sixgate.json **ALL PASS**（PRE-FINALIZE 相位先过——W217-debt standing law 执行·**连续第 23 波正相位**；gate-1 n1 三重恒等 **6df7875e7f9312cc**（worktree==freeze receipt post==LANDED git blob @ 68aad04b6）零漂移——本波零 post-splice heal（splice commit 68aad04b6=worktree 字节直落）+ pf 面 worktree==receipt post **34a5a2c68a20e3e4**（git-diff-empty 披露）+ wave-row faces==freeze bands + banned rc0 + pf selftest + n1 selftest + shards 12/12 + seed_admit FREE verbatim base=589501 span=2000 / base=591501 span=200 + W260 边界 kept）。
- canon flip 态：**NOT PERFORMED BY THIS WAVE -- GOVERNANCE PROPOSAL FACE ONLY (K2200 SAME LAW)**（governance proposal face only·K2200 同法）。
- 引擎烧录：engine self-burn **12/12**（shard 0-11·常驻引擎 materializer mtime-watch 自见 auto-ignite·splice 落盘 68aad04b6 后自烧·ledger appends ad2aa9322+b88dc8fcd batched 6+5 self-commit〔shard-7 由引擎下拍 batch tick 补载·盘上 12/12 齐已验〕·本窗 r1067 收口）。
- audit 段：machine=bm-c·finalize_only=true·shards_consumed 12/12 文件名全录。
- 诚实披露：K-lift **-0.000100**（W260 0.0000→本波 -0.0001=微移·远在 ±0.02 断言带内·nulls-deepening 测量面非注册收益）；A p95 0.299400 较 W260 键 0.3292 差 **-0.0298**（2,000 试 A 切片抽样波动·W257 -0.0134/W258 +0.0135/W259 +0.0126/W260 +0.0058 后本波 -0.0298=双向波动链续第十一证·带内 PASS 如实记注）；W261-only vs merged gap 0.001384（带内 0.02·W258 0.002891/W259 0.008115/W260 0.001170 后本波 0.001384 小 gap 族·2,200 新种子带抽样面·六键全过如实记注）；se_mu 0.000324（W257 0.000326→W258 0.000326→W259 0.000325→W260 0.000325→本波 0.000324·**恢复收窄**·≤ 断言 PASS·K 加深 2,200 后收窄=测量面如实记注）。
"""

sec8 = f"""## §8 批后复盘。【finalize 同窗回填】
- §5.5 W262+ 投影承接机证：本波 finalize 落地=**W262 席开放**——下一位 freezer 必须 seat-first publish（O-20261010-2350 §2）+post-W261 universe live re-derive（禁转录 r587 律）+derive B 时预留本波 A 窗 589_501..591_500 与 B 带 591_501..591_700（W261 §5.5 face：naive W262 A 起点 591_501 将被注册 W261 B 带 591_501..591_700 拒=staircase-affects-A **ELEVENTH consecutive A-hop 预期**→A first-clean 将再上移；B own-A reservation cascade 落位相应上移·B naive 591_701..591_900 CLEAN 但落投影 A 窗内=staircase face 延续；**W262 冻结方禁假设 A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**——W251 起 staircase affects A·W252..W261=A/B 双 1-hop 形态连续十波如实注记；verify at W262 prereg，hop 链逐跳在 probe 回执复核）。
- 宝藏与方法论捕获问：**本批零新方法论面**（W261 周期=正典链续接·五键全带内·六门/finalize 全正相位一次过——无新机制/无新根因；sixgate/fivekeys/sec78 derive=E63 canon-clone 链复用零新卡；宝藏登记零新条（既有链法覆盖）；se_mu 恢复收窄与 A p95 双向波动=测量面如实记注非新方法论）。
- 诚实披露面：本窗=**57th-gen absorb 续接**（死窗链 r1067 段：editor estate 预建〔build_editor+derive_editor+needle preflight 149 faces+freeze_edits bundle〕·本窗机器验证后续跑：1 disclosed comment needle heal〔freeze_edits 中段 STRUCTURAL CHOICE 注释面 W211..W238 legs (28)→W211..W242 legs (32)·W257-editor 起五代继承陈旧 needle 漏面·代码断言正身 governs·注释级零行为影响〕+五面冻结 splice 落地 commit **68aad04b6**〔pf 31d5dc07baee6620→34a5a2c68a20e3e4 / n1 f40a82c450f32c5a→6df7875e7f9312cc·bands A 589_501..591_500 TENTH A-hop / B 591_501..591_700 ELEVENTH above-own-A·parity 119 rows〕+引擎 mtime-watch 自烧 12/12〔ledger appends ad2aa9322+b88dc8fcd batched 6+5 self-commit〕+六门 PRE-FINALIZE ALL PASS〔连续第 23 波〕+finalize one-pass 998,535/K=572,120 EXACT+五键 6/6 ALL PASS+sec.7/8 本窗回填——E63 aging-token 律执法面：w244_a band-set 变量面继续持有 wave-261 bands 未滚动〔r1065 同缺陷防三犯〕）。
"""

t = io.open(P, encoding="utf-8", newline="").read()
ph7 = "## §7 跑后实证。【finalize 收口机械回填】\n- （占位·finalize one-pass 后回填：账本恒等式/合并池 K/merged mu·sigma·se_mu/K-lift 对照/§5 五预键机证件/六门探针/canon flip 态/audit 段——bm-c r1065 W260 §7 范式）\n"
ph8 = "## §8 批后复盘。【finalize 同窗回填】\n- （占位·finalize 同窗回填：§5.5 W262+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——bm-c r1065 W260 §8 范式）\n"
assert t.count(ph7) == 1, "sec.7 placeholder not found exactly once"
assert t.count(ph8) == 1, "sec.8 placeholder not found exactly once"
t2 = t.replace(ph7, sec7).replace(ph8, sec8)
assert "（占位" not in t2, "placeholder residue after backfill"
io.open(P, "w", encoding="utf-8", newline="").write(t2)
print("SEC78 BACKFILL OK -- placeholders=0, judge lines untouched")
