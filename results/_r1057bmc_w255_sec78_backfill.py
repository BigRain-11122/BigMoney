# -*- coding: utf-8 -*-
# r1057 bm-c: W255 prereg sec.7/8 mechanical backfill (finalize-window, bm-c
# r1055 W254 范式). Frozen-judgment faces untouched -- backfill limited to
# sec.7/8 placeholder lines per the prereg tail law (回填限 §7/§8).
import io

P = "research/PERPETUAL_N1_W255_PREREG.md"
t = io.open(P, encoding="utf-8").read()

sec7_old = "- （占位·finalize one-pass 后回填：账本恒等式/合并池 K/merged mu·sigma·se_mu/K-lift 对照/§5 五预键机证件/六门探针/canon flip 态/audit 段——bm-c r1055 W254 §7 范式）"
sec8_old = "- （占位·finalize 同窗回填：§5.5 W256+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——bm-c r1055 W254 §8 范式）"

sec7_new = """- 账本恒等式：prev **983,135** + 2,200 = **985,335 EXACT**（voids LOWAMP-P1/P2 同法应用·append_one_pass）。
- 合并池：**K=558,920 EXACT**（556,720+2,200）；merged mu **-0.092708**（-0.09270818864953839）/ sigma **0.245039**（0.24503941785778824）/ **se_mu@K=558,920=0.000328**（W254 键 0.000328 → **持平**·≤ 键 PASS）；W255-only mu **-0.085254**（-0.08525445454545455）/ sigma **0.247112**（0.24711158030834052）。
- §5 五预测键机证件（results/_r1057bmc_w255_fivekeys.json·**ALL PASS**）：①W255-only vs merged mu gap **0.007454**<0.02 ✓（merged vs W254 键差 0.0000295 ✓）②sigma rel **+0.0000345%**<±10% ✓ ③A 档 p95 **0.342200** vs 键 0.3092 差 **+0.033000**<0.05 ✓ ④K-lift 线移 **+0.000100**（line_pre 1.194500→line_merged 1.194600 @n_eff held 983,135）≤±0.02 ✓ ⑤se_mu **0.000328**≤0.000328 ✓（**持平**·W250..W254 连续收窄链首次持平·测量面如实注记）。
- 六门探针：results/_r1057bmc_w255_sixgate.json **ALL PASS**（PRE-FINALIZE 相位先过——W217-debt standing law 执行·**连续第 17 波正相位**；gate-1 n1 三重恒等 **c6dfb4291c09be1e**（worktree==freeze receipt post==LANDED git blob @ e166afc6c）零漂移——本波零 post-splice heal（splice commit e166afc6c=healed worktree 字节直落·2 needle heals+2 blanket-duplication sub heals pre-splice 闸内修复）+ pf 面 worktree==receipt post **d4a9d7164ba9490e**（CRLF 工作树面·commit blob=LF 归一化同内容·git-diff-empty 披露）+ wave-row faces==freeze bands + banned rc0 + pf selftest + n1 selftest + shards 12/12 + seed_admit FREE verbatim base=576301 span=2000 / base=578301 span=200 + W254 boundary 574101/576101 kept）。
- canon flip 态：**NOT PERFORMED BY THIS WAVE -- GOVERNANCE PROPOSAL FACE ONLY (K2200 SAME LAW)**（governance proposal face only·K2200 同法）。
- 引擎烧录：engine self-burn **12/12**（shard 0-11·常驻引擎 materializer mtime-watch 自见 auto-ignite·e166afc6c splice 落盘后自烧·ledger appends b1414b81a+f931cf102 batched 6+6 self-commit·本窗 r1057 收口）。
- audit 段：machine=bm-c·finalize_only=true·shards_consumed 12/12 文件名全录。
- 诚实披露：K-lift **+0.000100**=带内微移段（W136..W254 先例全在 ±0.0003 内·W253 0.0000→W254 -0.0001→本波 +0.0001 回摆=双向波动链第五证·远在 ±0.02 断言带内·nulls-deepening 测量面非注册收益）；A p95 0.342200 较 W254 键 0.3092 差 **+0.0330**（2,000 试 A 切片抽样波动·测量面非注册收益·W252 +0.0046/W253 -0.0077/W254 -0.0030 反向互证后本波正向大摆=**带内波动链最大单波摆幅**·带内 PASS 如实注记）；W255-only vs merged gap 0.007454（带内 0.02·W250 0.000511/W251 0.004986/W252 0.002565/W253 0.000189/W254 0.000324→本波 0.007454=**链内最大**·2,000 新种子带抽样面·六键全过如实注记）；se_mu 0.000328 持平（W250 0.000331→…→W253 0.000329→W254 0.000328→本波 0.000328·≤ 断言 PASS·**收窄链首次持平**·K 加深 2,200 后持平=测量面如实注记）。"""

sec8_new = """- §5.5 W256+ 投影承接机证：本波 finalize 落地=**W256 席开放**——下一位 freezer 必须 seat-first publish（O-20261010-2350 §2）+post-W255 universe live re-derive（禁转录 r587 律）+derive B 时预留本波 A 窗 576_301..578_300 与 B 带 578_301..578_500（W255 §5.5 face：A naive 578_301..580_300 CLEAN-at-naive pre-W255 **BUT post-W255 注册后起点 578_301 被注册 W255 B 带 578_301..578_500 拒**=staircase-affects-A **5th consecutive A-hop 预期**→A first-clean 将再上移；B own-A reservation cascade 落位相应上移·B naive 578_501..578_700 CLEAN 但落投影 A 窗内=W256p_B_lands_inside_W256p_A_naive face 延续；**W256 冻结方禁假设 A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**——W251 起 staircase affects A·W252/W253/W254/W255=A/B 双 1-hop 形态连续四波如实注记；W256 derive 必须在 post-W255 注册宇宙重 derive 且预留本波 A 窗+本波 B 带——leg2 律/E36 卡·W141 先例；verify at W256 prereg，hop 链逐跳在 probe 回执复核）。
- 宝藏与方法论捕获问：**本批零新方法论面**（W255 周期=正典链续接·五面全带内·六闸/五键/终定全正相位一次过——无新机制/无新根因；sixgate/fivekeys/sec78 derive=E63 canon-clone 链复用零新卡；宝藏登记零新条（既有链法覆盖）；se_mu 收窄链首次持平面与 A-p95 链内最大正摆=测量面如实注记非新方法论）。
- 诚实披露面：本窗=**48th-gen absorb 续接**（死窗 r1057 段：editor derive+freeze_edits+splice e166afc6c 落地并 push+引擎 mtime-watch 自烧 12/12〔ledger appends b1414b81a+f931cf102 self-commit〕后死 pre-closeout——本窗吸收续接：六门 PRE-FINALIZE ALL PASS〔连续第 17 波正相位〕+finalize one-pass 985,335/K=558,920 EXACT+五键 6/6+§7/§8 回填+W256 席位发布）；W255 席位=bm-c own-seat（第 75 枚 own·第 245 引擎波·prereg 72d292ea3·seat MSG-20261016-22xx-bmc-w255-seat origin cb79242ed 先于冻结发布〔r565 律〕）。"""

assert t.count(sec7_old) == 1, "sec7 placeholder not found exactly once"
assert t.count(sec8_old) == 1, "sec8 placeholder not found exactly once"
t = t.replace(sec7_old, sec7_new).replace(sec8_old, sec8_new)
io.open(P, "w", encoding="utf-8", newline="").write(t)
print("BACKFILL-OK bytes=%d" % len(t.encode("utf-8")))
