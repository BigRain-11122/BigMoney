# -*- coding: utf-8 -*-
# r1053 bm-c: W253 prereg sec.7/8 mechanical backfill (finalize-window, bm-c
# r1050 W252 范式). Frozen-judgment faces untouched -- backfill limited to
# sec.7/8 placeholder lines per the prereg tail law (回填限 §7/§8).
import io

P = "research/PERPETUAL_N1_W253_PREREG.md"
t = io.open(P, encoding="utf-8").read()

sec7_old = "- （占位·finalize one-pass 后回填：账本恒等式/合并池 K/merged mu·sigma·se_mu/K-lift 对照/§5 五预键机证件/六门探针/canon flip 态/audit 段——bm-c r1050 W252 §7 范式）"
sec8_old = "- （占位·finalize 同窗回填：§5.5 W254+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——bm-c r1050 W252 §8 范式）"

sec7_new = """- 账本恒等式：prev **978,735** + 2,200 = **980,935 EXACT**（voids LOWAMP-P1/P2 同法应用·append_one_pass）。
- 合并池：**K=554,520 EXACT**（552,320+2,200）；merged mu **-0.092739**（-0.09273892862295319）/ sigma **0.245048**（0.24504775480421728）/ **se_mu@K=554,520=0.000329**（W252 键 0.000330 → 首度再收窄·≤ 键 PASS）；W253-only mu **-0.092550**（-0.0925495）/ sigma **0.245070**（0.2450704959871504）。
- §5 五预测键机证件（results/_r1053bmc_w253_fivekeys.json·ALL PASS）：①W253-only vs merged mu gap **0.000189**<0.02 ✓（merged vs W252 键差 0.0000008 ✓）②sigma rel **-0.000059%**<±10% ✓ ③A 档 p95 **0.312200** vs 键 0.3199 差 **-0.007700**<0.05 ✓ ④K-lift 线移 **0.000000**（line_pre 1.194400→line_merged 1.194400 @n_eff held 978,735）≤±0.02 ✓ ⑤se_mu **0.000329**≤0.000330 ✓。
- 六门探针：results/_r1053bmc_w253_sixgate.json **ALL PASS**（PRE-FINALIZE 相位先过——W217-debt standing law 执行·连续第 15 波正相位；gate-1 n1 三重恒等 **c8218b4deb2540b5**（worktree==freeze receipt post==LANDED git blob @ c9b4fd855）零漂移——本波零 post-splice heal（splice commit c9b4fd855=worktree 字节直落·死窗 4 缺陷类 pre-splice 计数断言闸内修复）+ pf 面 worktree==receipt post **24fe08e65ef219c8**（CRLF 工作树面·commit blob=LF 归一化同内容·receipt eol.pf_crlf=true 披露）+ wave-row faces==freeze bands + banned rc0 + pf selftest + n1 selftest + shards 12/12 + seed_admit FREE verbatim base=571901 span=2000 / base=573901 span=200 + W252 boundary 569701/571701 kept）。
- canon flip 态：**NOT PERFORMED BY THIS WAVE -- GOVERNANCE PROPOSAL FACE ONLY (K2200 SAME LAW)**（governance proposal face only·K2200 同法）。
- 引擎烧录：engine self-burn **12/12**（shard 0-11·常驻引擎 materializer mtime-watch 自见 auto-ignite·c9b4fd855 splice 落盘后自烧·ledger appends b3caaedc1+bec86607a batched 6+6 self-commit·本窗 r1053 收口）。
- audit 段：machine=bm-c·finalize_only=true·shards_consumed 12/12 文件名全录。
- 诚实披露：K-lift **0.000000**=零移动段（W251/W252 两波 0.0001→本波 0.0000·W136..W252 先例全在 ±0.0003 内·零位=先例链内·远在 ±0.02 断言带内·nulls-deepening 测量面非注册收益）；A p95 0.312200 较 W252 键 0.3199 差 **-0.0077**（2,000 试 A 切片抽样波动·测量面非注册收益·W252 波 +0.0046 反向·双向波动先例互证链三波）；W253-only vs merged gap 0.000189（带内 0.02·W250 0.000511/W251 0.004986/W252 0.002565→本波 0.000189=近链最小）；se_mu 0.000329 收窄（W250 0.000331→W251 0.000330→W252 0.000330 两波持平后首度再收窄·≤ 断言 PASS·测量面如实注记）。"""

sec8_new = """- §5.5 W254+ 投影承接机证：本波 finalize 落地=**W254 席开放**——下一位 freezer 必须 seat-first publish（O-20261010-2350 §2）+post-W253 universe live re-derive（禁转录 r587 律）+derive B 时预留本波 A 窗 571_901..573_900 与 B 带 573_901..574_100（W253 §5.5 face：A naive 573_901..575_900 CLEAN-at-naive pre-W253 **BUT post-W253 注册后 start 被注册 W253 B 带 573_901..574_100 拒**=staircase-affects-A **3rd consecutive A-hop 预期**→A first-clean 将再上移；B own-A reservation cascade 落位相应上移；**W254 冻结方禁假设 A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**——W251 起 staircase affects A·W252/W253=A/B 双 1-hop 形态连续两波如实注记；W254 derive 必须在 post-W253 注册宇宙重 derive 且预留本波 A 窗+本波 B 带——leg2 律/E36 卡·W141 先例；verify at W254 prereg，hop 链逐跳在 probe 回执复核）。
- 宝藏与方法论捕获问：**本批零新方法论面**（W253 周期=正典链续接·五面全带内·六闸/五键/终定全正相位一次过——无新机制/无新根因；sixgate/fivekeys derive=E63 canon-clone 链复用零新卡；宝藏登记零新条（既有链法覆盖））。
- 诚实披露面：本窗=absorb 续接（死窗 14:32-14:36 执行 splice〔commit c9b4fd855 落地〕+engine self-burn 12/12〔ledger appends b3caaedc1+bec86607a self-commit〕——state 停在 round_no=1053·本窗 r1053 续接完成 sixgate〔首跑 ALL PASS·零 heal〕+finalize one-pass+五键+§7/§8 回填）；六门 PRE-FINALIZE 相位正确（连续第 15 波）；W253 席位=bm-c own-seat（第 73 枚 own·第 243 引擎波·prereg 741371846·seat MSG-20261016-12xx-bmc-w253-seat origin f6433ee61 先于冻结发布〔r565 律〕）。"""

assert t.count(sec7_old) == 1, "sec7 placeholder not found exactly once"
assert t.count(sec8_old) == 1, "sec8 placeholder not found exactly once"
t = t.replace(sec7_old, sec7_new).replace(sec8_old, sec8_new)
io.open(P, "w", encoding="utf-8", newline="").write(t)
print("BACKFILL-OK bytes=%d" % len(t.encode("utf-8")))
