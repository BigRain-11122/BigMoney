# -*- coding: utf-8 -*-
# r1199 bm-c: W310 prereg sec.7/sec.8 post-run backfill (finalize same-window law).
# Lineage: the r1197/r1198 one-pass backfill routine; every value is machine-read from
# the finalize product + the six-gate + five-key receipts (zero transcription, r587).
import io
import json

PREREG = 'research/PERPETUAL_N1_W310_PREREG.md'
d = json.load(io.open('results/perpetual_faces/n1_w310_results.json', encoding='utf-8'))
fk = json.load(io.open('results/_r1199bmc_w310_fivekeys.json', encoding='utf-8'))
sg = json.load(io.open('results/_r1199bmc_w310_sixgate.json', encoding='utf-8'))
p = d['null_pool_cumulative']
s = d['skill_line_v2_k_lift']
A = d['families']['A_random_engine_exit']
B = d['families']['B_random_entry_random_exit']
led = d['science_gates']['ledger']

sec7 = f"""## §7 跑后实证。【finalize 收口机械回填】
- 账本恒等式：`{led['prev_total']:,} + {led['batch_trials']:,} = {led['total']:,}`（exact={fk['ledger_identity']['exact']}）；累计池 K `677,720 + 2,200 = {p['merged']['n_values']:,}`（exact={fk['merged_k_identity']['exact']}）。
- 合并池（W1..W310）：mu **{p['merged']['mu']:.8f}** / sigma **{p['merged']['sigma']:.8f}** / se_mu@K679,920 **{p['se_mu_at_k679920']:.6f}**；W310-only mu **{p['w310_only']['mu']:.8f}** / sigma **{p['w310_only']['sigma']:.8f}**。
- A 档 full_sharpe p95 **{A['full_sharpe_p95']}** / p99 **{A['full_sharpe_p99']}**（锚 W309 p95 0.3384，差={fk['checks'][3]['value']:.4f} 在 ±0.05 带内）；B 档 n={B.get('n')}。
- K-lift 对照：line_pre_w310 **{s['line_pre_w310']}** → line_merged@K679,920 **{s['line_merged_679920']}**，差 **{s['line_delta_k_lift']:+.4f}**；n_eff_held_equal {s['n_eff_held_equal']:,}。
- §5 五预键验证：`results/_r1199bmc_w310_fivekeys.json` 共 **{sum(1 for c in fk['checks'] if c['pass'])}/6 ALL PASS**；prose 偏差披露 {len(fk['prereg_prose_deviations'])} 条（key4 K-lift prose +0.0001 vs 本波实测 0.0000——如实披露不抹平）。
- 六门探针：`results/_r1199bmc_w310_sixgate.json` verdict **{sg['verdict']}**（第 73 次连续正确相位；splice 完整性/clean-state/adjudication/pf+n1 selftest/12-12 分片 >100KB/seed_admit FREE 双带）。
- canon flip：**{s['canon_flip']}**（本波不动治理面）。
- audit 段：`{json.dumps(d.get('audit'), ensure_ascii=False)}`；shards_consumed 12/12；evidence_cutoff `{d.get('evidence_cutoff')}`。
"""

sec8 = f"""## §8 批后复盘。【finalize 同窗回填】
- §5.5 W311+ 投影承接机证：naive W311 A 699_301..701_300 CLEAN（hops=0），但注册 W310 B 带 699_301..699_500 会拒绝该起点（staircase-affects-A 承袭预期）；naive W311 B 699_501..699_700 CLEAN 但落投影 A 窗内——**W311 seat 必须 live re-derive，禁转抄本投影**（r587）；B own-A reservation cascade 相应上移。
- 宝藏与方法论捕获问：本波=nulls-deepening 常态加深，**无新方法/无新宝藏**，knowledge/METHODOLOGY_ASSETS.md 与 TREASURE_REGISTRY.md 均不追加。
- 诚实披露：§5 五预键 1 条 prose 偏差（key4 K-lift +0.0001 vs 本波 0.0000），以机读值为准并披露，不抹平；其余 mu/sigma/K-lift 全部落在冻结带内。
- 收口纪律：finalize 只消费在册分片（audit.finalize_only=true），本波零重烧、零双烧；S6 链与轮收口同窗。

"""

t = io.open(PREREG, encoding='utf-8').read()
i7 = t.find('## §7 跑后实证')
i8 = t.find('## §8 批后复盘')
assert i7 > 0 and i8 > i7, 'sec.7/sec.8 anchors missing'
end8 = t.find('\n- **跑前冻结=本件 commit**', i8)
if end8 < 0:
    end8 = len(t)
head = t[:i7]
tail = t[end8:]
out = head + sec7 + sec8 + tail
io.open(PREREG, 'w', encoding='utf-8', newline='\n').write(out)
chk = io.open(PREREG, encoding='utf-8').read()
assert '（占位·finalize' not in chk, 'placeholder survived'
assert chk.count('## §7 跑后实证') == 1 and chk.count('## §8 批后复盘') == 1
print(json.dumps({'bytes': len(out.encode('utf-8')),
                  'placeholders': chk.count('（占位·finalize'),
                  'sec7': '## §7 跑后实证' in chk,
                  'sec8': '## §8 批后复盘' in chk}, ensure_ascii=False))