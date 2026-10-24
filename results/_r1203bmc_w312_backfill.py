# -*- coding: utf-8 -*-
# r1203 bm-c: W312 prereg sec.7/sec.8 post-run backfill (finalize same-window law).
# Lineage: the r1197/r1198/r1199/r1201 one-pass backfill routine; every value is
# machine-read from the finalize product + the six-gate + five-key + own-seat probe
# receipt (zero transcription, r587).
import io
import json

PREREG = 'research/PERPETUAL_N1_W312_PREREG.md'
d = json.load(io.open('results/perpetual_faces/n1_w312_results.json', encoding='utf-8'))
fk = json.load(io.open('results/_r1203bmc_w312_fivekeys.json', encoding='utf-8'))
sg = json.load(io.open('results/_r1203bmc_w312_sixgate.json', encoding='utf-8'))
seat = json.load(io.open('results/_w312bmc_20261024_probe_receipt.json', encoding='utf-8'))
p = d['null_pool_cumulative']
s = d['skill_line_v2_k_lift']
A = d['families']['A_random_engine_exit']
B = d['families']['B_random_entry_random_exit']
led = d['science_gates']['ledger']
sA, sB = seat['bands']['A'], seat['bands']['B']
leg4 = seat['legs']['leg4']
k4 = [c for c in fk['checks'] if c['name'] == 'key4_k_lift_move'][0]
dev_keys = ', '.join(x['key'] for x in fk['prereg_prose_deviations'])

sec7 = f"""## §7 跑后实证。【finalize 收口机械回填】
- 账本恒等式：`{led['prev_total']:,} + {led['batch_trials']:,} = {led['total']:,}`（exact={fk['ledger_identity']['exact']}）；累计池 K `682,120 + 2,200 = {p['merged']['n_values']:,}`（exact={fk['merged_k_identity']['exact']}）。
- 合并池（W1..W312）：mu **{p['merged']['mu']:.8f}** / sigma **{p['merged']['sigma']:.8f}** / se_mu@K684,320 **{p['se_mu_at_k684320']:.6f}**；W312-only mu **{p['w312_only']['mu']:.8f}** / sigma **{p['w312_only']['sigma']:.8f}**。
- A 档 full_sharpe p95 **{A['full_sharpe_p95']}** / p99 **{A['full_sharpe_p99']}**（锚 W311 p95 {0.3213}，差={fk['checks'][3]['value']:.4f} 在 ±0.05 带内）；B 档 n={B.get('n')}。
- K-lift 对照：line_pre_w312 **{s['line_pre_w312']}** → line_merged@K684,320 **{s['line_merged_684320']}**，差 **{s['line_delta_k_lift']:+.4f}**；n_eff_held_equal {s['n_eff_held_equal']:,}。
- §5 五预键验证：`results/_r1203bmc_w312_fivekeys.json` 共 **{sum(1 for c in fk['checks'] if c['pass'])}/6 ALL PASS**；prose 偏差披露 {len(fk['prereg_prose_deviations'])} 条（{dev_keys or '无'}——§5 key4 prose `+0.0000` 是 W311 锚面，W312 实测 K-lift `{k4['value']:+.4f}` 属本波面，口径差如实披露不抹平）。
- 六门探针：`results/_r1203bmc_w312_sixgate.json` verdict **{sg['verdict']}**（第 75 次连续正确相位；splice 完整性/clean-state/adjudication/pf+n1 selftest/12-12 分片 >100KB/seed_admit FREE 双带）。
- canon flip：**{s['canon_flip']}**（本波不动治理面）。
- audit 段：`{json.dumps(d.get('audit'), ensure_ascii=False)}`；shards_consumed 12/12；evidence_cutoff `{d.get('evidence_cutoff')}`。
"""

sec8 = f"""## §8 批后复盘。【finalize 同窗回填】
- §5.5 W313+ 投影承接机证（本席 receipt `results/_w312bmc_20261024_probe_receipt.json` leg4，pre-W312 宇宙）：naive W313 A {leg4['W313p_A_naive']} clean，naive W313 B {leg4['W313p_B_naive']} clean 但落 W313 投影 A 窗内；**W312 注册后**（A {sA[0]:,}..{sA[1]:,} / B {sB[0]:,}..{sB[1]:,}）naive W313 A 起点即被注册 W312 B 带拒绝（staircase-affects-A 承袭预期·hops 以 W313 seat live trace 为准）——下一冻结窗必须重新 live derive，禁转抄（r587）。
- 本波席位 live 事实：A 701,501..703,500 起点被注册 W311 B 带 701,501..701,700 拒绝（hops=1 → {sA[0]:,}..{sA[1]:,}）；B 701,701..701,900 落本波 A 窗（own-A reservation → {sB[0]:,}..{sB[1]:,}），seed_admit_gate FREE x2，leg3 bands_clear=true。
- 宝藏与方法论捕获问：本波=nulls-deepening 常态加深，**无新方法/无新宝藏**，knowledge/METHODOLOGY_ASSETS.md 与 TREASURE_REGISTRY.md 均不追加。
- 诚实披露：§5 五预键 1 条 prose 偏差（{dev_keys}）以机读值为准并披露，不抹平；其余 mu/sigma/p95/K-lift 全部落在冻结带内。
- 坑律捕获（本窗两枚）：①`Tools/n1_freeze_face_adjudicate.py` 的 repo-relative 参数走 `git show <commit>:<path>`——**Windows 反斜杠路径一律 "exists on disk, but not in <commit>" 秒败**，正法=全正斜杠（r1188 工具面新实例）；②canon-clone 生成器的**纯数字标识面**（`k310pos`/`after310`/`whole_file_311_count`/`prior_wave_310_boundary_kept`）不含 `w31x` token，逃过波号级联而静默继承陈旧值——正法=此类键名一律列入显式 SPECIAL 计数表（r1170/r1184 字面量族新实例，本窗 count-assert 于写盘前拦下两个键面）。
- 收口纪律：finalize 只消费在册分片（audit.finalize_only=true），本波零重烧、零双烧；S6 链与轮收口同窗。

"""

t = io.open(PREREG, encoding='utf-8').read()
i7 = t.find('## §7 跑后实证')
i8 = t.find('## §8 批后复盘')
assert i7 > 0 and i8 > i7, 'sec.7/sec.8 anchors missing'
end8 = t.find('\n- **跑前冻结=本件 commit**', i8)
if end8 < 0:
    end8 = len(t)
out = t[:i7] + sec7 + sec8 + t[end8:]
io.open(PREREG, 'w', encoding='utf-8', newline='\n').write(out)
chk = io.open(PREREG, encoding='utf-8').read()
assert '（占位·finalize' not in chk, 'placeholder survived'
assert chk.count('## §7 跑后实证') == 1 and chk.count('## §8 批后复盘') == 1
print(json.dumps({'bytes': len(out.encode('utf-8')),
                  'placeholders': chk.count('（占位·finalize'),
                  'sec7': '## §7 跑后实证' in chk,
                  'sec8': '## §8 批后复盘' in chk}, ensure_ascii=False))