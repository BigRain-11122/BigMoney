# -*- coding: utf-8 -*-
# r1048 bm-c: W251 prereg sec.7/sec.8 finalize-window backfill.
# Law: backfill-limited (sec.7/8 only), needle = regex placeholder lines
# (count-asserted exactly 1 each), zero hand-copied CJK needles -- anchors
# are the ASCII faces 占位·finalize prefix (authored, not console-copied).
import io
import re

PATH = "research/PERPETUAL_N1_W251_PREREG.md"
t = io.open(PATH, encoding="utf-8").read()

SEC7 = """- 账本恒等式：prev **974,135** + 2,200 = **976,535 EXACT**（voids LOWAMP-P1/P2 同法应用·append_one_pass）。
- 合并池：**K=550,120 EXACT**（547,920+2,200）；merged mu **-0.092750**（-0.09274993928597397）/ sigma **0.245036**（0.24503622147677206）/ **se_mu@K=550,120=0.000330**（W250 键 0.000331 → 收窄·≤ 键 PASS）；W251-only mu **-0.087764** / sigma **0.245331**。
- §5 五预测键机证件（results/_r1048bmc_w251_fivekeys.json·ALL PASS）：①W251-only vs merged mu gap **0.004986**<0.02 ✓（merged vs W250 键差 0.000020 ✓）②sigma rel **0.00046%**<±10% ✓ ③A 档 p95 **0.315300** vs 键 0.3235 差 **-0.008200**<0.05 ✓ ④K-lift 线移 **0.000100**（line_pre 1.194000→line_merged 1.194100 @n_eff held 974,135）≤±0.02 ✓ ⑤se_mu **0.000330**≤0.000331 ✓。
- 六门探针：results/_r1048bmc_w251_sixgate.json **ALL PASS**（PRE-FINALIZE 相位先过——W217-debt standing law 执行·连续第 13 波正相位；gate-1 三重恒等 worktree==freeze receipt post==LANDED git blob n1 c9de218d7c362499 / pf d88cd951f44dfaf6 零漂移——本波零 post-splice heal（splice commit c813471cd=worktree 字节直落·E70 re-anchor 无需面）+ wave-row faces==freeze bands + banned rc0 + pf selftest + n1 selftest + shards 12/12 + seed_admit FREE verbatim base=567501 span=2000 / base=569501 span=200 + W250 boundary 565501/545101 kept）。
- canon flip 态：**NOT PERFORMED BY THIS WAVE -- GOVERNANCE PROPOSAL FACE ONLY (K2200 SAME LAW)**（governance proposal face only·K2200 同法）。
- 引擎烧录：engine self-burn **12/12**（shard 0-11·常驻引擎 materializer mtime-watch 自见 auto-ignite·r1048 splice c813471cd 落盘后自烧·ledger appends c15c32afd+e46094052 batched 6+6 self-commit·本窗 r1048 收口）。
- audit 段：machine=bm-c·finalize_only=true·shards_consumed 12/12 文件名全录。
- 诚实披露：K-lift **0.000100**=先例链内首个非零微移段（W136..W250 全在 ±0.0003 内·机读可复核·本移 0.0001 仍远在 ±0.02 断言带内·nulls-deepening 测量面非注册收益）；A p95 0.315300 较 W250 键 0.3235 差 -0.0082（2,000 试 A 切片抽样波动·测量面非注册收益·W250 波同面 +0.0077 反向·双向波动先例互证）；W251-only vs merged gap 0.004986（单波切片 mu 上偏·带内 0.02·W249 波 0.00485/W250 波 0.000511→本波 0.00499=单波切片波动回归常态面）；se_mu 0.000331→0.000330 收窄（K 增 2,200 后 6 位小数面收窄·≤ 断言 PASS·测量面如实注记）。
"""

SEC8 = """- §5.5 W252+ 投影承接机证：本波 finalize 落地=**W252 席开放**——下一位 freezer 必须 seat-first publish（O-20261010-2350 §2）+post-W251 universe live re-derive（禁转录 r587 律）+derive B 时预留本波 A 窗与 B 带（W251 §5.5 face：A naive 569_501..571_500 预投影 CLEAN（hops=0·pre-W251 宇宙零活点拒）/ B naive 569_701..569_900 CLEAN-at-naive **但落投影 A 窗 569_501..571_500 内**=staircase re-emergence face——W251 B 569_501..569_700 注册后 B 带首次落入 W251 A 2,000-span ladder 区间·W252 B derive with own-A reservation 将 hop past 571_500→~571_501..571_700 staircase 面重现；**W252 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace**（seed-gap face 承袭 W239..W250·W251 起 B 入 A-ladder 区=above-own-A 新形态如实注记）；W252 derive 必须在 post-W251 注册宇宙重 derive 且预留本波 A 窗 567_501..569_500+本波 B 带 569_501..569_700——leg2 律/E36 卡·W141 先例；verify at W252 prereg，hop 链逐跳在 probe 回执复核）。
- 宝藏与方法论捕获问：**本批零新方法论面**（W251 周期=正典链续接·五面全带内·六闸/五键/终定全正相位一次过——无新机制/无新根因/零 heal 披露；fivekeys derive=E63 canon-clone 链复用零新卡；宝藏登记零新条（既有链法覆盖））。
- 诚实披露面：本窗=canonical 续接（死窗 r1048-predecessor 09:2x-09:3x 执行 splice 09:31-09:32〔commit c813471cd 落地〕+engine self-burn 12/12〔ledger appends c15c32afd+e46094052 self-commit〕+sixgate script authored 09:35:45 未跑即死——state 停在 round_no=1048·本窗 r1048 续接完成 sixgate〔首跑 ALL PASS·零 heal 零 re-anchor 面〕+finalize one-pass+五键+§7/§8 回填）；六门 PRE-FINALIZE 相位正确（engine burn 完成后 finalize 前·连续第 13 波）；W251 席位=bm-c own-seat（第 71 枚 own·第 241 引擎波·prereg 9f5f106d6·splice c813471cd）。
"""

pat7 = re.compile(r"\n- （占位·finalize one-pass[^\n]*\n")
pat8 = re.compile(r"\n- （占位·finalize 同窗[^\n]*\n")
n7 = len(pat7.findall(t))
n8 = len(pat8.findall(t))
assert n7 == 1, f"sec7 placeholder count {n7} != 1"
assert n8 == 1, f"sec8 placeholder count {n8} != 1"
t2 = pat7.sub("\n" + SEC7, t, count=1)
t2 = pat8.sub("\n" + SEC8, t2, count=1)

# MUST faces present after backfill
must = ["976,535 EXACT", "K=550,120 EXACT", "_r1048bmc_w251_fivekeys.json",
        "_r1048bmc_w251_sixgate.json", "c813471cd", "c9de218d7c362499",
        "W252 席开放", "staircase re-emergence face", "9f5f106d6"]
for m in must:
    assert m in t2, f"MUST face missing after backfill: {m!r}"
# MUST_NOT: placeholders gone
assert "占位·finalize" not in t2, "placeholder survived"

io.open(PATH, "w", encoding="utf-8", newline="").write(t2)
print("BACKFILL-OK bytes=%d (+%d)" % (len(t2.encode("utf-8")),
                                      len(t2.encode("utf-8")) - len(t.encode("utf-8"))))
