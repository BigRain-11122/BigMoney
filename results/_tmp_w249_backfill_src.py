# -*- coding: utf-8 -*-
"""r1036 bm-c: W248 prereg sec.7/8 finalize backfill (bm-a r1022 W247 pattern).
Backfill-limited-to-sec.7/8 law; placeholder needle replace, byte-preserving elsewhere."""
import io

P = 'research/PERPETUAL_N1_W248_PREREG.md'
t = io.open(P, encoding='utf-8', newline='').read()

n7 = '- （占位·finalize one-pass 后回填：账本恒等式/合并池 K/merged mu·sigma·se_mu/K-lift 对照/§5 五预键机证件/六门探针/canon flip 态/audit 段——bm-a r1022 W247 §7 范式）'
r7 = '\n'.join([
    '- 账本恒等式：prev **967,735** + 2,200 = **969,935 EXACT**（voids LOWAMP-P1/P2 同法应用·append_one_pass）。',
    '- 合并池：**K=543,520 EXACT**（541,320+2,200）；merged mu **-0.09279**（-0.09279163）/ sigma **0.24504**（0.24503930）/ **se_mu@K=543,520=0.000332**（W247 键 0.000333 → 收窄链续）；W248-only mu **-0.09134** / sigma **0.24223**。',
    '- §5 五预键机证件（results/_r1036bmc_w248_fivekeys.json·ALL PASS）：①W248-only vs merged mu gap **0.00145**<0.02 ✓（merged vs W247 键差 0.0000059 ✓）②sigma rel **-0.0047%**<±10% ✓ ③A 档 p95 **0.3154** vs 键 0.3292 差 **-0.0138**<0.05 ✓ ④K-lift 线移 **-0.0001**（line_pre 1.1938→line_merged 1.1937 @n_eff held 967,735）≤±0.02 ✓ ⑤se_mu **0.000332**≤0.000333 收窄 ✓。',
    '- 六门探针：results/_r1036bmc_w248_sixgate.json **ALL PASS**（splice sha16 双恒等 pf fd8b95810b45c48c/n1 72e95889017708ba + wave-row faces==freeze bands + banned rc0 + pf selftest 9/9 + n1 selftest + shards 12/12 + seed_admit FREE verbatim base=561501 span=2000 / base=544701 span=200 + W247 boundary 559501/544501 kept）。',
    '- canon flip 态：**NOT PERFORMED BY THIS WAVE -- GOVERNANCE PROPOSAL FACE ONLY (K2200 SAME LAW)**（governance proposal face only·K2200 同法）。',
    '- 引擎烧录：engine self-burn **12/12**（shard 0-11·21:36-21:44·常驻引擎 materializer mtime-watch 自见 auto-ignite·claim exempt law sec.2·冻结编辑 r1036 死窗（21:36-21:39 splice 落盘）后引擎自见点火·本窗 r1036 收口）。',
    '- audit 段：machine=bm-c·finalize_only=true·shards_consumed 12/12 文件名全录。',
    '- 诚实披露：K-lift **-0.0001**=连续零移段（W136..W247 先例链带内·零机制含义·nulls-deepening 测量面）；A p95 0.3154 较 W247 键 0.3292 差 -0.0138（2,000 试 A 切片抽样波动·测量面非注册收益）；W248-only vs merged gap 0.00145（单波切片 mu 上偏·带内 0.02·W247 先例 0.0048 同向更大）。',
])

n8 = '- （占位·finalize 同窗回填：§5.5 W248+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——bm-a r1022 W247 §8 范式）'
r8 = '\n'.join([
    '- §5.5 W249+ 投影承接机证：本波 finalize 落地=**W249 席开放**——下一位 freezer 必须 seat-first publish（O-20261010-2350 §2）+post-W248 universe live re-derive（禁转录 r587 律）+derive B 时预留本波 A 窗（W248 face：A naive 563_501..565_500 预投影 CLEAN（hops=0）/ B naive 544_901..545_100 CLEAN（hops=0·B base==544_900+1 EXACT·B_hop_lands_inside_A=false 腿在场））；W248 A 561_501..563_500 高悬于 B 544_701..544_900 之上·seed-gap face 连续第十波·禁假设 staircase A-base==prior-B-tail+1 恒等）。',
    '- 宝藏与方法论捕获问：**零新方法**（finalize one-pass=r1022/W247 管线 verbatim 复用·sixgate/fivekeys/backfill 脚本克隆血统注明）→ METHODOLOGY_ASSETS 零 append；宝藏登记零新条（既有链法覆盖）。',
    '- 诚实披露面：本窗收养死窗序列（r1035 closeout 21:13 后死窗 21:36-21:39 执行五面冻结 splice 落盘+引擎自烧 12/12 后死·零 own commit——state 停在 r1035/round_no=1036·本窗 r1036=canonical 续接·bm-c 吸收先例链第 36 代）；引擎烧录 21:36-21:44=常驻引擎 mtime-watch 自见 auto-ignite（r535 律·引擎车道自主点火·非引擎约束）；W248 席位=bm-c own-seat（第 68 波 own·MSG-20261015-164x-bmc-w248-seat·prereg r1035 窗 SUB derive landed b9abac7067）。',
])

assert t.count(n7) == 1, 'sec.7 needle not unique: %d' % t.count(n7)
assert t.count(n8) == 1, 'sec.8 needle not unique: %d' % t.count(n8)
t2 = t.replace(n7, r7).replace(n8, r8)
io.open(P, 'w', encoding='utf-8', newline='').write(t2)
print('backfill OK: sec.7 %d chars -> %d, sec.8 %d chars -> %d, file %d -> %d bytes' % (
    len(n7), len(r7), len(n8), len(r8), len(t.encode("utf-8")), len(t2.encode("utf-8"))))
