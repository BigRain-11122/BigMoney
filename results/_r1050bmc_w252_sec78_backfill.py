# -*- coding: utf-8 -*-
# r1050 bm-c: W252 prereg sec.7/sec.8 mechanical backfill (finalize closeout leg).
# W251 r1048 范式. Exact placeholder needles, count-asserted, zero-prose-drift law.
import io

P = "research/PERPETUAL_N1_W252_PREREG.md"
t = io.open(P, encoding="utf-8").read()

sec7_placeholder = "- （占位·finalize one-pass 后回填：账本恒等式/合并池 K/merged mu·sigma·se_mu/K-lift 对照/§5 五预键机证件/六门探针/canon flip 态/audit 段——bm-c r1048 W251 §7 范式）"
sec8_placeholder = "- （占位·finalize 同窗回填：§5.5 W253+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——bm-c r1048 W251 §8 范式）"

sec7_body = """- 账本恒等式：prev **976,535** + 2,200 = **978,735 EXACT**（voids LOWAMP-P1/P2 同法应用·append_one_pass）。
- 合并池：**K=552,320 EXACT**（550,120+2,200）；merged mu **-0.092740**（-0.09273968315469293）/ sigma **0.245048**（0.24504788580090198）/ **se_mu@K=552,320=0.000330**（W251 键 0.000330 → 6 位小数面持平·≤ 键 PASS）；W252-only mu **-0.090175** / sigma **0.247990**。
- §5 五预测键机证件（results/_r1050bmc_w252_fivekeys.json·ALL PASS）：①W252-only vs merged mu gap **0.002565**<0.02 ✓（merged vs W251 键差 0.0000103 ✓）②sigma rel **0.00477%**<±10% ✓ ③A 档 p95 **0.319900** vs 键 0.3153 差 **+0.004600**<0.05 ✓ ④K-lift 线移 **0.000100**（line_pre 1.194200→line_merged 1.194300 @n_eff held 976,535）≤±0.02 ✓ ⑤se_mu **0.000330**≤0.000330 ✓。
- 六门探针：results/_r1050bmc_w252_sixgate.json **ALL PASS**（PRE-FINALIZE 相位先过——W217-debt standing law 执行·连续第 14 波正相位；gate-1 三重恒等 worktree==freeze receipt post==LANDED git blob n1 7252c90bad52de99 / pf b3eed1c579e7f22f 零漂移——本波零 post-splice heal（splice commit e63561df3=worktree 字节直落·死窗 5 缺陷类 pre-splice 计数断言闸内修复·E70 re-anchor 无需面）+ wave-row faces==freeze bands + banned rc0 + pf selftest + n1 selftest + shards 12/12 + seed_admit FREE verbatim base=569701 span=2000 / base=571701 span=200 + W251 boundary 567501/569501 kept）。
- canon flip 态：**NOT PERFORMED BY THIS WAVE -- GOVERNANCE PROPOSAL FACE ONLY (K2200 SAME LAW)**（governance proposal face only·K2200 同法）。
- 引擎烧录：engine self-burn **12/12**（shard 0-11·常驻引擎 materializer mtime-watch 自见 auto-ignite·r1050 splice e63561df3 落盘后自烧·ledger appends cbf6411bf+b3d563f4f batched 6+6 self-commit·本窗 r1050 收口）。
- audit 段：machine=bm-c·finalize_only=true·shards_consumed 12/12 文件名全录。
- 诚实披露：K-lift **0.000100**=先例链内第二个连续非零微移段（W251 首个 0.0001→本波 0.0001·W136..W251 全在 ±0.0003 内·机读可复核·本移仍远在 ±0.02 断言带内·nulls-deepening 测量面非注册收益）；A p95 0.319900 较 W251 键 0.3153 差 +0.0046（2,000 试 A 切片抽样波动·测量面非注册收益·W251 波同面 -0.0082 反向·双向波动先例互证）；W252-only vs merged gap 0.002565（单波切片 mu 上偏·带内 0.02·W250 波 0.000511/W251 波 0.004986→本波 0.002565=波动带中位回归面）；se_mu 0.000330 持平（K 增 2,200 后 6 位小数面持平未再收窄·≤ 断言 PASS·测量面如实注记）。"""

sec8_body = """- §5.5 W253+ 投影承接机证：本波 finalize 落地=**W253 席开放**——下一位 freezer 必须 seat-first publish（O-20261010-2350 §2）+post-W252 universe live re-derive（禁转录 r587 律）+derive B 时预留本波 A 窗 569_701..571_700 与 B 带 571_701..571_900（W252 §5.5 face：A naive 571_701..573_700 CLEAN-at-naive **BUT start refused at registered W252 B band 571_701..571_900**=staircase-affects-A **2nd consecutive hop**（W252 A 首跳后承袭）→A first-clean 将再上移；B own-A reservation cascade **~573_901..574_100-class** 落位面；**W253 冻结方禁假设 A-base==prior-B-tail+1 恒等·须重读 live trace**（seed-gap face 承袭 W239..W251·staircase 双跳面如实注记）；W253 derive 必须在 post-W252 注册宇宙重 derive 且预留本波 A 窗 569_701..571_700+本波 B 带 571_701..571_900——leg2 律/E36 卡·W141 先例；verify at W253 prereg，hop 链逐跳在 probe 回执复核）。
- 宝藏与方法论捕获问：**本批零新方法论面**（W252 周期=正典链续接·五面全带内·六闸/五键/终定全正相位一次过——无新机制/无新根因；fivekeys/sixgate derive=E63 canon-clone 链复用零新卡；宝藏登记零新条（既有链法覆盖））。
- 诚实披露面：本窗=absorb 续接（死窗 10:4x-11:3x 执行 splice 11:33-11:34〔commit e63561df3 落地〕+engine self-burn 12/12〔ledger appends cbf6411bf+b3d563f4f self-commit〕——state 停在 round_no=1050·本窗 r1050 续接完成 sixgate〔首跑 ALL PASS·零 heal 零 re-anchor 面〕+finalize one-pass+五键+§7/§8 回填）；六门 PRE-FINALIZE 相位正确（连续第 14 波）；W252 席位=bm-c own-seat（第 72 枚 own·第 242 引擎波·prereg 472cc8386·seat MSG-20261016-10xx-bmc-w252-seat origin f9441de67 先于冻结发布〔r565 律〕）。"""

assert t.count(sec7_placeholder) == 1, "sec7 placeholder count != 1"
assert t.count(sec8_placeholder) == 1, "sec8 placeholder count != 1"
t = t.replace(sec7_placeholder, sec7_body)
t = t.replace(sec8_placeholder, sec8_body)
io.open(P, "w", encoding="utf-8", newline="").write(t)
print("BACKFILL-OK sec7=%dB sec8=%dB file=%dB" % (
    len(sec7_body.encode("utf-8")), len(sec8_body.encode("utf-8")),
    len(t.encode("utf-8"))))
