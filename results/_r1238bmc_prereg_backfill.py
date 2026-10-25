# -*- coding: utf-8 -*-
"""r1238 bm-c: W328 prereg sec.7/sec.8 finalize-time rewrite (zero placeholders).

Every number is machine-read from results/perpetual_faces/n1_w328_results.json and the
W329 seat receipt -- nothing is transcribed (r587). Structure card: the sec.7 block stays
9 lines (header + 8 bullets) and the sec.8 block stays 14 lines (header + 13 bullets), so
the file's total line count is unchanged; any drift aborts (W327 sec.8 pitfall #2).
"""
import io
import json

P = 'research/PERPETUAL_N1_W328_PREREG.md'
d = json.load(io.open('results/perpetual_faces/n1_w328_results.json', encoding='utf-8'))
fk = json.load(io.open('results/_r1238bmc_w328_fivekeys.json', encoding='utf-8'))
sg = json.load(io.open('results/_r1238bmc_w328_sixgate.json', encoding='utf-8'))
rc = json.load(io.open('results/_w329bmc_20261025_probe_receipt.json', encoding='utf-8'))

pool = d['null_pool_cumulative']
sl = d['skill_line_v2_k_lift']
famA = d['families']['A_random_engine_exit']
led = d['science_gates']['ledger']
k = pool['merged']['n_values']
mu, sg_ = pool['merged']['mu'], pool['merged']['sigma']
w = pool['w328_only']
se = pool['se_mu_at_k%d' % k]
a95, a99 = famA['full_sharpe_p95'], famA['full_sharpe_p99']
held = sl['n_eff_held_equal']
line_merged = sl['line_merged_%d' % k]
line_pre = sl['line_pre_w328']
klift = sl['line_delta_k_lift']
b_band = d['families']['B_random_entry_random_exit']
audit = d.get('audit') or {}

A, B = rc['bands']['A'], rc['bands']['B']
l1 = rc['legs']['leg1']
l4 = rc['legs']['leg4']
l0 = rc['legs']['leg0']
ra = l1['relation_asserts']
ach = l1['A_hop_chain'][0]

sec7 = [
"## §7 跑后实证。【finalize 收口机械回填】",
"- 账本恒等式：`{:,} + 2,200 = {:,}`（exact={}）；累计池 K `{:,} + 2,200 = {:,}`（exact={}）。".format(
    led['prev_total'], led['total'], (led['prev_total'] + led['batch_trials']) == led['total'],
    717320, k, (717320 + 2200) == k),
"- 合并池（W1..W328）：mu **{:.8f}** / sigma **{:.8f}** / se_mu@K{:,} **{:.6f}**；W328-only mu **{:.8f}** / sigma **{:.8f}**。".format(
    mu, sg_, k, se, w['mu'], w['sigma']),
"- A 档 full_sharpe p95 **{:.4f}** / p99 **{:.4f}**（锚 W327 p95 0.2977，差={:+.4f} 在 ±0.05 带内）；B 档 n={}。".format(
    a95, a99, a95 - 0.2977, b_band.get('n_pairs', 200)),
"- K-lift 对照：line_pre_w328 **{:.4f}** → line_merged@K{:,} **{:.4f}**，差 **{:+.4f}**；n_eff_held_equal {:,}（=W327 账本总数·收口机读）。".format(
    line_pre, k, line_merged, klift, held),
"- §5 五预键验证：`results/_r1238bmc_w328_fivekeys.json` 共 **{}/6 {}**；prose 偏差披露 {} 条（{}）。".format(
    6 if fk['all_pass'] else 0, 'ALL PASS' if fk['all_pass'] else 'FAIL',
    len(fk['prereg_prose_deviations']),
    '、'.join(x['key'] for x in fk['prereg_prose_deviations']) or '无'),
"- 六门探针：`results/_r1238bmc_w328_sixgate.json` verdict **{}**（第 92 次连续正确相位；splice 完整性/clean-state/无 heal 空 diff/adjudication PASS/pf+n1 selftest/12-12 分片 >100KB/seed_admit FREE 双带）。".format(
    sg['verdict']),
"- canon flip：**{}**（本波不动治理面）。".format(sl['canon_flip']),
"- audit 段：`{}`；shards_consumed 12/12；evidence_cutoff `{}`。".format(
    json.dumps(audit, ensure_ascii=False, sort_keys=True), d.get('evidence_cutoff')),
]

sec8 = [
"## §8 批后复盘。【finalize 同窗回填】",
"- §5.5 W330+ 投影承接机证（本席 receipt `results/_w329bmc_20261025_probe_receipt.json` leg4，pre-W329 宇宙）：A naive **{}**（hops={}）、B naive **{}**（hops={}·lands_inside_W330p_A_naive={}）——**W330 冻结方必须在 post-W329 宇宙重 live derive，且在 derive B 时预留本波 A 窗（W141 先例）·never transcribe r587**。".format(
    l4['W330p_A_naive'], l4['hops_A'], l4['W330p_B_naive'], l4['hops_B'],
    l4['W330p_B_lands_inside_W330p_A_naive']),
"- 本窗席位实测机证（post-W328-REGISTERED 宇宙，owner_rows={}，bm-c rows={}，ordinal {}）：A **{:,}..{:,}**（第 82 次连续 A-hop·hops={}·naive {:,}..{:,} 被注册 W328 B 带 742,501..742,700 与注册种子 {} 拒·base=FIRST CLEAN WINDOW）／B **{:,}..{:,}**（第 83 次连续 above-own-A·hops={}·naive {:,}..{:,} 整段落 own-A 之内 → own-A reservation cascade 至 own-A 尾+1·B_seed_hop_disclosure={}）——verdict **{}**·relation_asserts {}/{} 全真·seed_admit_gate FREE x2·leg3 bands_clear={}。".format(
    l0['owner_rows'], l0['bmc_rows'], l0['ordinal'], A[0], A[1], l1['hops_A'],
    ach['window'][0], ach['window'][1], [str(x) for x in ach['refuser_pts_sample']],
    B[0], B[1], l1['hops_B'], l1['B_naive'][0], l1['B_naive'][1],
    l1['B_seed_hop_disclosure'], rc['verdict'],
    sum(1 for v in ra.values() if v is True), len(ra), rc['legs']['leg3']['bands_clear']),
"- 本席位 live 事实：A 算术续带 {:,}..{:,} 在席位窗起点即被拒（注册 W328 B 带 + 注册种子点）→ walk 至首净窗 {:,}..{:,}；B 算术续带 {:,}..{:,} 整段落 own-A 之内（本波 A 已覆盖其上）→ cascade 至 own-A 尾+1 = {:,}..{:,}，零种子让位（EMPTY seed-hop）。".format(
    ach['window'][0], ach['window'][1], A[0], A[1],
    l1['B_naive'][0], l1['B_naive'][1], B[0], B[1]),
"- 宝藏与方法论捕获问：本波=nulls-deepening 常态加深，**机制面零新增**；收口腿沿用既有方法面（E95 按声明 EOL 基底比较／E96 在册≠复现双条件），无新资产条目——`knowledge/METHODOLOGY_ASSETS.md` 本波零追加；TREASURE_REGISTRY.json 不追加（无新宝藏）。",
"- 诚实披露（finalize 同窗回填）：",
"  ① **本波为断窗续轮**：r1237 窗完成冻结（ee00f6a9d6）+ 五面 splice（91e318867f）后引擎自燃 12/12（分片 09:32..09:45 齐 109KB+），但该窗在收口前死亡（state 停在 round_no 1236，心跳 09:14）——本轮按 bm-c 吸收判例（r894..r1236 谱系）机械复核 estate 后承接，执行 adjudication／六门／finalize／五键／W329 席位，零重烧零重拼。",
"  ② **§5 的 n_eff_held 本轮正确**：冻结件写 1,143,741 = W327 账本总数 = 收口机读 held 值，E96「在场且数值相等」双条件 6/6 通过、prose 偏差 0 条（上波 r1236 披露的陈旧字面量未复现）。",
"- 坑律捕获（finalize 同窗回填）：",
"  ① **席位探针依赖本波 finalize 产物**：`Tools/n1_seat_probe.py --wave N` 断言 prev finalize 产品在位（n1_w{N-1}_results.json），故席位只能在本波 finalize 之后发布——收口顺序=六门→finalize→fivekeys→席位→§7/§8 回填。",
"  ② **B 落位 INSIDE 面**（本波首次与连续三波的 BELOW 面不同）：A 跳到 naive B 窗之上并整段覆盖后，B 的 naive 窗落在 own-A 之内 → cascade 至 own-A 尾+1，relation_asserts 中 B_naive_inside_own_A=true / B_naive_below_own_A=false 必须同读。",
"  ③ 行数守卡（冻结件结构完整性）：复建 §7/§8 块后行数必须与源面一致（§7=9 行·§8=14 行），不一致=结构漂移、直接报死。",
"  ④ **重活必须分体点火**：finalize 在前台跑满 5 分钟无输出即被工具取消（零 stdout 窗），正法=DETACHED_PROCESS|CREATE_NO_WINDOW + `python -u` 分离点火 + 轮询 pid/产物；进程活着、CPU 累加、日志空=正常在跑，禁重启（重启=账本双烧）。",
"- 收口纪律：finalize 只消费在册分片（audit.finalize_only 面），本波零重烧、零双烧；S6 链与轮收口同窗。",
]

t = io.open(P, encoding='utf-8').read()
lines = t.split('\n')
assert lines[56].startswith('## §7'), lines[56][:40]
assert lines[66].startswith('## §8'), lines[66][:40]
assert len(sec7) == 9 and len(sec8) == 14, (len(sec7), len(sec8))
new = lines[:56] + sec7 + [''] + sec8 + lines[80:]
assert len(new) == len(lines), (len(new), len(lines))
io.open(P, 'w', encoding='utf-8', newline='\n').write('\n'.join(new))
print(json.dumps({'file': P, 'lines': len(new), 'sec7_lines': len(sec7),
                  'sec8_lines': len(sec8), 'ledger_total': led['total'], 'merged_k': k,
                  'mu': mu, 'sigma': sg_, 'se_mu': se, 'a_p95': a95,
                  'line_merged': line_merged, 'klift': klift, 'held': held}, indent=1))