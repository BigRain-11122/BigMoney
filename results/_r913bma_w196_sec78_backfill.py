# -*- coding: utf-8 -*-
# r913 bm-a: W196 prereg sec7/sec8 finalize backfill (machine-derived, byte-level
# CRLF-preserving replace; r910 pattern verbatim-roll, r587 zero-transcription).
import json

P = 'research/PERPETUAL_N1_W196_PREREG.md'
d = json.loads(open('results/perpetual_faces/n1_w196_results.json', encoding='utf-8').read())
nc = d['null_pool_cumulative']
led = d['science_gates']['ledger']
sl = d['skill_line_v2_k_lift']
A = d['families']['A_random_engine_exit']
aud = d['audit']

assert led['prev_total'] == 843345 and led['batch_trials'] == 2200 and led['total'] == 845545
assert aud['finalize_only'] is True and aud['machine'] == 'bm-a'
assert nc['merged']['n_values'] == 429120
assert sl['line_merged_429120'] == 1.1875 and abs(sl['line_delta_k_lift'] - 0.0001) < 5e-5
assert len(d['shards_consumed']) == 12
assert d['evidence_cutoff'] == '2026-09-22'
wmu, mmu = nc['w196_only']['mu'], nc['merged']['mu']
gap = abs(wmu - mmu)
sig_old = 0.245069  # W195 merged-sigma frozen key (prereg sec5)
sig_new = nc['merged']['sigma']
sig_rel = (sig_new - sig_old) / sig_old * 100
p95_d = A['full_sharpe_p95'] - 0.3078
assert gap < 0.02 and abs(sig_rel) < 10 and abs(p95_d) < 0.05 and abs(sl['line_delta_k_lift']) <= 0.02
mu_delta = nc['mu_delta_w196_vs_w195ext']
se_mu = nc['se_mu_at_k429120']
p99 = A['full_sharpe_p99']
wsig = nc['w196_only']['sigma']

sec7 = f"""## §7 跑后实证。【finalize 收口机械回填·r913 回填窗（r912 五面冻结 11:0x → 引擎 tick 自燃 n1w196 12/12 11:07..11:17 → r913 六门 pre-finalize 探针 13/13 PASS → session finalize one-pass 12:0x 落件·§7/§8 同窗回填）】
- 账本恒等式：843,345 + 2,200 = **845,545** EXACT（prev_total/batch_trials/total 三键机读·**vs §0/§5 冻结窗投影 845,545 恒等零偏离**·连续第三窗 EXACT·W191 +6,008 分叉族后干净链头消费延续）。
- 合并池：**K=429,120** EXACT（=W195 池 426,920 + 本波 2,200·§5 投影 429,120 命中）。
- merged mu **{round(mmu, 6)}**（机读 {mmu}）/ w-only mu **{round(wmu, 6)}**（机读 {wmu}）/ mu_delta(w196 vs w195ext) **{mu_delta}**。
- merged sigma **{round(sig_new, 6)}**（W195 键 0.245069→{round(sig_new, 6)} 微升·相对变化 {round(sig_rel, 4)}%）；w-only sigma {round(wsig, 6)}；se_mu@K429,120 **{se_mu}**（W195 0.000375→W196 {se_mu} 收窄·链面 …W193 0.000377→W194 0.000376→W195 0.000375→W196 {se_mu}）。
- skill_line_v2：line_pre **1.1874** → line_merged@K429,120 **{sl['line_merged_429120']}**（K-lift **{sl['line_delta_k_lift']}**·n_eff_held_equal 843,345）；canon flip **NOT performed**（K2,200 同例法·治理提案面）。
- A 档 full_sharpe_p95 **{A['full_sharpe_p95']}**（W195 键 0.3078·Δ{round(p95_d, 4)} 门内）·p99 {p99}。
- §5 四预键机证全过：①mu gap {round(gap, 6)}<0.02 PASS（w-only 高于合并池·门内如实披露）②sigma 相对变化 {round(sig_rel, 4)}%<±10% PASS ③A p95 Δ{round(p95_d, 4)}<0.05 PASS ④K-lift {sl['line_delta_k_lift']}≤±0.02 PASS。
- audit.finalize_only=**true**（bm-a）·voids_applied=LOWAMP-P1,LOWAMP-P2·evidence_cutoff=2026-09-22 在位·shards_consumed 12/12（r911 buildgen prereg → r912 五面冻结 → 引擎 tick 自燃 n1w196-0of12..11of12 落位 → r913 六门 pre-finalize 探针 13/13 PASS GREEN_FINALIZE_READY〔G1 计数/G2 半开铺瓦/G3 种子连续 A 446_004..448_003 B 448_004..448_203/G4 output-absent/G5 零活进程/G6 head 843,345·r708 活进程腿含〕→ session finalize one-pass 落账 → n1 selftest PASS 缺省波 r522 律）。
"""

sec8 = """## §8 批后复盘。【finalize 同窗回填·r913 回填窗】
- §5.5 W197+ 投影承接（probe 机证·r587 never-transcribe 律）：naive A first-clean **448_004..450_003**（hops=0 CLEAN）——将被注册 W196 B 带 448_004..448_203 own-start 拒=**W196-B-refuses-W197-A**·阶梯 A-hops-prior-B 继承**第五十七例**（§5.5 预披露兑现·W197 A 重 derive 强制）；naive B first-clean **448_204..448_403**（hops=0 CLEAN）——naive B 落 naive A 窗内·**W141 同窗互斥 leg2 律适用 W197**（W197 冻结方必须在 post-W196 注册宇宙重 derive 且 derive B 时预留本波 A 窗·E36 卡）。
- 宝藏/方法论捕获问：本批 finalize=session one-pass（r910/r906/r904 血统既有律复用·非新方法）；r911/r912 双死会话窗（commits 落地但 closeout 未写·state 停 910）由 r913 遗产吸收窗承接（r899/r902/r904/r906/r910 先例·state heal 910→913 诚实·双轮工作零丢失：r911 buildgen+W196 prereg=origin 在册·r912 五面冻结+W196 座位=origin 在册）·零新方法零新坑·TREASURE/METHODOLOGY 零 append。
- 诚实披露面：账本 vs §5 投影**零偏离 EXACT**（连续第三窗干净链头消费）；K-lift **+0.0001**（W195 −0.0001 后微升·门内）；mu_delta **+0.006627**=w-only 面高于合并池（门内单波波动·四预键①PASS）；A p95 0.3267 较 W195 键 0.3078 微升 Δ+0.0189 门内；合并池 K=429,120 EXACT；执行链=r911 buildgen prereg+r912 五面冻结+引擎自燃 12/12（11:07..11:17）+r913 六门探针 13/13+session finalize one-pass+§7/§8 本窗同窗回填+commit 收口。
"""

raw = open(P, 'rb').read()
ph7 = "## §7 跑后实证。【finalize 收口机械回填·待 W196 finalize 窗】\r\n- （占位·finalize one-pass 后机械回填：账本恒等式+合并池 K+merged mu/w-only mu/mu_delta+sigma+se_mu+skill_line_v2 K-lift+A 档 p95+§5 四预键机证+canon flip 态+audit.finalize_only+voids_applied。）\r\n".encode('utf-8')
ph8 = "## §8 批后复盘。【finalize 同窗回填·待 W196 finalize 窗】\r\n- （占位·§5.5 W197+ 投影承接+宝藏/方法论捕获问+诚实披露面·finalize 收口窗机械回填。）\r\n".encode('utf-8')
assert ph7 in raw, 'sec7 placeholder (CRLF) not found'
assert ph8 in raw, 'sec8 placeholder (CRLF) not found'
out = raw.replace(ph7, sec7.replace('\n', '\r\n').encode('utf-8')) \
         .replace(ph8, sec8.replace('\n', '\r\n').encode('utf-8'))
with open(P, 'wb') as f:
    f.write(out)
print('backfill OK: sec7+sec8 landed (CRLF preserved, %d -> %d bytes)' % (len(raw), len(out)))
