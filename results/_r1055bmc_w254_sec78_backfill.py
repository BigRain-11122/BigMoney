# -*- coding: utf-8 -*-
# r1055 bm-c: W254 prereg sec.7/8 mechanical backfill (finalize-window, bm-c
# r1053 W253 范式). Frozen-judgment faces untouched -- backfill limited to
# sec.7/8 placeholder lines per the prereg tail law (回填限 §7/§8).
import io

P = "research/PERPETUAL_N1_W254_PREREG.md"
t = io.open(P, encoding="utf-8").read()

sec7_old = "- （占位·finalize one-pass 后回填：账本恒等式/合并池 K/merged mu·sigma·se_mu/K-lift 对照/§5 五预键机证件/六门探针/canon flip 态/audit 段——bm-c r1053 W253 §7 范式）"
sec8_old = "- （占位·finalize 同窗回填：§5.5 W255+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——bm-c r1053 W253 §8 范式）"

sec7_new = """- 账本恒等式：prev **980,935** + 2,200 = **983,135 EXACT**（voids LOWAMP-P1/P2 同法应用·append_one_pass）。
- 合并池：**K=556,720 EXACT**（554,520+2,200）；merged mu **-0.092738**（-0.0927376436988073）/ sigma **0.245031**（0.2450309685260551）/ **se_mu@K=556,720=0.000328**（W253 键 0.000329 → 连续收窄·≤ 键 PASS）；W254-only mu **-0.092414**（-0.09241377272727273）/ sigma **0.240817**（0.24081711527035077）。
- §5 五预测键机证件（results/_r1055bmc_w254_fivekeys.json·ALL PASS）：①W254-only vs merged mu gap **0.000324**<0.02 ✓（merged vs W253 键差 0.0000013 ✓）②sigma rel **-0.0000685%**<±10% ✓ ③A 档 p95 **0.309200** vs 键 0.3122 差 **-0.003000**<0.05 ✓ ④K-lift 线移 **-0.000100**（line_pre 1.194500→line_merged 1.194400 @n_eff held 980,935）≤±0.02 ✓ ⑤se_mu **0.000328**≤0.000329 ✓。
- 六门探针：results/_r1055bmc_w254_sixgate.json **ALL PASS**（PRE-FINALIZE 相位先过——W217-debt standing law 执行·连续第 16 波正相位；gate-1 n1 三重恒等 **7b550e65716e0ada**（worktree==freeze receipt post==LANDED git blob @ 3eb691575）零漂移——本波零 post-splice heal（splice commit 3eb691575=healed worktree 字节直落·死窗+治愈窗 4 缺陷类 pre-splice 计数断言闸内修复）+ pf 面 worktree==receipt post **924e87b3f02afb72**（CRLF 工作树面·commit blob=LF 归一化同内容·git-diff-empty 披露）+ wave-row faces==freeze bands + banned rc0 + pf selftest + n1 selftest + shards 12/12 + seed_admit FREE verbatim base=574101 span=2000 / base=576101 span=200 + W253 boundary 571901/573901 kept）。
- canon flip 态：**NOT PERFORMED BY THIS WAVE -- GOVERNANCE PROPOSAL FACE ONLY (K2200 SAME LAW)**（governance proposal face only·K2200 同法）。
- 引擎烧录：engine self-burn **12/12**（shard 0-11·常驻引擎 materializer mtime-watch 自见 auto-ignite·3eb691575 splice 落盘后自烧·ledger appends c211d1269+fa2bc55e5 batched 6+6 self-commit·本窗 r1055 收口）。
- audit 段：machine=bm-c·finalize_only=true·shards_consumed 12/12 文件名全录。
- 诚实披露：K-lift **-0.000100**=带内微移段（W251 0.0001→W252 0.0001→W253 0.0000→本波 -0.0001·W136..W253 先例全在 ±0.0003 内·零位邻域=先例链内·远在 ±0.02 断言带内·nulls-deepening 测量面非注册收益）；A p95 0.309200 较 W253 键 0.3122 差 **-0.0030**（2,000 试 A 切片抽样波动·测量面非注册收益·W252 +0.0046/W253 -0.0077 反向互证·本波回摆=双向波动链第四证）；W254-only vs merged gap 0.000324（带内 0.02·W250 0.000511/W251 0.004986/W252 0.002565/W253 0.000189→本波 0.000324=链内）；se_mu 0.000328 连续收窄（W250 0.000331→W251 0.000330→W252 0.000330→W253 0.000329→本波 0.000328·≤ 断言 PASS·测量面如实注记）。"""

sec8_new = """- §5.5 W255+ 投影承接机证：本波 finalize 落地=**W255 席开放**——下一位 freezer 必须 seat-first publish（O-20261010-2350 §2）+post-W254 universe live re-derive（禁转录 r587 律）+derive B 时预留本波 A 窗 574_101..576_100 与 B 带 576_101..576_300（W254 §5.5 face：A naive 576_101..578_100 CLEAN-at-naive pre-W254 **BUT post-W254 注册后起点 576_101 被注册 W254 B 带 576_101..576_300 拒**=staircase-affects-A **4th consecutive A-hop 预期**→A first-clean 将再上移；B own-A reservation cascade 落位相应上移·B naive 576_301..576_500 CLEAN 但落投影 A 窗内=W255p_B_lands_inside_W255p_A_naive face 延续；**W255 冻结方禁假设 A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**——W251 起 staircase affects A·W252/W253/W254=A/B 双 1-hop 形态连续三波如实注记；W255 derive 必须在 post-W254 注册宇宙重 derive 且预留本波 A 窗+本波 B 带——leg2 律/E36 卡·W141 先例；verify at W255 prereg，hop 链逐跳在 probe 回执复核）。
- 宝藏与方法论捕获问：**本批零新方法论面**（W254 周期=正典链续接·五面全带内·六闸/五键/终定全正相位一次过——无新机制/无新根因；sixgate/fivekeys derive=E63 canon-clone 链复用零新卡；宝藏登记零新条（既有链法覆盖）；六门克隆首跑 FAIL→PF face 字节恒等误断言（CRLF 工作树 vs LF blob）→按 W253 母版 git-diff-empty 正法当窗治愈=E73 母版克隆保真律执法面·零 estate 缺陷）。
- 诚实披露面：本窗=45th-gen absorb 续接（死窗双段：r1054 收口后 20:07-20:39 死窗 authored editor clone〔_w254bmc_editor_clone.py〕；21:02 治愈窗 healed 4 缺陷类+splice 落地 3eb691575+engine self-burn 12/12〔ledger appends c211d1269+fa2bc55e5 self-commit〕+V5 QC 板四件半途——state 停在 round_no=1055·本窗 r1055 续接完成六门〔首跑 pf_landed 误断言 FAIL→治愈后 ALL PASS〕+finalize one-pass 983,135/K=556,720 EXACT+五键 6/6+§7/§8 回填）；六门 PRE-FINALIZE 相位正确（连续第 16 波）；W254 席位=bm-c own-seat（第 74 枚 own·第 244 引擎波·prereg e2c4b543e·seat MSG-20261016-14xx-bmc-w254-seat origin fa70f3765 先于冻结发布〔r565 律〕）。"""

assert t.count(sec7_old) == 1, "sec7 placeholder not found exactly once"
assert t.count(sec8_old) == 1, "sec8 placeholder not found exactly once"
t = t.replace(sec7_old, sec7_new).replace(sec8_old, sec8_new)
io.open(P, "w", encoding="utf-8", newline="").write(t)
print("BACKFILL-OK bytes=%d" % len(t.encode("utf-8")))
