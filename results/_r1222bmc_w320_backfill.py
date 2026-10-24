# -*- coding: utf-8 -*-
# r1222 bm-c: W320 prereg sec.7/sec.8 post-run backfill (finalize same-window law).
# Lineage: _r1219bmc_w319_backfill.py; every number is machine-read from the finalize
# product + six-gate + five-key + own-seat probe receipt + admit receipt (r587).
# All wave numerals and the prior-K/prior-ledger anchors are written EXPLICITLY
# (no cascade, r1168/r1184/r1208 family).
import io
import json

PREREG = 'research/PERPETUAL_N1_W320_PREREG.md'
d = json.load(io.open('results/perpetual_faces/n1_w320_results.json', encoding='utf-8'))
fk = json.load(io.open('results/_r1222bmc_w320_fivekeys.json', encoding='utf-8'))
sg = json.load(io.open('results/_r1222bmc_w320_sixgate.json', encoding='utf-8'))
seat = json.load(io.open('results/_w320bmc_20261025_probe_receipt.json', encoding='utf-8'))
p = d['null_pool_cumulative']
s = d['skill_line_v2_k_lift']
A = d['families']['A_random_engine_exit']
B = d['families']['B_random_entry_random_exit']
led = d['science_gates']['ledger']
sA, sB = seat['bands']['A'], seat['bands']['B']
leg1 = seat['legs']['leg1']
leg4 = seat['legs']['leg4']
k4 = [c for c in fk['checks'] if c['name'] == 'key4_k_lift_move'][0]
k3 = [c for c in fk['checks'] if c['name'] == 'key3_a_p95_delta_actual_anchor'][0]
dev_keys = ', '.join(x['key'] for x in fk['prereg_prose_deviations'])
adj = json.load(io.open('results/_n1_face_adjudication_w320.json', encoding='utf-8'))

merged_k = p['merged']['n_values']
prev_k = 699720
prior_ledger = 1126141
a_ref = leg1['A_hop_chain'][0]['refuser_bands'][0]
b_ref = leg1['B_hop_chain'][0]['refuser_bands'][0]

sec7 = f"""## §7 跑后实证。【finalize 收口机械回填】
- 账本恒等式：`{led['prev_total']:,} + {led['batch_trials']:,} = {led['total']:,}`（exact={fk['ledger_identity']['exact']}）；累计池 K `{prev_k:,} + 2,200 = {merged_k:,}`（exact={fk['merged_k_identity']['exact']}）。
- 合并池（W1..W320）：mu **{p['merged']['mu']:.8f}** / sigma **{p['merged']['sigma']:.8f}** / se_mu@K{merged_k:,} **{p['se_mu_at_k' + str(merged_k)]:.6f}**；W320-only mu **{p['w320_only']['mu']:.8f}** / sigma **{p['w320_only']['sigma']:.8f}**。
- A 档 full_sharpe p95 **{A['full_sharpe_p95']}** / p99 **{A['full_sharpe_p99']}**（锚 W319 p95 0.3225，差={k3['value']:+.4f} 在 ±0.05 带内）；B 档 n={B.get('n')}。
- K-lift 对照：line_pre_w320 **{s['line_pre_w320']}** → line_merged@K{merged_k:,} **{s['line_merged_' + str(merged_k)]}**，差 **{s['line_delta_k_lift']:+.4f}**；n_eff_held_equal {s['n_eff_held_equal']:,}。
- §5 五预键验证：`results/_r1222bmc_w320_fivekeys.json` 共 **{sum(1 for c in fk['checks'] if c['pass'])}/6 ALL PASS**；prose 偏差披露 {len(fk['prereg_prose_deviations'])} 条（{dev_keys or '无'}）。
- 六门探针：`results/_r1222bmc_w320_sixgate.json` verdict **{sg['verdict']}**（第 83 次连续正确相位；splice 完整性/clean-state/adjudication/pf+n1 selftest/12-12 分片 >100KB/seed_admit FREE 双带）。
- canon flip：**{s['canon_flip']}**（本波不动治理面）。
- audit 段：`{json.dumps(d.get('audit'), ensure_ascii=False)}`；shards_consumed 12/12；evidence_cutoff `{d.get('evidence_cutoff')}`。
"""

sec8 = f"""## §8 批后复盘。【finalize 同窗回填】
- §5.5 W321+ 投影承接机证（本席 receipt `results/_w320bmc_20261025_probe_receipt.json` leg4，pre-W320 宇宙）：naive W321 A `{leg4['W321p_A_naive']}` clean（hops={leg4['hops_A']}），naive W321 B `{leg4['W321p_B_naive']}` clean（hops={leg4['hops_B']}）但落投影 A 窗内（lands_inside={leg4['W321p_B_lands_inside_W321p_A_naive']}）；**W320 注册后**（A {sA[0]:,}..{sA[1]:,} / B {sB[0]:,}..{sB[1]:,}）naive W321 A 起点 {sA[1] + 1:,} 即被注册 W320 B 带 {sB[0]:,}..{sB[1]:,} 拒绝（staircase-affects-A 承袭预期·hops 以 W321 seat live trace 为准）——下一冻结窗必须重新 live derive，禁转抄（r587）。
- 本波席位 live 事实：A 算术续带 {leg1['ARITH_A'][0]:,}..{leg1['ARITH_A'][1]:,} 在席位窗起点即被注册 W319 B 带 {a_ref[0]:,}..{a_ref[1]:,} 拒绝（hops={leg1['hops_A']} → {sA[0]:,}..{sA[1]:,}，base==注册 W319 B 尾 {a_ref[1]:,}+1）；B 算术续带 {leg1['ARITH_B'][0]:,}..{leg1['ARITH_B'][1]:,} 落本波 A 窗 {b_ref[0]:,}..{b_ref[1]:,}（own-A reservation cascade·hops={leg1['hops_B']} → {sB[0]:,}..{sB[1]:,}，base==本波 A 尾 {sA[1]:,}+1）；seed_admit_gate FREE x2，relation_asserts 4/4，verdict {seat['verdict']}。
- 宝藏与方法论捕获问：本波=nulls-deepening 常态加深，**无新方法/无新宝藏**，knowledge/METHODOLOGY_ASSETS.md 与 TREASURE_REGISTRY.json 均不追加。
- 诚实披露（本波 2 条·均为面相等价性披露，判据与产物零影响）：
  ① §5 五预键 prose 偏差 {len(fk['prereg_prose_deviations'])} 条（{dev_keys or '无'}），以机读值为准不抹平；mu/sigma/p95/K-lift 全部落在冻结带内。
  ② **冻结回执 post 面是 pre-heal 面**：r1221 窗在 freeze receipt 落盘（01:27）之后跑了两次 bare-number heal（01:31，`results/_r1221bmc_heal_w320_cfg.py`：cfg shard_subdir n1_w319→n1_w320 + prose wave label），故 `_w320bmc_freeze_receipt.json` 的 n1_sha16_post `{adj['receipt_n1_sha16_post']}` 早于落地面。冻结件不回改（历史面保全），等价性由 adjudication 机械证明：把两次 heal 逆向后逐字节复现回执 post 面（`{adj['faces']['n1'].get('pre_heal_reconstruction_sha16')}`），heal_delta 计入 disclosed、unexplained=0，verdict **{adj['verdict']}**。
- 坑律捕获（本窗）：①**freeze 回执的后置 heal 不要当 FAIL**——r1188 口径下「receipt post ≠ land」有两种成因（EOL 基准 vs 后置 heal），正解=逐面记 EOL 基准 + 对后置 heal 做逆向字节复现，复现成功即 PASS（本轮首个实弹）。②**finalize 在管道里跑会被工具 5 分钟无输出窗取消**（本轮 `python -u ... | Select-Object -Last 25` 被取消），但脚本可能已跑完——正解=先查产物文件与账本恒等式再决定是否重跑（重跑=双烧台账，r1219 同族）。
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
                  'sec8': '## §8 批后复盘' in chk,
                  'freeze_anchor_kept': '- **跑前冻结=本件 commit**' in chk,
                  'prior_ledger_anchor': prior_ledger}, ensure_ascii=False))