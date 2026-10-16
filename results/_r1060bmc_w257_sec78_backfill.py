# -*- coding: utf-8 -*-
# r1060 bm-c: W257 prereg sec.7/8 mechanical backfill (finalize-window, bm-c
# r1058 W256 范式 clone). Frozen-judgment faces untouched -- backfill limited
# to sec.7/8 placeholder lines per the prereg tail law (回填限 §7/§8).
import io

P = "research/PERPETUAL_N1_W257_PREREG.md"
t = io.open(P, encoding="utf-8").read()

sec7_old = "- （占位·finalize one-pass 后回填：账本恒等式/合并池 K/merged mu·sigma·se_mu/K-lift 对照/§5 五预键机证件/六门探针/canon flip 态/audit 段——bm-c r1058 W256 §7 范式）"
sec8_old = "- （占位·finalize 同窗回填：§5.5 W258+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——bm-c r1058 W256 §8 范式）"

sec7_new = """- 账本恒等式：prev **987,535** + 2,200 = **989,735 EXACT**（voids LOWAMP-P1/P2 同法应用·append_one_pass）。
- 合并池：**K=563,320 EXACT**（561,120+2,200）；merged mu **-0.092756**（-0.09275554143293332）/ sigma **0.245030**（0.24502958710593273）/ **se_mu@K=563,320=0.000326**（W256 键 0.000327 → **收窄链续**·< 键 PASS）；W257-only mu **-0.106882**（-0.10688227272727273）/ sigma **0.242427**（0.2424268565881185）。
- §5 五预测键机证件（results/_r1060bmc_w257_fivekeys.json·**ALL PASS**）：①W257-only vs merged mu gap **0.014127**<0.02 ✓（merged vs W256 键差 0.000055 ✓）②sigma rel **-0.0000036%**<±10% ✓ ③A 档 p95 **0.297300** vs 键 0.3107 差 **-0.013400**<0.05 ✓ ④K-lift 线移 **-0.000100**（line_pre 1.194800→line_merged 1.194700 @n_eff held 987,535）≤±0.02 ✓ ⑤se_mu **0.000326**<0.000327 ✓（**收窄链续**——W255 0.000328→W256 0.000327→本波 0.000326 连续收窄·测量面如实注记）。
- 六门探针：results/_r1060bmc_w257_sixgate.json **ALL PASS**（PRE-FINALIZE 相位先过——W217-debt standing law 执行·**连续第 19 波正相位**；gate-1 n1 三重恒等 **e37b483340aa67ba**（worktree==freeze receipt post==LANDED git blob @ 550293d3f）零漂移——本波零 post-splice heal（splice commit 550293d3f=worktree 字节直落）+ pf 面 worktree==receipt post **38da334ef0a033d2**（git-diff-empty 披露）+ wave-row faces==freeze bands + banned rc0 + pf selftest + n1 selftest + shards 12/12 + seed_admit FREE verbatim base=580701 span=2000 / base=582701 span=200 + W256 boundary 578501/580501 kept）。
- canon flip 态：**NOT PERFORMED BY THIS WAVE -- GOVERNANCE PROPOSAL FACE ONLY (K2200 SAME LAW)**（governance proposal face only·K2200 同法）。
- 引擎烧录：engine self-burn **12/12**（shard 0-11·常驻引擎 materializer mtime-watch 自见 auto-ignite·splice 落盘 05:00:08 后自烧·ledger appends 9b848c2e0+370d6c81 batched 6+6 self-commit·本窗 r1060 收口）。
- audit 段：machine=bm-c·finalize_only=true·shards_consumed 12/12 文件名全录。
- 诚实披露：K-lift **-0.000100**（W136..W256 先例全在 ±0.0003 内·W255 +0.0001→W256 0.0000→本波 -0.0001=负向微摆·远在 ±0.02 断言带内·nulls-deepening 测量面非注册收益）；A p95 0.297300 较 W256 键 0.3107 差 **-0.0134**（2,000 试 A 切片抽样波动·W254 -0.0030/W255 +0.0330/W256 -0.0315 后本波 -0.0134=**双向波动链续第七证**·带内 PASS 如实注记）；W257-only vs merged gap 0.014127（带内 0.02·W254 0.000324/W255 0.007454/W256 0.002041 链内最大后本波 0.014127=**链内新最大**·2,000 新种子带抽样面·六键全过如实注记）；se_mu 0.000326（W255 0.000328→W256 0.000327→本波 0.000326·< 断言 PASS·**收窄链续**·K 加深 2,200 后续收窄=测量面如实注记）。"""

sec8_new = """- §5.5 W258+ 投影承接机证：本波 finalize 落地=**W258 席开放**——下一位 freezer 必须 seat-first publish（O-20261010-2350 §2）+post-W257 universe live re-derive（禁转录 r587 律）+derive B 时预留本波 A 窗 580_701..582_700 与 B 带 582_701..582_900（W257 §5.5 face：A naive 582_701..584_700 CLEAN-at-naive pre-W257 **BUT post-W257 注册后起点 582_701 被注册 W257 B 带 582_701..582_900 拒**=staircase-affects-A **7th consecutive A-hop 预期**→A first-clean 将再上移；B own-A reservation cascade 落位相应上移·B naive 582_901..583_100 CLEAN 但落投影 A 窗内=W258p_B_lands_inside_W258p_A_naive face 延续；**W258 冻结方禁假设 A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**——W251 起 staircase affects A·W252..W257=A/B 双 1-hop 形态连续六波如实注记；W258 derive 必须在 post-W257 注册宇宙重 derive 且预留本波 A 窗+本波 B 带——leg2 律/E36 卡·W141 先例；verify at W258 prereg，hop 链逐跳在 probe 回执复核）。
- 宝藏与方法论捕获问：**本批零新方法论面**（W257 周期=正典链续接·五面全带内·六闸/五键/终定全正相位一次过——无新机制/无新根因；sixgate/fivekeys/sec78 derive=E63 canon-clone 链复用零新卡；宝藏登记零新条（既有链法覆盖）；se_mu 收窄链续与 W257-only gap 链内新大=测量面如实注记非新方法论）。
- 诚实披露面：本窗=**50th-gen absorb 续接**（死窗 r1060 段：needle_preflight 04:48+editor derive canon-clone 04:52+splice 落盘 05:00:08 receipt+引擎 mtime-watch 自烧 12/12〔ledger appends 9b848c2e0+370d6c81 self-commit〕后死 pre-commit——本窗吸收续接：estate 机器验证〔receipt pre==HEAD 双面+post==worktree 双面零漂移〕+splice commit 550293d3f 落地并 push+六门 PRE-FINALIZE ALL PASS〔连续第 19 波正相位〕+finalize one-pass 989,735/K=563,320 EXACT+五键 6/6+§7/§8 回填+W258 席位发布）；W257 席位=bm-c own-seat（第 77 枚 own·第 247 引擎波·prereg c7fbc443c·seat MSG-20261017-03xx-bmc-w257-seat origin 27ee6e95a 先于冻结发布〔r565 律〕）。"""

assert t.count(sec7_old) == 1, "sec7 placeholder not found exactly once"
assert t.count(sec8_old) == 1, "sec8 placeholder not found exactly once"
t = t.replace(sec7_old, sec7_new).replace(sec8_old, sec8_new)
assert t.count("占位") == 0, "residual placeholders remain"
io.open(P, "w", encoding="utf-8", newline="").write(t)
print("BACKFILL-OK bytes=%d placeholders=0" % len(t.encode("utf-8")))
