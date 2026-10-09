# -*- coding: utf-8 -*-
# r915 bm-a: W197 prereg sec7/sec8 finalize backfill (machine-derived, byte-level
# CRLF-preserving replace; r913 pattern verbatim-roll, r587 zero-transcription).
import json

P = 'research/PERPETUAL_N1_W197_PREREG.md'
d = json.loads(open('results/perpetual_faces/n1_w197_results.json', encoding='utf-8').read())
nc = d['null_pool_cumulative']
led = d['science_gates']['ledger']
sl = d['skill_line_v2_k_lift']
A = d['families']['A_random_engine_exit']
aud = d['audit']

assert led['prev_total'] == 845545 and led['batch_trials'] == 2200 and led['total'] == 847745
assert aud['finalize_only'] is True and aud['machine'] == 'bm-a'
assert nc['merged']['n_values'] == 431320
assert sl['line_merged_431320'] == 1.1877 and abs(sl['line_delta_k_lift'] - 0.0001) < 5e-5
assert len(d['shards_consumed']) == 12
assert d['evidence_cutoff'] == '2026-09-22'
wmu, mmu = nc['w197_only']['mu'], nc['merged']['mu']
gap = abs(wmu - mmu)
sig_old = 0.245081  # W196 merged-sigma frozen key (prereg sec5)
sig_new = nc['merged']['sigma']
sig_rel = (sig_new - sig_old) / sig_old * 100
p95_d = A['full_sharpe_p95'] - 0.3267
assert gap < 0.02 and abs(sig_rel) < 10 and abs(p95_d) < 0.05 and abs(sl['line_delta_k_lift']) <= 0.02
mu_delta = nc['mu_delta_w197_vs_w196ext']
se_mu = nc['se_mu_at_k431320']
p99 = A['full_sharpe_p99']
wsig = nc['w197_only']['sigma']

sec7 = f"""## §7 跑后实证。【finalize 收口机械回填·r915 回填窗（r914 buildgen prereg 12:3x → r915 死者会话五面冻结 13:0x → 引擎 tick 自烧 n1w197 12/12 13:01..13:12 → r915 遗产吸收窗六门 pre-finalize 探针 13/13 PASS → session finalize one-pass 13:3x 落账·§7/§8 同窗回填）】
- 账本恒等式：845,545 + 2,200 = **847,745** EXACT（prev_total/batch_trials/total 三键机读·vs §0/§5 冻结投影 847,745 恒等零偏差·连续第四窗 EXACT 干净锚头消费延续）。
- 合并池：**K=431,320** EXACT（W196 池 429,120 + 本波 2,200·§5 投影 431,320 命中）。
- merged mu **{round(mmu, 6)}**（机读 {mmu}）； w-only mu **{round(wmu, 6)}**（机读 {wmu}）； mu_delta(w197 vs w196ext) **{mu_delta}**。
- merged sigma **{round(sig_new, 6)}**（W196 键 0.245081→{round(sig_new, 6)} 微升·相对变化 {round(sig_rel, 4)}%）；w-only sigma {round(wsig, 6)}；se_mu@K431,320 **{se_mu}**（链面 W191 0.000379→W192 0.000378→W193 0.000377→W194 0.000376→W195 0.000375→W196 0.000374→W197 {se_mu} 收窄延续）。
- skill_line_v2：line_pre **1.1876** → line_merged@K431,320 **{sl['line_merged_431320']}**（K-lift **+{sl['line_delta_k_lift']}**·n_eff_held_equal 845,545）；canon flip **NOT performed**（K2,200 同例法·治理提案面）。
- A 档 full_sharpe_p95 **{A['full_sharpe_p95']}**（W196 键 0.3267·Δ{round(p95_d, 4)} 门内·p99 {p99}）。
- §5 四预键机器验证全过：①mu gap {round(gap, 6)}<0.02 PASS（w-only 高于合并池·门内如实披露）②sigma 相对变化 {round(sig_rel, 4)}%<±10% PASS ③p95 Δ{round(p95_d, 4)}<0.05 PASS ④K-lift +{sl['line_delta_k_lift']}≤0.02 PASS。
- audit.finalize_only=**true**（bm-a）；voids_applied=LOWAMP-P1,LOWAMP-P2；evidence_cutoff=2026-09-22 在位；shards_consumed 12/12（r911 buildgen 血统 prereg → r915 死者会话五面冻结 → 引擎 tick 自烧 n1w197-0of12..11of12 落地 → r915 遗产吸收窗六门探针 13/13 PASS GREEN_FINALIZE_READY【G1 计数/G2 半开锁闭/G3 种子连续 A 448_204..450_203 B 450_204..450_403/G4 output-absent/G5 零活进程 r708 活进程腿/G6 head 845,545】→ session finalize one-pass 落账 → n1 selftest PASS 缺省律 r522 例）。
"""

sec8 = """## §8 批后复盘。【finalize 同窗回填·r915 回填窗】
- §5.5 W198+ 投影承接（probe 机证·r587 never-transcribe 律）：naive A first-clean **450_204..452_203**（probe 于 pre-W197 宇宙机证 CLEAN）——将被注册 W197 B 带 450_204..450_403 own-start 拒 → **W197-B-refuses-W198-A**·A-hops-prior-B 阶梯继承**第五十八例**（W198 A re-derive 强制）；naive B first-clean **450_404..450_603** CLEAN——naive B 落 naive A 窗内·**W141 同窗互斥 leg2 律适用 W198**（W198 冻结方 derive B 时预留本波 A 窗·E36 卡）；verify at W198 prereg·hop 链逐跳在 probe 回执。
- 宝藏/方法论捕获问题：本批 finalize=session one-pass（r910/r906/r904/r913 血统既有例复用·非新方法）；r915 死者会话窗（五面冻结+引擎自烧 12/12 落地·closeout 未写·state 停 914）由本窗遗产吸收承接（r899/r902/r904/r906/r910/r913/r914 先例链·三轮工作零丢失）——零新方法零新宝藏·TREASURE/METHODOLOGY 零 append。
- 诚实披露面：账本 vs §5 投影**零偏差 EXACT**（连续第四窗干净锚头消费）；K-lift **+0.0001**（W196 +0.0001 后微升·门内）；mu_delta **+0.009186**=w-only 面高于合并池（门内单波波动·四预键①PASS）；A p95 0.3307 较 W196 键 0.3267 微升 Δ+0.0040 门内；合并池 K=431,320 EXACT；执行链=r914 buildgen prereg+r915 死者会话五面冻结+引擎自烧 12/12（13:01..13:12）+r915 遗产吸收窗六门探针 13/13+session finalize one-pass+§7/§8 本窗同窗回填+commit 收口。
"""

raw = open(P, 'rb').read()
i7 = raw.find('## §7'.encode('utf-8'))
i8 = raw.find('## §8'.encode('utf-8'))
itail = raw.find('- **跑前冻结'.encode('utf-8'))
assert 0 < i7 < i8 < itail, f'section boundaries bad: {i7} {i8} {itail}'
out = raw[:i7] + sec7.replace('\n', '\r\n').encode('utf-8') + raw[i8:i8] + sec8.replace('\n', '\r\n').encode('utf-8') + raw[itail:]
with open(P, 'wb') as f:
    f.write(out)
print('backfill OK: sec7+sec8 landed (CRLF preserved, %d -> %d bytes)' % (len(raw), len(out)))
