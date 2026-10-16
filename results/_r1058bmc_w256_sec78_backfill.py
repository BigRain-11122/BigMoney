# -*- coding: utf-8 -*-
# r1058 bm-c: W256 prereg sec.7/8 mechanical backfill (finalize-window, bm-c
# r1057 W255 范式). Frozen-judgment faces untouched -- backfill limited to
# sec.7/8 placeholder lines per the prereg tail law (回填限 §7/§8).
import io

P = "research/PERPETUAL_N1_W256_PREREG.md"
t = io.open(P, encoding="utf-8").read()

sec7_old = "- （占位·finalize one-pass 后回填：账本恒等式/合并池 K/merged mu·sigma·se_mu/K-lift 对照/§5 五预键机证件/六门探针/canon flip 态/audit 段——bm-c r1057 W255 §7 范式）"
sec8_old = "- （占位·finalize 同窗回填：§5.5 W257+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——bm-c r1057 W255 §8 范式）"

sec7_new = """- 账本恒等式：prev **985,335** + 2,200 = **987,535 EXACT**（voids LOWAMP-P1/P2 同法应用·append_one_pass）。
- 合并池：**K=561,120 EXACT**（558,920+2,200）；merged mu **-0.092700**（-0.09270015433418877）/ sigma **0.245038**（0.24503834821648132）/ **se_mu@K=561,120=0.000327**（W255 键 0.000328 → **收窄恢复**·< 键 PASS）；W256-only mu **-0.090659**（-0.090659）/ sigma **0.244814**（0.24481355135242097）。
- §5 五预测键机证件（results/_r1058bmc_w256_fivekeys.json·**ALL PASS**）：①W256-only vs merged mu gap **0.002041**<0.02 ✓（merged vs W255 键差 0.000008 ✓）②sigma rel **-0.0000044%**<±10% ✓ ③A 档 p95 **0.310700** vs 键 0.3422 差 **-0.031500**<0.05 ✓ ④K-lift 线移 **0.000000**（line_pre 1.194700→line_merged 1.194700 @n_eff held 985,335）≤±0.02 ✓ ⑤se_mu **0.000327**<0.000328 ✓（**收窄链恢复**——W254 0.000328→W255 0.000328 持平后本波再收窄·测量面如实注记）。
- 六门探针：results/_r1058bmc_w256_sixgate.json **ALL PASS**（PRE-FINALIZE 相位先过——W217-debt standing law 执行·**连续第 18 波正相位**；gate-1 n1 三重恒等 **986e9162b86e0c7f**（worktree==freeze receipt post==LANDED git blob @ aa6102e35）零漂移——本波零 post-splice heal（splice commit aa6102e35=healed worktree 字节直落·3 needle heals pre-splice 闸内修复）+ pf 面 worktree==receipt post **ad9776287dd52280**（git-diff-empty 披露）+ wave-row faces==freeze bands + banned rc0 + pf selftest + n1 selftest + shards 12/12 + seed_admit FREE verbatim base=578501 span=2000 / base=580501 span=200 + W255 boundary 576301/578301 kept）。
- canon flip 态：**NOT PERFORMED BY THIS WAVE -- GOVERNANCE PROPOSAL FACE ONLY (K2200 SAME LAW)**（governance proposal face only·K2200 同法）。
- 引擎烧录：engine self-burn **12/12**（shard 0-11·常驻引擎 materializer mtime-watch 自见 auto-ignite·aa6102e35 splice 落盘后自烧·ledger appends 31c9e4872+1c7112fd9 batched 6+6 self-commit·本窗 r1058 收口）。
- audit 段：machine=bm-c·finalize_only=true·shards_consumed 12/12 文件名全录。
- 诚实披露：K-lift **0.000000**=零移动段（W136..W255 先例全在 ±0.0003 内·W254 -0.0001→W255 +0.0001→本波 0.0000=回中·远在 ±0.02 断言带内·nulls-deepening 测量面非注册收益）；A p95 0.310700 较 W255 键 0.3422 差 **-0.0315**（2,000 试 A 切片抽样波动·测量面非注册收益·W252 +0.0046/W253 -0.0077/W254 -0.0030/W255 +0.0330 正向大摆后本波负向回摆=**双向波动链第六证**·带内 PASS 如实注记）；W256-only vs merged gap 0.002041（带内 0.02·W253 0.000189/W254 0.000324/W255 0.007454 链内最大后本波 0.002041=**收紧回中**·2,000 新种子带抽样面·六键全过如实注记）；se_mu 0.000327（W254 0.000328→W255 0.000328 持平→本波 0.000327·< 断言 PASS·**收窄链恢复**·K 加深 2,200 后恢复收窄=测量面如实注记）。"""

sec8_new = """- §5.5 W257+ 投影承接机证：本波 finalize 落地=**W257 席开放**——下一位 freezer 必须 seat-first publish（O-20261010-2350 §2）+post-W256 universe live re-derive（禁转录 r587 律）+derive B 时预留本波 A 窗 578_501..580_500 与 B 带 580_501..580_700（W256 §5.5 face：A naive 580_501..582_500 CLEAN-at-naive pre-W256 **BUT post-W256 注册后起点 580_501 被注册 W256 B 带 580_501..580_700 拒**=staircase-affects-A **6th consecutive A-hop 预期**→A first-clean 将再上移；B own-A reservation cascade 落位相应上移·B naive 580_701..580_900 CLEAN 但落投影 A 窗内=W257p_B_lands_inside_W257p_A_naive face 延续；**W257 冻结方禁假设 A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**——W251 起 staircase affects A·W252/W253/W254/W255/W256=A/B 双 1-hop 形态连续五波如实注记；W257 derive 必须在 post-W256 注册宇宙重 derive 且预留本波 A 窗+本波 B 带——leg2 律/E36 卡·W141 先例；verify at W257 prereg，hop 链逐跳在 probe 回执复核）。
- 宝藏与方法论捕获问：**本批零新方法论面**（W256 周期=正典链续接·五面全带内·六闸/五键/终定全正相位一次过——无新机制/无新根因；sixgate/fivekeys/sec78 derive=E63 canon-clone 链复用零新卡；宝藏登记零新条（既有链法覆盖）；se_mu 收窄链恢复面与 A-p95 负向回摆=测量面如实注记非新方法论）。
- 诚实披露面：本窗=**49th-gen absorb 续接**（死窗 r1058 段：prereg freeze 5996e2c93 落地并 push+five-face splice aa6102e35 落地并 push+引擎 mtime-watch 自烧 12/12〔ledger appends 31c9e4872+1c7112fd9 self-commit〕+S6 43 腿 03:06:18 rc0 后死 pre-closeout——本窗吸收续接：六门 PRE-FINALIZE ALL PASS〔连续第 18 波正相位〕+finalize one-pass 987,535/K=561,120 EXACT+五键 6/6+§7/§8 回填+W257 席位发布）；W256 席位=bm-c own-seat（第 76 枚 own·第 246 引擎波·prereg 5996e2c93·seat MSG-20261017-023x-bmc-w256-seat origin fd48643c9 先于冻结发布〔r565 律〕）。"""

assert t.count(sec7_old) == 1, "sec7 placeholder not found exactly once"
assert t.count(sec8_old) == 1, "sec8 placeholder not found exactly once"
t = t.replace(sec7_old, sec7_new).replace(sec8_old, sec8_new)
io.open(P, "w", encoding="utf-8", newline="").write(t)
print("BACKFILL-OK bytes=%d" % len(t.encode("utf-8")))
