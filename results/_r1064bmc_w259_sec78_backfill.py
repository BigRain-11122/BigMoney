# -*- coding: utf-8 -*-
"""r1064 bm-c: W259 prereg sec.7/8 finalize backfill (r1062 W258 template, E63 canon-clone).

Replaces the two frozen placeholders in research/PERPETUAL_N1_W259_PREREG.md with
measured finalize faces. Count-asserted gates: each needle must appear exactly once.
Backfill is the ONLY permitted post-freeze edit (frozen-face law).
"""
import io
import sys

PATH = "research/PERPETUAL_N1_W259_PREREG.md"

S7_NEEDLE = "- （占位·finalize one-pass 后回填：账本恒等式/合并池 K/merged mu·sigma·se_mu/K-lift 对照/§5 五预键机证件/六门探针/canon flip 态/audit 段——bm-c r1062 W258 §7 范式）"
S8_NEEDLE = "- （占位·finalize 同窗回填：§5.5 W260+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——bm-c r1062 W258 §8 范式）"

S7_BACKFILL = """- 账本恒等式：prev **991,935** + 2,200 = **994,135 EXACT**（voids LOWAMP-P1/P2 同法应用·append_one_pass）。
- 合并池：**K=567,720 EXACT**（565,520+2,200）；merged mu **-0.092735**（-0.09273526298175157）/ sigma **0.245038**（0.24503750022170157）/ **se_mu@K=567,720=0.000325**（W258 键 0.000326 → **收窄·≤ 键 PASS**）；W259-only mu **-0.084620**（-0.08462）/ sigma **0.245945**（0.2459453776097889）。
- §5 五预测键机证件（results/_r1064bmc_w259_fivekeys.json·**ALL PASS**）：①W259-only vs merged mu gap **0.008115**<0.02 ✓（merged vs W258 键差 0.0000316 ✓——小 gap 族延续）②sigma rel **+0.0016%**<±10% ✓ ③A 档 p95 **0.323400** vs 键 0.3108 差 **+0.012600**<0.05 ✓ ④K-lift 线移 **0.000000**（line_pre 1.1949→line_merged 1.1949 @n_eff held 991,935）≤±0.02 ✓ ⑤se_mu **0.000325**≤0.000326 ✓（**收窄**——W257 0.000326→W258 0.000326→本波 0.000325·K 加深 2,200 后收窄=测量面如实记注）。
- 六门探针：results/_r1064bmc_w259_sixgate.json **ALL PASS**（PRE-FINALIZE 相位先过——W217-debt standing law 执行·**连续第 21 波正相位**；gate-1 n1 三重恒等 **57a139af18df580d**（worktree==freeze receipt post==LANDED git blob @ 89aeea31b）零漂移——本波零 post-splice heal（splice commit 89aeea31b=worktree 字节直落）+ pf 面 worktree==receipt post **bfd877ee61d6b456**（git-diff-empty 披露）+ wave-row faces==freeze bands + banned rc0 + pf selftest + n1 selftest + shards 12/12 + seed_admit FREE verbatim base=585101 span=2000 / base=587101 span=200 + W258 边界 582901/584901 kept）。
- canon flip 态：**NOT PERFORMED BY THIS WAVE -- GOVERNANCE PROPOSAL FACE ONLY (K2200 SAME LAW)**（governance proposal face only·K2200 同法）。
- 引擎烧录：engine self-burn **12/12**（shard 0-11·常驻引擎 materializer mtime-watch 自见 auto-ignite·splice 落盘 89aeea31b 后自烧·ledger appends 85e44f6a6+778bd1c04+ceeb47cda batched 6+4+2 self-commit·本窗 r1064 收口）。
- audit 段：machine=bm-c·finalize_only=true·shards_consumed 12/12 文件名全录。
- 诚实披露：K-lift **0.000000**（W258 0.0000→本波 0.0000=持续零移·远在 ±0.02 断言带内·nulls-deepening 测量面非注册收益）；A p95 0.323400 较 W258 键 0.3108 差 **+0.0126**（2,000 试 A 切片抽样波动·W255 +0.0330/W256 -0.0315/W257 -0.0134/W258 +0.0135 后本波 +0.0126=双向波动链续第九证·带内 PASS 如实记注）；W259-only vs merged gap 0.008115（带内 0.02·W257 链内 0.014127/W258 0.002891 后本波 0.008115 小 gap 族·2,200 新种子带抽样面·六键全过如实记注）；se_mu 0.000325（W256 0.000327→W257 0.000326→W258 0.000326→本波 0.000325·**收窄**·≤ 断言 PASS·K 加深 2,200 后收窄=测量面如实记注）。"""

S8_BACKFILL = """- §5.5 W260+ 投影承接机证：本波 finalize 落地=**W260 席开放**——下一位 freezer 必须 seat-first publish（O-20261010-2350 §2）+post-W259 universe live re-derive（禁转录 r587 律）+derive B 时预留本波 A 窗 585_101..587_100 与 B 带 587_101..587_300（W259 §5.5 face：naive W260 A 起点 587_101 将被注册 W259 B 带 587_101..587_300 拒=staircase-affects-A **NINTH consecutive A-hop 预期**→A first-clean 将再上移；B own-A reservation cascade 落位相应上移·B naive 587_301..587_500 CLEAN 但落投影 A 窗内=W260p_B_lands_inside_W260p_A_naive face 延续；**W260 冻结方禁假设 A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**——W251 起 staircase affects A·W252..W259=A/B 双 1-hop 形态连续八波如实记注；verify at W260 prereg，hop 链逐跳在 probe 回执复核）。
- 宝藏与方法论捕获问：**本批零新方法论面**（W259 周期=正典链续接·五键全带内·六门/finalize 全正相位一次过——无新机制/无新根因；sixgate/fivekeys/sec78 derive=E63 canon-clone 链复用零新卡；宝藏登记零新条（既有链法覆盖）；se_mu 收窄与 A p95 双向波动=测量面如实记注非新方法论）。
- 诚实披露面：本窗=**54th-gen absorb 续接**（死窗 r1064 段：editor derive（dead-r1063 预建件 08:43 执行）+freeze edits+splice 落盘 commit 89aeea31b〔4 disclosed gate-list needle heals：w244_a frozen-verbatim heal / r1064 freeze-window stamp heal / 248th anti-gate heal / 247-129-77 anti-gate heal·selftest 9/9〕+引擎 mtime-watch 自烧 12/12〔ledger appends 85e44f6a6+778bd1c04+ceeb47cda batched 6+4+2 self-commit〕+六门 PRE-FINALIZE ALL PASS〔连续第 21 波〕+finalize one-pass 994,135/K=567,720 EXACT 后死 pre-closeout——本窗吸收续接：estate 机器验证〔六门 json 三重恒等 57a139af18df580d+finalize 产物账本恒等 EXACT+五键本窗补跑 6/6 ALL PASS〕+§7/§8 回填+W260 席位发布）；W259 席位=bm-c own-seat（冻结时 engine_owner 78 行+候选=第 79 枚 own·prereg b709bc2cc·seat MSG-20261017-0704-bmc-w259-seat origin 16dba0e70 先于冻结发布〔r565 律〕）。"""


def main():
    t = io.open(PATH, encoding="utf-8", newline="").read()
    n7 = t.count(S7_NEEDLE)
    n8 = t.count(S8_NEEDLE)
    assert n7 == 1, f"S7 needle count {n7} != 1"
    assert n8 == 1, f"S8 needle count {n8} != 1"
    t2 = t.replace(S7_NEEDLE, S7_BACKFILL).replace(S8_NEEDLE, S8_BACKFILL)
    assert t2.count("（占位·finalize") == 0, "placeholder residue after backfill"
    assert t2.count("57a139af18df580d") >= 2, "gate-1 sha16 must appear in sec.7"
    assert t2.count("994,135 EXACT") == 1, "ledger identity line"
    assert t2.count("567,720 EXACT") == 2, "K identity line (sec.7 identity + sec.8 absorb disclosure)"
    io.open(PATH, "w", encoding="utf-8", newline="").write(t2)
    # read-back verification
    t3 = io.open(PATH, encoding="utf-8", newline="").read()
    assert t3 == t2, "read-back mismatch"
    print("BACKFILL OK; bytes", len(t), "->", len(t3))


if __name__ == "__main__":
    main()
