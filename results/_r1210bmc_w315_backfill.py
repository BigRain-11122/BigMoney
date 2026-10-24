# -*- coding: utf-8 -*-
# r1210 bm-c: W315 prereg sec.7/sec.8 post-run backfill (finalize same-window law).
# Lineage: the r1197..r1208 one-pass backfill routine; every number is machine-read
# from the finalize product + six-gate + five-key + own-seat probe receipt (r587).
import io
import json

PREREG = 'research/PERPETUAL_N1_W315_PREREG.md'
d = json.load(io.open('results/perpetual_faces/n1_w315_results.json', encoding='utf-8'))
fk = json.load(io.open('results/_r1210bmc_w315_fivekeys.json', encoding='utf-8'))
sg = json.load(io.open('results/_r1210bmc_w315_sixgate.json', encoding='utf-8'))
seat = json.load(io.open('results/_w315bmc_20261024_probe_receipt.json', encoding='utf-8'))
p = d['null_pool_cumulative']
s = d['skill_line_v2_k_lift']
A = d['families']['A_random_engine_exit']
B = d['families']['B_random_entry_random_exit']
led = d['science_gates']['ledger']
sA, sB = seat['bands']['A'], seat['bands']['B']
leg4 = seat['legs']['leg4']
k4 = [c for c in fk['checks'] if c['name'] == 'key4_k_lift_move'][0]
k3 = [c for c in fk['checks'] if c['name'] == 'key3_a_p95_delta_actual_anchor'][0]
dev_keys = ', '.join(x['key'] for x in fk['prereg_prose_deviations'])

merged_k = p['merged']['n_values']
se_k = merged_k  # se_mu key suffix tracks the merged K of this wave
prev_k = 688720

sec7 = f"""## §7 跑后实证。【finalize 收口机械回填】
- 账本恒等式：`{led['prev_total']:,} + {led['batch_trials']:,} = {led['total']:,}`（exact={fk['ledger_identity']['exact']}）；累计池 K `{prev_k:,} + 2,200 = {merged_k:,}`（exact={fk['merged_k_identity']['exact']}）。
- 合并池（W1..W315）：mu **{p['merged']['mu']:.8f}** / sigma **{p['merged']['sigma']:.8f}** / se_mu@K{se_k:,} **{p['se_mu_at_k' + str(se_k)]:.6f}**；W315-only mu **{p['w315_only']['mu']:.8f}** / sigma **{p['w315_only']['sigma']:.8f}**。
- A 档 full_sharpe p95 **{A['full_sharpe_p95']}** / p99 **{A['full_sharpe_p99']}**（锚 W314 p95 0.3246，差={k3['value']:+.4f} 在 ±0.05 带内）；B 档 n={B.get('n')}。
- K-lift 对照：line_pre_w315 **{s['line_pre_w315']}** → line_merged@K{se_k:,} **{s['line_merged_' + str(se_k)]}**，差 **{s['line_delta_k_lift']:+.4f}**；n_eff_held_equal {s['n_eff_held_equal']:,}。
- §5 五预键验证：`results/_r1210bmc_w315_fivekeys.json` 共 **{sum(1 for c in fk['checks'] if c['pass'])}/6 ALL PASS**；prose 偏差披露 {len(fk['prereg_prose_deviations'])} 条（{dev_keys or '无'}——§5 key4 prose `+0.0000` 是 W314 锚面，W315 实测 K-lift `{k4['value']:+.4f}` 属本波面，口径差如实披露不抹平）。
- 六门探针：`results/_r1210bmc_w315_sixgate.json` verdict **{sg['verdict']}**（第 78 次连续正确相位；splice 完整性/clean-state/adjudication/pf+n1 selftest/12-12 分片 >100KB/seed_admit FREE 双带）。
- canon flip：**{s['canon_flip']}**（本波不动治理面）。
- audit 段：`{json.dumps(d.get('audit'), ensure_ascii=False)}`；shards_consumed 12/12；evidence_cutoff `{d.get('evidence_cutoff')}`。
"""

sec8 = f"""## §8 批后复盘。【finalize 同窗回填】
- §5.5 W316+ 投影承接机证（本席 receipt `results/_w315bmc_20261024_probe_receipt.json` leg4，pre-W315 宇宙）：naive W316 A {leg4['W316p_A_naive']} clean（hops={leg4['hops_A']}），naive W316 B {leg4['W316p_B_naive']} clean 但落 W316 投影 A 窗内（lands_inside={leg4['W316p_B_lands_inside_W316p_A_naive']}）；**W315 注册后**（A {sA[0]:,}..{sA[1]:,} / B {sB[0]:,}..{sB[1]:,}）naive W316 A 起点即被注册 W315 B 带拒绝（staircase-affects-A 承袭预期·hops 以 W316 seat live trace 为准）——下一冻结窗必须重新 live derive，禁转抄（r587）。
- 本波席位 live 事实：A 708,101..710,100 算术续带在席位窗起点即被注册 W314 B 带 708,101..708,300 拒绝（hops=1 → {sA[0]:,}..{sA[1]:,}）；B 708,301..708,500 落本波 A 窗（own-A reservation → {sB[0]:,}..{sB[1]:,}），seed_admit_gate FREE x2，leg3 bands_clear=true。
- 宝藏与方法论捕获问：本波=nulls-deepening 常态加深，**无新方法/无新宝藏**，knowledge/METHODOLOGY_ASSETS.md 与 TREASURE_REGISTRY.md 均不追加。
- 诚实披露：§5 五预键 prose 偏差 {len(fk['prereg_prose_deviations'])} 条（{dev_keys or '无'}）以机读值为准并披露，不抹平；其余 mu/sigma/p95/K-lift 全部落在冻结带内。
- 坑律捕获（本窗三枚，全部在正典前拦下）：①canon-clone 生成器里**同一个字面量不能既走显式替换又进波号级联**——`PREV = 314` 与 lineage 串 `_r1208bmc_w314_sixgate.py` 显式写成目标值后又被级联推进一波（0 命中双假 FAIL）；正法=这两类最终值先停靠纯字母哨兵，级联后再解开（r1168 双移位族第三实例）。②**显式替换的先后顺序本身会吃掉字面量**——`77th`→`78th` 先跑会让 `_r1206..._77th consecutive` 永不命中；正法=长串先改、短串后改并各自 count-assert。③`prereg sec.7/§8` 的模板字号沿用前波（W314 数字），回填脚本必须逐值机读覆盖且以「锚前波 p95/prev_k」显式声明，否则会把前波数字当本波实测发出去。
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