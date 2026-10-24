# -*- coding: utf-8 -*-
# r1201 bm-c: W311 prereg sec.7/sec.8 post-run backfill (finalize same-window law).
# Lineage: the r1197/r1198/r1199 one-pass backfill routine; every value is machine-read
# from the finalize product + the six-gate + five-key + W312 seat receipts (zero
# transcription, r587).
import io
import json

PREREG = 'research/PERPETUAL_N1_W311_PREREG.md'
d = json.load(io.open('results/perpetual_faces/n1_w311_results.json', encoding='utf-8'))
fk = json.load(io.open('results/_r1201bmc_w311_fivekeys.json', encoding='utf-8'))
sg = json.load(io.open('results/_r1201bmc_w311_sixgate.json', encoding='utf-8'))
seat = json.load(io.open('results/_w312bmc_20261024_probe_receipt.json', encoding='utf-8'))
p = d['null_pool_cumulative']
s = d['skill_line_v2_k_lift']
A = d['families']['A_random_engine_exit']
B = d['families']['B_random_entry_random_exit']
led = d['science_gates']['ledger']
sA, sB = seat['bands']['A'], seat['bands']['B']
leg4 = seat['legs']['leg4']

sec7 = f"""## §7 跑后实证。【finalize 收口机械回填】
- 账本恒等式：`{led['prev_total']:,} + {led['batch_trials']:,} = {led['total']:,}`（exact={fk['ledger_identity']['exact']}）；累计池 K `679,920 + 2,200 = {p['merged']['n_values']:,}`（exact={fk['merged_k_identity']['exact']}）。
- 合并池（W1..W311）：mu **{p['merged']['mu']:.8f}** / sigma **{p['merged']['sigma']:.8f}** / se_mu@K682,120 **{p['se_mu_at_k682120']:.6f}**；W311-only mu **{p['w311_only']['mu']:.8f}** / sigma **{p['w311_only']['sigma']:.8f}**。
- A 档 full_sharpe p95 **{A['full_sharpe_p95']}** / p99 **{A['full_sharpe_p99']}**（锚 W310 p95 {0.302}，差={fk['checks'][3]['value']:.4f} 在 ±0.05 带内）；B 档 n={B.get('n')}。
- K-lift 对照：line_pre_w311 **{s['line_pre_w311']}** → line_merged@K682,120 **{s['line_merged_682120']}**，差 **{s['line_delta_k_lift']:+.4f}**；n_eff_held_equal {s['n_eff_held_equal']:,}。
- §5 五预键验证：`results/_r1201bmc_w311_fivekeys.json` 共 **{sum(1 for c in fk['checks'] if c['pass'])}/6 ALL PASS**；prose 偏差披露 {len(fk['prereg_prose_deviations'])} 条（key5 se_mu prose 0.000298 vs W310 实测 0.000297——如实披露不抹平）。
- 六门探针：`results/_r1201bmc_w311_sixgate.json` verdict **{sg['verdict']}**（第 74 次连续正确相位；splice 完整性/clean-state/adjudication/pf+n1 selftest/12-12 分片 >100KB/seed_admit FREE 双带）。
- canon flip：**{s['canon_flip']}**（本波不动治理面）。
- audit 段：`{json.dumps(d.get('audit'), ensure_ascii=False)}`；shards_consumed 12/12；evidence_cutoff `{d.get('evidence_cutoff')}`。
"""

sec8 = f"""## §8 批后复盘。【finalize 同窗回填】
- §5.5 W312+ 投影承接机证：naive W312 A 701_501..703_500 被注册 W311 A 带内起点拒绝（hops=1，前移至 {sA[0]:,}..{sA[1]:,}）；naive W312 B 701_701..701_900 落本波 A 窗内（own-A reservation，jump 至 {sB[0]:,}..{sB[1]:,}）——席位已 live re-derive 并 ADMIT（`results/_w312bmc_20261024_probe_receipt.json`，seed_admit_gate FREE x2，leg3 bands_clear=true），禁转抄（r587）。
- W313 投影（`leg4`，pre-W312 宇宙）：A naive {leg4['W313p_A_naive']} clean；B naive {leg4['W313p_B_naive']} clean 但落 W313 投影 A 窗内——下一冻结窗必须重新 live derive。
- 宝藏与方法论捕获问：本波=nulls-deepening 常态加深，**无新方法/无新宝藏**，knowledge/METHODOLOGY_ASSETS.md 与 TREASURE_REGISTRY.md 均不追加。
- 诚实披露：§5 五预键 1 条 prose 偏差（key5 se_mu 0.000298 vs 0.000297），以机读值为准并披露，不抹平；其余 mu/sigma/K-lift 全部落在冻结带内。
- 坑律捕获：本波 finalize 首跑以 `python scripts/perpetual_faces_n1.py --wave 311 finalize` 在工具内静默跑满 5 分钟被工具取消（零输出=零心跳），改 `python -u` 即正常出流——**多腿/长活驱动一律 python -u**（r1186 族第二现）；canon-clone 生成器再踩「SPECIAL 常量被波号级联二次前移」坑（`w310_seg` 被 '310'→'311' 改写致 NameError），正法=哨兵占位、级联后再落常量（r1184 族新实例）。
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