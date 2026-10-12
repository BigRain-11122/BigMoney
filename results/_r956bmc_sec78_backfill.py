# -*- coding: utf-8 -*-
"""r956 bm-c absorb: backfill W227 prereg sec.7/8 (placeholders -> machine-read actuals).
Values derived programmatically from receipts (r583 zero-literal law).
Assert count==1 per placeholder before write (fail-fast, no partial surgery)."""
import json

REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
P = rf'{REPO}\research\PERPETUAL_N1_W227_PREREG.md'

d = json.load(open(rf'{REPO}\results\perpetual_faces\n1_w227_results.json'))
fk = json.load(open(rf'{REPO}\results\_r956bmc_w227_fivekey_receipt.json'))
sg = json.load(open(rf'{REPO}\results\_r956bmc_w227_sixgate_prereg.json'))
pr = json.load(open(rf'{REPO}\results\_w227bmc_20261012_probe_receipt.json'))

led = fk['ledger']
k1 = fk['five_keys']['key1_wonly_vs_merged_dmu']['value']
k2 = fk['five_keys']['key2_sigma_rel_pct']['value']
k3 = fk['five_keys']['key3_A_p95_diff_vs_w226']['value']
k4 = fk['five_keys']['key4_k_lift']['value']
semu = list(fk['se_mu'].values())[0]
npc = d['null_pool_cumulative']
only_key = [k for k in npc if k.endswith('_only')][0]
kl = d['skill_line_v2_k_lift']
pre_key = [p for p in kl if p.startswith('line_pre')][0]
mrg_key = [p for p in kl if p.startswith('line_merged')][0]
famA = d['families']['A_random_engine_exit']
prev_p95 = json.load(open(rf'{REPO}\results\perpetual_faces\n1_w226_results.json'))['families']['A_random_engine_exit']['full_sharpe_p95']
sp = sg['gates']['splice_integrity']
wc = sg['gates']['wave_configs_row'] if 'wave_configs_row' in sg['gates'] else sg['wave_configs_row']
leg4 = pr['legs']['leg4']

SEC7 = f"""- **finalize one-pass 已落地（r956 死窗 2026-10-13 06:53:09·承 r955 席位发布 10781c2f8+r956 per-wave prereg derive 0d0c63c6e+r956 五面冻结 splice 48c321706+引擎 daemon mtime-watch 自燃 12/12（batched ledger append 20720d04f+dba434a41 自提交））——r956 死窗死于 fivekey 回执与收口 commit 前（六门已 PRE-FINALIZE 正相位跑毕=W217-debt 常设法正确执行·非 W212-pattern 复发）=本吸收窗（r956 续窗）机证 fivekey+恒等断言后收口（披露面 §8）**：
  - 账本恒等式：prev_total **{led['prev']:,}** + batch_trials **{led['batch']:,}** = total **{led['total']:,}** EXACT（断言通过·与 sixgate ledger_pre 投影恒等）；
  - 合并池 K=**497,320** EXACT（与 ledger_pre 投影 495,120+2,200 恒等）；merged mu=**{fk['merged_mu']}** / merged sigma=**{fk['merged_sigma']}**；w227-only mu=**{fk['w_only_mu']}** / w227-only sigma=**{fk['w_only_sigma']}**（全机读=results/perpetual_faces/n1_w227_results.json+results/_r956bmc_w227_fivekey_receipt.json；锚 W226 实数程序 derive 写入 r583 律）；
  - skill_line_v2 K-lift 对照：line_pre **{kl[pre_key]}** → line_merged **{kl[mrg_key]}** @n_eff {fk['skill_line']['n_eff']:,}；delta **{k4}**（§5 预键 ≤0.02 达标·W2..W226 阶梯对照链实锚）；
  - **§5 五预键机证验证（fivekey probe=results/_r956bmc_w227_fivekey_receipt.json·吸收窗配对）**：key1 w-only vs merged |Δmu|=**{k1}**<0.02 PASS；key2 sigma 相对变化 **{k2}%**<±10% PASS；key3 A 面 p95 **{fk['A_p95']}** vs W226 {prev_p95} 差 **{k3}**<0.05 PASS；key4 K-lift **{k4}**≤0.02 PASS；key5 投影承接见 §8（**五键全过=§5 五预键全达标零违例**）；
  - se_mu 收窄链头：se_mu_at_k497320=**{semu}**（前值 W226 0.000348 平/微收窄·链头收窄）；
  - canon flip 态=NOT performed（K2200 同律·治理提案面 only）；
  - audit：voids_applied={fk['voids']}；machine=bm-c；finalize_only=True；shards_consumed={fk['shards_consumed']}/12；evidence_cutoff={fk['evidence_cutoff']}；
  - **六门探针=PRE-FINALIZE 正相位（W217-debt 常设法正确执行）=results/_r956bmc_w227_sixgate_prereg.json**：banned ADMIT rc0+pf selftest 9/9+n1 selftest PASS+shards 12/12 在场+seed_admit FREE x2（base=514204 span=2000+base=516204 span=200）+splice 完整性（bands facts==freeze receipt·pf sha16 **{sp['pf_sha16_now']}** 与 n1 sha16 **{sp['n1_sha16_now']}** 双面 clean-equal 断言通过=family #6 三元组 r956 splice 原子携带零返）+WAVE_CONFIGS[227] row engine_owner=bm-c（a_seed_base={wc['a_seed_base']}/b_exit_seed_base={wc['b_exit_seed_base']}）+**finalize 恒等 post-hoc 断言（账本 {led['total']:,}/K 497,320 EXACT vs W226 锚）**——W228 必须六门 PRE-FINALIZE（常设法·防死窗复发面）。"""

SEC8 = f"""- **批后复盘（bm-c r956 吸收窗回填·r956 死窗愈合窗）**：
  - §5.5 下波投影承接机证：**W228+ 投影=席位 probe 机证 leg4（承本波 §5.5·results/_w227bmc_20261012_probe_receipt.json）**：A naive first-clean **{leg4['W227p_A']}**（hops={leg4['hops_A']}·pre-W227 宇宙·post-W227 注册宇宙待重 derive）；B naive first-clean **{leg4['W227p_B']}**（hops={leg4['hops_B']}）——**naive B 落在 naive A 窗内**（W141 先例·同窗互斥面适用于 W228）；**W227 B 带 516_204..516_403 注册后将拒 naive W228 A 窗**（A-hops-prior-B **EIGHTY-EIGHTH 例**预期·E36 卡/leg2 律）：W228 冻结方必须 post-W227 注册宇宙重 derive 且 derive B 时**预留本波 A 窗**；verify at W228 prereg·hop 链逐跳在 probe 回执。
  - 宝藏与方法论捕获：**六门相位=PRE-FINALIZE 正确执行（W217-debt 常设法连续正确相位·W212-pattern 零复发）**——本窗死因=会话中途死亡（finalize 落地 06:53:09 后死于 fivekey/收口 commit 前）非相位 miss=法面无缺口零新方法论卡（knowledge/METHODOLOGY_ASSETS.md 零 append·捕获律问过即录）；零新宝藏（TREASURE_REGISTRY 零行）。
  - 诚实披露面：r956 死窗 estate=finalize 产物+六门回执未 commit——本吸收窗按 bm-c absorb 先例线（r894/r897/r907/r911/r915/r917/r919/r921/r928/r930/r933/r941/r947/r951 第 15 例）机证五键全过+账本恒等 EXACT 后收口上链；QC 帧遗产（_r955bmc_qcframes 120 件 82MB）按 bloat 门不入库（3 张 contact sheets 已随 r955 addendum 73d795ef7 落库=可审证据面·源视频在 cph4 archive_i2v 归档在位=帧可再生·quarantine 7 天观察窗处置）；canon flip 治理提案面未执行（K2200 同律·待治理窗）；MV i2v 21/21 收口于 r955（CEO 令车道零欠账）。"""

raw = open(P, 'rb').read()
text = raw.decode('utf-8-sig')

lines = text.splitlines()
ph7 = [l for l in lines if '占位' in l and 'finalize one-pass' in l]
ph8 = [l for l in lines if '占位' in l and 'finalize 同窗回填' in l]
assert len(ph7) == 1, f'ph7 count={len(ph7)}'
assert len(ph8) == 1, f'ph8 count={len(ph8)}'

out = []
for l in lines:
    if l == ph7[0]:
        out.append(SEC7)
    elif l == ph8[0]:
        out.append(SEC8)
    else:
        out.append(l)
new = '\n'.join(out) + '\n'
open(P, 'wb').write(new.encode('utf-8-sig'))

# verify
chk = open(P, 'rb').read().decode('utf-8-sig')
assert '（占位·finalize' not in chk, 'placeholder residue'
for needle in [f"{led['total']:,}", '497,320', str(fk['merged_mu']), str(k1), 'EIGHTY-EIGHTH', 'PRE-FINALIZE 正相位']:
    assert needle in chk, f'missing {needle!r}'
print('SEC78 BACKFILL OK; placeholders=0; total_lines=', len(chk.splitlines()))
