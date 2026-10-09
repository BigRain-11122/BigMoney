# r906 bm-a: W194 prereg sec7/sec8 finalize backfill (machine-derived, byte-level
# CRLF-preserving replace; r895 pattern verbatim-roll, r587 zero-transcription).
import json

P = 'research/PERPETUAL_N1_W194_PREREG.md'
d = json.loads(open('results/perpetual_faces/n1_w194_results.json', encoding='utf-8').read())
nc = d['null_pool_cumulative']
led = d['science_gates']['ledger']
sl = d['skill_line_v2_k_lift']
A = d['families']['A_random_engine_exit']
aud = d['audit']

assert led['prev_total'] == 838945 and led['batch_trials'] == 2200 and led['total'] == 841145
assert aud['finalize_only'] is True and aud['machine'] == 'bm-a'
assert nc['merged']['n_values'] == 424720
assert sl['line_merged_424720'] == 1.1873 and abs(sl['line_delta_k_lift'] - 0.0) < 5e-5
assert len(d['shards_consumed']) == 12
assert d['evidence_cutoff'] == '2026-09-22'
wmu, mmu = nc['w194_only']['mu'], nc['merged']['mu']
gap = abs(wmu - mmu)
sig_old = 0.245100  # W193 merged-sigma frozen key (prereg sec5)
sig_new = nc['merged']['sigma']
sig_rel = (sig_new - sig_old) / sig_old * 100
p95_d = A['full_sharpe_p95'] - 0.2957
assert gap < 0.02 and abs(sig_rel) < 10 and abs(p95_d) < 0.05 and abs(sl['line_delta_k_lift']) <= 0.02
mu_delta = nc['mu_delta_w194_vs_w193ext']
se_mu = nc['se_mu_at_k424720']
p99 = A['full_sharpe_p99']
wsig = nc['w194_only']['sigma']

sec7 = f"""## §7 跑后实证。【finalize 收口机械回填·r906 回填窗（引擎自燃 12/12 08:00:05..08:02:18 → r906 session finalize one-pass 08:2x 落件·§7/§8 同窗回填）】
- 账本恒等式：838,945 + 2,200 = **841,145** EXACT（prev_total/batch_trials/total 三键机读·**vs §5 冻结窗投影恒等零偏离**——本窗=干净链头消费·W191 +6,008 分叉面（bm-b fund_trio 追加式重锚族）后回归 EXACT 面）。
- 合并池：**K=424,720** EXACT（=W193 池 422,520 + 本波 2,200·§5 投影 424,720 命中）。
- merged mu **{round(mmu, 6)}**（机读 {mmu}）/ w-only mu **{round(wmu, 6)}**（机读 {wmu}）/ mu_delta(w194 vs w193ext) **+{mu_delta}**。
- merged sigma **{round(sig_new, 6)}**（W193 键 0.245100→{round(sig_new, 6)} 微降·相对变化 {round(sig_rel, 4)}%）；w-only sigma {round(wsig, 6)}；se_mu@K424,720 **{se_mu}**（W193 0.000377→W194 {se_mu} 收窄·链面 …W191 0.000379→W192 0.000378→W193 0.000377→W194 {se_mu}）。
- skill_line_v2：line_pre **1.1873** → line_merged@K424,720 **{sl['line_merged_424720']}**（K-lift **+0.0000**·n_eff_held_equal 838,945）；canon flip **NOT performed**（K2,200 同例法·治理提案面）。
- A 档 full_sharpe_p95 **{A['full_sharpe_p95']}**（W193 键 0.2957·Δ+{round(p95_d, 4)} 门内）·p99 {p99}。
- §5 四预键机证全过：①mu gap {round(gap, 6)}<0.02 PASS（w-only 高于合并池·门内如实披露）②sigma 相对变化 {round(sig_rel, 4)}%<±10% PASS ③A p95 Δ+{round(p95_d, 4)}<0.05 PASS ④K-lift +0.0000≤±0.02 PASS。
- audit.finalize_only=**true**（bm-a）·voids_applied=LOWAMP-P1,LOWAMP-P2·evidence_cutoff=2026-09-22 在位·shards_consumed 12/12（r905 五面冻结 07:53:42 → 引擎 tick 自燃 n1w194-1of12..12of12 08:00:05..08:02:18 → r906 六门 pre-finalize 探针 13/13 PASS GREEN_FINALIZE_READY〔G1 计数/G2 半开铺瓦/G3 种子连续 A 441_604..443_603 B 443_604..443_803/G4 output-absent/G5 零活进程/G6 head 838,945·r708 活进程腿含〕→ session finalize one-pass 落账〔本窗 status 面机证 finalize output 缺位=materializer 自动 finalize 未复现·坑律入 pit-engine-finalize.md r906 行〕→ n1 selftest PASS 缺省波 r522 律）。
"""

sec8 = """## §8 批后复盘。【finalize 同窗回填·r906 回填窗】
- §5.5 W195+ 投影承接（probe 机证·r587 never-transcribe 律）：naive A first-clean **443_604..445_603**（hops=0 CLEAN）——将被注册 W194 B 带 443_604..443_803 own-start 拒=**W194-B-refuses-W195-A**·阶梯 A-hops-prior-B 继承**第五十五例**（§5.5 预披露兑现·W195 A 重 derive 强制）；naive B first-clean **443_804..444_003**（hops=0 CLEAN）——naive B 落 naive A 窗内·**W141 同窗互斥 leg2 律适用 W195**（W195 冻结方必须在 post-W194 注册宇宙重 derive 且 derive B 时预留本波 A 窗·E36 卡）。
- 宝藏/方法论捕获问：本批 finalize=session one-pass（r903/r904/r895 血统既有律复用·非新方法）；materializer 自动 finalize 未复现观测=坑律面入 research/pit-engine-finalize.md（r906 行）非方法论卡·TREASURE/METHODOLOGY 零 append。
- 诚实披露面：账本 vs §5 投影**零偏离 EXACT**（干净链头消费窗·W191 +6,008 分叉族后回归）；K-lift **+0.0000**（W193 −0.0001 后持平）；mu_delta **+0.00476**=w-only 面回升（门内单波波动·四预键①PASS）；A p95 0.3135 较 W193 键 0.2957 微升 +0.0178 门内；合并池 K=424,720 EXACT；执行链=r905 五面冻结（07:53:42）+引擎自燃 12/12（08:00..08:02）+r906 六门探针+session finalize one-pass+n1 selftest PASS+§7/§8 本窗同窗回填+commit 收口——r905 死会话尾（S6 面未 commit+state/心跳/轮报告三失写）由 r906 遗产吸收窗承接（r899/r902/r904 先例）。
"""

raw = open(P, 'rb').read()
ph7 = "## §7 跑后实证。【finalize 收口机械回填·待 W194 finalize 窗】\r\n- （占位·finalize one-pass 后机械回填：账本恒等式+合并池 K+merged mu/w-only mu/mu_delta+sigma+se_mu+skill_line_v2 K-lift+A 档 p95+§5 四预键机证+canon flip 态+audit.finalize_only+voids_applied。）\r\n".encode('utf-8')
ph8 = "## §8 批后复盘。【finalize 同窗回填·待 W194 finalize 窗】\r\n- （占位·§5.5 W195+ 投影承接+宝藏/方法论捕获问+诚实披露面·finalize 收口窗机械回填。）\r\n".encode('utf-8')
assert ph7 in raw, 'sec7 placeholder (CRLF) not found'
assert ph8 in raw, 'sec8 placeholder (CRLF) not found'
out = raw.replace(ph7, sec7.replace('\n', '\r\n').encode('utf-8')) \
         .replace(ph8, sec8.replace('\n', '\r\n').encode('utf-8'))
with open(P, 'wb') as f:
    f.write(out)
print('backfill OK: sec7+sec8 landed (CRLF preserved, %d -> %d bytes)' % (len(raw), len(out)))
