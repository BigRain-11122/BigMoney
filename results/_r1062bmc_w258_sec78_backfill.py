# -*- coding: utf-8 -*-
# r1062 bm-c: W258 prereg sec.7/8 mechanical backfill (finalize-window, bm-c
# r1060 W257 范式 clone). Frozen-judgment faces untouched -- backfill limited
# to sec.7/8 placeholder lines per the prereg tail law (回填限 §7/§8).
# Line-located placeholders (console-wrap-safe): sec7 line contains
# '占位·finalize one-pass', sec8 line contains '占位·finalize 同窗回填'.
import io

P = "research/PERPETUAL_N1_W258_PREREG.md"
lines = io.open(P, encoding="utf-8").read().splitlines(keepends=False)

sec7_new = """- 账本恒等式：prev **989,735** + 2,200 = **991,935 EXACT**（voids LOWAMP-P1/P2 同法应用·append_one_pass）。
- 合并池：**K=565,520 EXACT**（563,320+2,200）；merged mu **-0.092767**（-0.09276683318008204）/ sigma **0.245034**（0.24503365523916693）/ **se_mu@K=565,520=0.000326**（W257 键 0.000326 → **持平**·≤ 键 PASS）；W258-only mu **-0.095658**（-0.09565813636363636）/ sigma **0.246112**（0.2461119919383847）。
- §5 五预测键机证件（results/_r1062bmc_w258_fivekeys.json·**ALL PASS**）：①W258-only vs merged mu gap **0.002891**<0.02 ✓（merged vs W257 键差 0.0000113 ✓——W257 链内新大 0.0141 后本波回落小 gap 族）②sigma rel **+0.0000166%**<±10% ✓ ③A 档 p95 **0.310800** vs 键 0.2973 差 **+0.013500**<0.05 ✓ ④K-lift 线移 **0.000000**（line_pre 1.1948→line_merged 1.1948 @n_eff held 989,735）≤±0.02 ✓ ⑤se_mu **0.000326**≤0.000326 ✓（**持平**——W256 0.000327→W257 0.000326→本波 0.000326·K 加深 2,200 后持平=测量面如实注记）。
- 六门探针：results/_r1062bmc_w258_sixgate.json **ALL PASS**（PRE-FINALIZE 相位先过——W217-debt standing law 执行·**连续第 20 波正相位**；gate-1 n1 三重恒等 **381d26df7e6d6b7f**（worktree==freeze receipt post==LANDED git blob @ 37ccebffd）零漂移——本波零 post-splice heal（splice commit 37ccebffd=worktree 字节直落）+ pf 面 worktree==receipt post **dca9e66660f0c4ac**（git-diff-empty 披露）+ wave-row faces==freeze bands + banned rc0 + pf selftest + n1 selftest + shards 12/12 + seed_admit FREE verbatim base=582901 span=2000 / base=584901 span=200 + W257 boundary 580701/582701 kept）。
- canon flip 态：**NOT PERFORMED BY THIS WAVE -- GOVERNANCE PROPOSAL FACE ONLY (K2200 SAME LAW)**（governance proposal face only·K2200 同法）。
- 引擎烧录：engine self-burn **12/12**（shard 0-11·常驻引擎 materializer mtime-watch 自见 auto-ignite·splice 落盘 37ccebffd 后自烧·ledger appends 122485949+cc72046d7 batched 6+6 self-commit·本窗 r1062 收口）。
- audit 段：machine=bm-c·finalize_only=true·shards_consumed 12/12 文件名全录。
- 诚实披露：K-lift **0.000000**（W257 -0.0001→本波 0.0000=回零·远在 ±0.02 断言带内·nulls-deepening 测量面非注册收益）；A p95 0.310800 较 W257 键 0.2973 差 **+0.0135**（2,000 试 A 切片抽样波动·W254 -0.0030/W255 +0.0330/W256 -0.0315/W257 -0.0134 后本波 +0.0135=**双向波动链续第八证**·带内 PASS 如实注记）；W258-only vs merged gap 0.002891（带内 0.02·W257 链内新大 0.014127 后本波回落小 gap 族·2,200 新种子带抽样面·六键全过如实注记）；se_mu 0.000326（W256 0.000327→W257 0.000326→本波 0.000326·**持平**·≤ 断言 PASS·K 加深 2,200 后持平=测量面如实注记）。"""

sec8_new = """- §5.5 W259+ 投影承接机证：本波 finalize 落地=**W259 席开放**——下一位 freezer 必须 seat-first publish（O-20261010-2350 §2）+post-W258 universe live re-derive（禁转录 r587 律）+derive B 时预留本波 A 窗 582_901..584_900 与 B 带 584_901..585_100（W258 §5.5 face：naive W259 A 起点 584_901 将被注册 W258 B 带 584_901..585_100 拒=staircase-affects-A **8th consecutive A-hop 预期**→A first-clean 将再上移；B own-A reservation cascade 落位相应上移·B naive 585_101..585_300 CLEAN 但落投影 A 窗内=W259p_B_lands_inside_W259p_A_naive face 延续；**W259 冻结方禁假设 A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**——W251 起 staircase affects A·W252..W258=A/B 双 1-hop 形态连续七波如实注记；verify at W259 prereg，hop 链逐跳在 probe 回执复核）。
- 宝藏与方法论捕获问：**本批零新方法论面**（W258 周期=正典链续接·五面全带内·六闸/五键/终定全正相位一次过——无新机制/无新根因；sixgate/fivekeys/sec78 derive=E63 canon-clone 链复用零新卡；宝藏登记零新条（既有链法覆盖）；se_mu 持平与 A p95 双向波动=测量面如实注记非新方法论）。
- 诚实披露面：本窗=**52nd-gen absorb 续接**（死窗 r1062 段：editor derive canon-clone（machine-splice builder _r1062bmc_build_editor.py·E63 10th-gen 四级 replay）+needle preflight 134 faces ALL PASS+splice 落盘 commit 37ccebffd〔NEW FACE: kept/dropped split boundary 239->240 per frozen W258 prereg sec.3 mandate·kept W211..W239 29+dropped W240..W256 17+fresh W240..W257 18=116 parity rows〕+引擎 mtime-watch 自烧 12/12〔ledger appends 122485949+cc72046d7 self-commit〕后死 pre-closeout——本窗吸收续接：estate 机器验证〔n1 三重恒等+pf git-diff-empty+shards 12/12+banned ADMIT re-run〕+六门 PRE-FINALIZE ALL PASS〔连续第 20 波正相位〕+finalize one-pass 991,935/K=565,520 EXACT+五键 6/6+§7/§8 回填+W259 席位发布）；W258 席位=bm-c own-seat（第 78 枚 own·第 248 引擎波·prereg 824b46d31·seat MSG-20261017-0517-bmc-w258-seat origin d0d0d04a4 先于冻结发布〔r565 律〕）。"""

i7 = [n for n, l in enumerate(lines) if '占位·finalize one-pass' in l]
i8 = [n for n, l in enumerate(lines) if '占位·finalize 同窗回填' in l]
assert len(i7) == 1, "sec7 placeholder line not found exactly once: %r" % i7
assert len(i8) == 1, "sec8 placeholder line not found exactly once: %r" % i8
lines[i7[0]] = sec7_new
lines[i8[0]] = sec8_new
t = "\n".join(lines) + "\n"
assert t.count("占位") == 0, "residual placeholders remain"
io.open(P, "w", encoding="utf-8", newline="").write(t)
print("BACKFILL-OK bytes=%d placeholders=0" % len(t.encode("utf-8")))
