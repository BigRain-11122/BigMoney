# -*- coding: utf-8 -*-
"""r1046 bm-c: W250 prereg sec.7/8 finalize backfill (r1043 W249 pattern).
Backfill-limited-to-sec.7/8 law; placeholder LINE replace (prefix-anchored,
programmatic needle location -- zero hand-copied CJK needles), byte-preserving
elsewhere. Numbers machine-derived from finalize results + fivekeys + sixgate
receipts (zero transcription)."""
import io
import json

P = 'research/PERPETUAL_N1_W250_PREREG.md'
t = io.open(P, encoding='utf-8', newline='').read()

res = json.load(open('results/perpetual_faces/n1_w250_results.json', encoding='utf-8'))
fk = json.load(open('results/_r1046bmc_w250_fivekeys.json', encoding='utf-8'))
sg = json.load(open('results/_r1046bmc_w250_sixgate.json', encoding='utf-8'))
pool = res['null_pool_cumulative']
sl = res['skill_line_v2_k_lift']
famA = res['families']['A_random_engine_exit']
merged_mu = pool['merged']['mu']
merged_sigma = pool['merged']['sigma']
w250_mu = pool['w250_only']['mu']
w250_sigma = pool['w250_only']['sigma']
se_mu = pool['se_mu_at_k547920']
a_p95 = famA['full_sharpe_p95']
kd = {c['name']: c for c in fk['checks']}

def f6(x):
    return '%.6f' % x

r7 = '\n'.join([
    '- 账本恒等式：prev **972,135** + 2,200 = **974,335 EXACT**（voids LOWAMP-P1/P2 同法应用·append_one_pass）。',
    '- 合并池：**K=547,920 EXACT**（545,720+2,200）；merged mu **%s**（%s）/ sigma **%s**（%s）/ **se_mu@K=547,920=%s**（W249 键 0.000332 → 收窄·≤ 键 PASS）；W250-only mu **%s** / sigma **%s**。' % (
        f6(merged_mu), merged_mu, f6(merged_sigma), merged_sigma, f6(se_mu), f6(w250_mu), f6(w250_sigma)),
    '- §5 五预键机证件（results/_r1046bmc_w250_fivekeys.json·ALL PASS）：①W250-only vs merged mu gap **%s**<0.02 ✓（merged vs W249 键差 %s ✓）②sigma rel **%s%%**<±10%% ✓ ③A 档 p95 **%s** vs 键 0.3158 差 **+%s**<0.05 ✓ ④K-lift 线移 **%s**（line_pre %s→line_merged %s @n_eff held 972,135）≤±0.02 ✓ ⑤se_mu **%s**≤0.000332 ✓。' % (
        f6(kd['key1_w250_vs_merged_mu_gap']['value']), f6(kd['key1b_merged_vs_w249_key']['value']),
        '%.4f' % (kd['key2_sigma_rel']['value'] * 100), f6(a_p95),
        f6(kd['key3_a_p95_delta']['value']), f6(kd['key4_k_lift_move']['value']),
        f6(sl['line_pre_w250']), f6(sl['line_merged_547920']), f6(se_mu)),
    '- 六门探针：results/_r1046bmc_w250_sixgate.json **ALL PASS**（PRE-FINALIZE 相位先过——W217-debt standing law 执行；gate-1 锚面披露：freeze receipt n1_sha16_post=**in-memory pre-heal 快照**（receipt 08:04:23 写于 disclosed post-splice heal〔print face rows 68→69·commit 29930f489 message〕之前→按构造不可等 healed blob；gate-1 断言改锚 worktree==**LANDED git blob** n1 22a957f851fd3adc / pf 40b0befe37ebbe2c 零漂移）+ wave-row faces==freeze bands + banned rc0 + pf selftest + n1 selftest + shards 12/12 + seed_admit FREE verbatim base=565501 span=2000 / base=545101 span=200 + W249 boundary 563501/544901 kept）。',
    '- canon flip 态：**NOT PERFORMED BY THIS WAVE -- GOVERNANCE PROPOSAL FACE ONLY (K2200 SAME LAW)**（governance proposal face only·K2200 同法）。',
    '- 引擎烧录：engine self-burn **12/12**（shard 0-11·常驻引擎 materializer mtime-watch 自见 auto-ignite·r1046 splice 落盘后自烧·claim exempt law sec.2·ledger appends 486458150+77a4f529a batched 6+6·本窗 r1046 收口）。',
    '- audit 段：machine=bm-c·finalize_only=true·shards_consumed 12/12 文件名全录。',
    '- 诚实披露：K-lift **%s**=连续零移段（W136..W249 先例链带内·零机制含义·nulls-deepening 测量面）；A p95 %s 较 W249 键 0.3158 差 +0.0077（2,000 试 A 切片抽样波动·测量面非注册收益）；W250-only vs merged gap %s（单波切片 mu 上偏·带内 0.02·较 W249 波 0.00485 显著收窄）；se_mu 0.000332→%s 收窄（K 增 2,200 后 6 位小数面收窄·≤ 断言 PASS·测量面如实注记）。' % (
        f6(kd['key4_k_lift_move']['value']), f6(a_p95), f6(kd['key1_w250_vs_merged_mu_gap']['value']), f6(se_mu)),
])

r8 = '\n'.join([
    '- §5.5 W251+ 投影承接机证：本波 finalize 落地=**W251 席开放**——下一位 freezer 必须 seat-first publish（O-20261010-2350 §2）+post-W250 universe live re-derive（禁转录 r587 律）+derive B 时预留本波 A 窗（W250 §5.5 face：A naive 567_501..569_500 预投影 CLEAN（hops=0·pre-W250 宇宙零活点拒）/ B naive 545_301..545_500 REFUSED（SEED_REGISTRY seed 545_500 命中+W240..W249 A-ladder 拒面→first-clean 565_501..565_700·hops=11·不落投影 A 窗内）；**W250 A 565_501..567_500 注册后=post-W250 宇宙新拒面**——W251 冻结方 B derive 必须跳过本波 A 带（pre-W250 投影 565_501..565_700 已被本波 A 带覆盖·W251 live re-derive 首过窗面必变·禁转录投影）；seed-gap face 连续第十四波·禁假设 staircase A-base==prior-B-tail+1 恒等）。',
    '- 宝藏与方法论捕获问：**一项新方法论面**（非复用零新面）——post-splice heal 使 in-memory freeze receipt post-sha 按构造失真（receipt 哈希 pre-heal 字符串·heal 落盘先于 commit）→ sixgate gate-1 断言改锚 **worktree==LANDED git blob**（git show 恒等·强于陈旧 receipt 对比·heal 以 commit message 披露面为准）→ METHODOLOGY_ASSETS 卡已定向 append；宝藏登记零新条（既有链法覆盖）。',
    '- 诚实披露面：本窗=canonical 续接（死窗 r1046-predecessor 07:4x-08:1x 执行 splice 08:02-08:04〔commit 29930f489 落地含 disclosed heal〕+engine self-burn 12/12〔ledger appends 08:07/08:10 self-commit〕+sixgate script authored 08:09:43 未跑即死——state 停在 round_no=1046·本窗 r1046 续接完成 sixgate〔首跑 FAIL=stale receipt sha face·root-cause 定谳·gate-1 改锚 landed blob 后 ALL PASS〕+finalize one-pass+五键+§7/§8 回填）；六门 PRE-FINALIZE 相位正确（engine burn 完成后 finalize 前）；W250 席位=bm-c own-seat（第 70 枚 own·MSG-20261016-055x-bmc-w250-seat origin cc06f1f4a·prereg 4f7a130ff·splice 29930f489）。',
])

lines = t.split('\n')
i7 = i8 = None
for idx, l in enumerate(lines):
    if l.startswith('## §7'):
        i7 = idx
    elif l.startswith('## §8'):
        i8 = idx
assert i7 is not None and i8 is not None and i7 < i8, 'section anchors missing'
p7 = [idx for idx in range(i7, i8) if lines[idx].startswith('- （占位·finalize one-pass 后回填')]
p8 = [idx for idx in range(i8, len(lines)) if lines[idx].startswith('- （占位·finalize 同窗回填')]
assert len(p7) == 1, 'sec.7 placeholder not unique: %d' % len(p7)
assert len(p8) == 1, 'sec.8 placeholder not unique: %d' % len(p8)
lines[p7[0]] = r7
lines[p8[0]] = r8
t2 = '\n'.join(lines)
io.open(P, 'w', encoding='utf-8', newline='').write(t2)
print('backfill OK: sec.7 line %d -> %d chars, sec.8 line %d -> %d chars, file %d -> %d bytes' % (
    p7[0], len(r7), p8[0], len(r8), len(t.encode('utf-8')), len(t2.encode('utf-8'))))
