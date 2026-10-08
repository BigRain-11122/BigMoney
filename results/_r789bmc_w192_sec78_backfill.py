# r789 bm-c: W192 prereg sec7/sec8 finalize backfill (machine-derived, UTF-8 no BOM).
# Clone of r895 bm-a W191 backfill one wave later. Numbers read directly from
# results/perpetual_faces/n1_w192_results.json (finalize landed this window,
# session one-pass per r381 recovery-round-first-action law) -- zero hand
# transcription. §5 frozen keys = W190 anchors (draft-window latest landed face).
import json, math

P = 'research/PERPETUAL_N1_W192_PREREG.md'
d = json.loads(open('results/perpetual_faces/n1_w192_results.json', encoding='utf-8').read())
nc = d['null_pool_cumulative']
led = d['science_gates']['ledger']
sl = d['skill_line_v2_k_lift']
A = d['families']['A_random_engine_exit']
aud = d['audit']

assert led['prev_total'] == 834545 and led['batch_trials'] == 2200 and led['total'] == 836745
assert aud['finalize_only'] is True and aud['machine'] == 'bm-c'
assert nc['merged']['n_values'] == 420320
assert sl['line_merged_420320'] and abs(sl['line_delta_k_lift'] - (-0.0002)) < 5e-5
assert len(d['shards_consumed']) == 12
assert d['evidence_cutoff'] == '2026-09-22'
wmu, mmu = nc['w192_only']['mu'], nc['merged']['mu']
gap = abs(wmu - mmu)
sig_old, sig_new = 0.245150, nc['merged']['sigma']
sig_rel = (sig_new - sig_old) / sig_old * 100
p95_d = A['full_sharpe_p95'] - 0.3068
se_mu = nc['merged']['sigma'] / math.sqrt(nc['merged']['n_values'])
assert gap < 0.02 and abs(sig_rel) < 10 and abs(p95_d) < 0.05 and abs(sl['line_delta_k_lift']) <= 0.02

sec7 = """## §7 跑后实证。【finalize 收口机械回填·r789 回填窗（06:2x 会话 one-pass finalize 落件·§7/§8 同窗回填）】
- 账本恒等式：834,545 + 2,200 = **836,745** EXACT（prev_total/batch_trials/total 三键机读；**prev=834,545=活链头时点消费**（r518 律）=W191 n1 落账 833,536 + bm-a r899 F1-BULL-COND-P1 判决批 1,009（FAIL-CLOSED 0/9 照计）两段合成——vs §0 起稿窗锚（W191 在飞未落）偏离如实披露非改判据·r807 活链头正典律）。
- 合并池：**K=420,320** EXACT（=W191 池 418,120 + 本波 2,200·§0 投影 420,320 命中）。
- merged mu **-0.092854**（机读 -0.09285400171298058）/ w-only mu **-0.090474**（机读 -0.09047404545454546）/ w-only 较 W191-only（-0.089832）回落 **-0.000642**（W191 +0.008767 升后单波回落·门内波动如实披露）。
- merged sigma **0.245131**（W190 冻结键 0.245150→0.245131·相对变化 **-0.008%**）；w-only sigma 0.238494；se_mu@K420,320 **0.000378**（链面 …W189 0.000381→W190 0.000380→W191 0.000379→W192 0.000378 续收窄）。
- skill_line_v2：line_pre **1.1874** → line_merged@K420,320 **1.1872**（K-lift **-0.0002**·n_eff_held_equal 834,545）；canon flip **NOT performed**（K2,200 同例法·治理提案面）。
- A 档 full_sharpe_p95 **0.2989**（W190 冻结键 0.3068·Δ-0.0079 门内）·p99 0.4400。
- §5 四预键机证全过：①mu gap 0.002380<0.02 PASS（w-only 高于合并池·与 W191 同向·门内如实披露）②sigma 相对变化 -0.008%<±10% PASS ③A p95 Δ-0.0079<0.05 PASS ④K-lift -0.0002≤±0.02 PASS。
- audit.finalize_only=**true**（bm-c）·voids_applied=LOWAMP-P1,LOWAMP-P2·evidence_cutoff=2026-09-22 在位·shards_consumed 12/12（引擎 tick 自烧 r787 点火 03:45-03:48 12 分片全落·06:2x 会话 one-pass finalize〔pit-95 落地守卫+六门 pre-finalize 探针 GREEN_FINALIZE_READY results/_r789bmc_w192_prefinalize_probe.json〕+n1 selftest 全绿缺省波）。
"""

sec8 = """## §8 批后复盘。【finalize 同窗回填·r789 回填窗】
- §5.5 W193+ 投影承接（bm-a r900 席位已发布=MSG-2026-10-09-0458-bma-w193-seat·机证 **A 439_404..441_403 / B 441_404..441_603** 双 hops=1 与本波 §5.5 投影（A first-clean 439_204..441_203 **被本波注册 B 带 439_204..439_403 own-start 拒**=阶梯 A-hops-prior-B 第五十三例兑现·B first-clean 441_404..441_603 过本波 A 窗保留跳=W141 同窗互斥 leg2 律兑现）恒等——W193 五面冻结待本 finalize 落地后开窗（bm-a MSG 明示 materializer dep chain W17..W192 全在场·本件落账即解锁）·r587 never-transcribe 律）。
- 宝藏/方法论捕获问：本批 finalize=既有 one-pass 机械（r895 W191 范式同款）+发现面一件（bm-a r899 F1-BULL null base 94_200 落已烧 W137 B 带 j=199——r870/r874 同族第二例·pocket 扫描漏 N1_BANDS 面同盲区·spawn-children-only 消费=bookkeeping 级零统计伤害·perpetual_faces_n1.py w137_adjudicated in-section adjudication 治愈+n1 selftest 复绿·轮报告披露）；TREASURE/METHODOLOGY 零 append（既有判例复用非新方法）。
- 诚实披露面：账本 prev 消费=活链头 834,545（W191 833,536+F1-BULL 1,009·r518 律·干净入链零科学损失）；w-only mu 回落 -0.000642（W191 升后单波波动·门内）；w-only sigma 0.238494 低于合并池（单波抽样面）；A p95 0.2989 较 W190 键 0.3068 降 -0.0079（门内·测量面非注册利益）；合并池 K=420,320 EXACT；引擎 tick 自烧 12 分片（r787 点火 03:45-03:48）+r789 会话 one-pass finalize+六门探针+n1 selftest+§7/§8 本窗同窗回填+commit 收口。
"""

src = open(P, encoding='utf-8').read()
ph7 = "## §7 跑后实证。【finalize 收口机械回填·待 W192 finalize 窗】\n- （占位·finalize one-pass 后机械回填：账本恒等式+合并池 K+merged mu/w-only mu/mu_delta+sigma+se_mu+skill_line_v2 K-lift+A 档 p95+§5 四预键机证+canon flip 态+audit.finalize_only+voids_applied。）\n"
ph8 = "## §8 批后复盘。【finalize 同窗回填·待 W192 finalize 窗】\n- （占位·§5.5 W193+ 投影承接+宝藏/方法论捕获问+诚实披露面·finalize 收口窗机械回填。）\n"
assert ph7 in src, 'sec7 placeholder not found'
assert ph8 in src, 'sec8 placeholder not found'
src = src.replace(ph7, sec7).replace(ph8, sec8)
with open(P, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
print('backfill OK: sec7+sec8 landed; gap=%.6f sig_rel=%.4f%% p95_d=%.4f se_mu=%.6f' % (gap, sig_rel, p95_d, se_mu))
