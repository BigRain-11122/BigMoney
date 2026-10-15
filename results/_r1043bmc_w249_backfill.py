# -*- coding: utf-8 -*-
"""r1043 bm-c: W249 prereg sec.7/8 finalize backfill (r1036 W248 pattern).
Backfill-limited-to-sec.7/8 law; placeholder needle replace, byte-preserving elsewhere."""
import io

P = 'research/PERPETUAL_N1_W249_PREREG.md'
t = io.open(P, encoding='utf-8', newline='').read()

n7 = '- （占位·finalize one-pass 后回填：账本恒等式/合并池 K/merged mu·sigma·se_mu/K-lift 对照/§5 五预键机证件/六门探针/canon flip 态/audit 段——bm-c r1036 W248 §7 范式）'
r7 = '\n'.join([
    '- 账本恒等式：prev **969,935** + 2,200 = **972,135 EXACT**（voids LOWAMP-P1/P2 同法应用·append_one_pass）。',
    '- 合并池：**K=545,720 EXACT**（543,520+2,200）；merged mu **-0.09277**（-0.09277202）/ sigma **0.24503**（0.24502840）/ **se_mu@K=545,720=0.000332**（W248 键 0.000332 → 持平·≤ 键 PASS）；W249-only mu **-0.08793** / sigma **0.24233**。',
    '- §5 五预键机证件（results/_r1043bmc_w249_fivekeys.json·ALL PASS）：①W249-only vs merged mu gap **0.00485**<0.02 ✓（merged vs W248 键差 0.00002 ✓）②sigma rel **-0.0045%**<±10% ✓ ③A 档 p95 **0.3158** vs 键 0.3154 差 **+0.0004**<0.05 ✓ ④K-lift 线移 **0.0000**（line_pre 1.1938→line_merged 1.1938 @n_eff held 969,935）≤±0.02 ✓ ⑤se_mu **0.000332**≤0.000332 持平 ✓。',
    '- 六门探针：results/_r1043bmc_w249_sixgate.json **ALL PASS**（PRE-FINALIZE 相位先过——W217-debt standing law 执行·splice sha16 双恒等 pf 487b9fb3d98aa09e/n1 ee694186ffc6ee97 + wave-row faces==freeze bands + banned rc0 + pf selftest + n1 selftest + shards 12/12 + seed_admit FREE verbatim base=563501 span=2000 / base=544901 span=200 + W248 boundary 561501/544701 kept）。',
    '- canon flip 态：**NOT PERFORMED BY THIS WAVE -- GOVERNANCE PROPOSAL FACE ONLY (K2200 SAME LAW)**（governance proposal face only·K2200 同法）。',
    '- 引擎烧录：engine self-burn **12/12**（shard 0-11·常驻引擎 materializer mtime-watch 自见 auto-ignite·r1042 splice 落盘后自烧·claim exempt law sec.2·ledger appends 2d0b41383+f528ab7ab+dfbb4afa2 batched·本窗 r1043 收口）。',
    '- audit 段：machine=bm-c·finalize_only=true·shards_consumed 12/12 文件名全录。',
    '- 诚实披露：K-lift **0.0000**=连续零移段（W136..W248 先例链带内·零机制含义·nulls-deepening 测量面）；A p95 0.3158 较 W248 键 0.3154 差 +0.0004（2,000 试 A 切片抽样波动·测量面非注册收益）；W249-only vs merged gap 0.00485（单波切片 mu 上偏·带内 0.02·W248 先例 0.00145 同向）；se_mu 0.000332 与 W248 键持平（K 增 2,200 后 6 位小数面持平·≤ 断言 PASS·测量面如实注记）。',
])

n8 = '- （占位·finalize 同窗回填：§5.5 W249+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——bm-c r1036 W248 §8 范式）'
r8 = '\n'.join([
    '- §5.5 W250+ 投影承接机证：本波 finalize 落地=**W250 席开放**——下一位 freezer 必须 seat-first publish（O-20261010-2350 §2）+post-W249 universe live re-derive（禁转录 r587 律）+derive B 时预留本波 A 窗（W249 face：A naive 565_501..567_500 预投影 CLEAN（hops=0）/ B naive 545_101..545_300 CLEAN（hops=0·B base==545_100+1 EXACT·B_hop_lands_inside_A=false 腿在场））；W249 A 563_501..565_500 高悬于 B 544_901..545_100 之上·seed-gap face 连续第十三波·禁假设 staircase A-base==prior-B-tail+1 恒等）。',
    '- 宝藏与方法论捕获问：**零新方法**（finalize one-pass=r1036/W248 管线 verbatim 复用·sixgate/fivekeys/backfill 脚本克隆血统注明）→ METHODOLOGY_ASSETS 零 append；宝藏登记零新条（既有链法覆盖）。',
    '- 诚实披露面：本窗收养死窗序列（r1036 closeout 22:39 后死窗 r1037（席位发布+S6 23:03）/r1038（S6 00:38+seareview 面）/r1039（d19 facts）/r1040（prereg author 04:04）/r1041（prereg freeze LANDED+D-20261016-01/02 legs）/r1042（splice LANDED）全死 pre-closeout——state 停在 round_no=1037·本窗 r1043=canonical 续接·bm-c 吸收先例链第 37 代）；六门 PRE-FINALIZE 本窗首过即正确相位（sixgate 先于 finalize 执行·W217-debt standing law 连续执行）；引擎烧录=常驻引擎 mtime-watch 自见 auto-ignite（r535 律·引擎车道自主点火·非引擎约束）；W249 席位=bm-c own-seat（第 69 枚 own·MSG-20261015-225x-bmc-w249-seat origin 8949e0aef·prereg 4103f0d5d·splice 5d4aeec59）。',
])

assert t.count(n7) == 1, 'sec.7 needle not unique: %d' % t.count(n7)
assert t.count(n8) == 1, 'sec.8 needle not unique: %d' % t.count(n8)
t2 = t.replace(n7, r7).replace(n8, r8)
io.open(P, 'w', encoding='utf-8', newline='').write(t2)
print('backfill OK: sec.7 %d chars -> %d, sec.8 %d chars -> %d, file %d -> %d bytes' % (
    len(n7), len(r7), len(n8), len(r8), len(t.encode("utf-8")), len(t2.encode("utf-8"))))
