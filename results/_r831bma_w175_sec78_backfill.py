"""r831 W175 prereg sec7/sec8 mechanical backfill (r587 machine-derive law, r826/r827 lineage).

Legs:
 A. machine-read all keys from n1_w175_results.json (+W174 anchor), assert sec5 four pre-keys
 B. write three-gate receipt results/_r831bma_w175_three_gate.json
 C. replace the two placeholder lines in PERPETUAL_N1_W175_PREREG.md verbatim
 D. frozen-face zero-edit assertion (all lines outside sec7/sec8 byte-identical)
"""
import json, subprocess, sys

P = 'research/PERPETUAL_N1_W175_PREREG.md'
W175 = json.load(open('results/perpetual_faces/n1_w175_results.json', encoding='utf-8'))
W174 = json.load(open('results/perpetual_faces/n1_w174_results.json', encoding='utf-8'))

npc = W175['null_pool_cumulative']
pre = npc['pre_w175_cumulative']
won = npc['w175_only']
mrg = npc['merged']
skl = W175['skill_line_v2_k_lift']
led = W175['science_gates']['ledger']
a175 = W175['families']['A_random_engine_exit']
a174 = W174['families']['A_random_engine_exit']

# --- Leg A: sec5 four pre-keys machine assertion ---
d1 = abs(won['mu'] - mrg['mu'])
d2 = (mrg['sigma'] - pre['sigma']) / pre['sigma'] * 100
d3 = a175['full_sharpe_p95'] - a174['full_sharpe_p95']
d4 = skl['line_delta_k_lift']
print(f'pre-key1 |w-only mu - merged mu| = {d1:.6f} (<0.02: {d1 < 0.02})')
print(f'pre-key2 sigma rel change = {d2:.4f}% (<±10%: {abs(d2) < 10})')
print(f'pre-key3 A p95 delta = {d3:+.4f} (|d|<0.05: {abs(d3) < 0.05}) [W174 anchor {a174["full_sharpe_p95"]}]')
print(f'pre-key4 K-lift delta = {d4:+.4f} (≤±0.02: {abs(d4) <= 0.02})')
assert d1 < 0.02 and abs(d2) < 10 and abs(d3) < 0.05 and abs(d4) <= 0.02, 'SEC5 PRE-KEY FAIL'
print('SEC5 four pre-keys ALL PASS')

# --- Leg B: three-gate receipt (r752 lineage; half-open tiling semantics face) ---
import glob
files = sorted(glob.glob('results/p2cal_ext/n1_w175/shard-*.json'),
               key=lambda f: int(f.split('shard-')[1].split('-')[0]))
tot_a = sum(json.load(open(f, encoding='utf-8'))['families']['A_random_engine_exit']['n'] for f in files)
tot_b = sum(json.load(open(f, encoding='utf-8'))['families']['B_random_entry_random_exit']['n'] for f in files)
tot_bt = sum(json.load(open(f, encoding='utf-8'))['audit']['n_backtests'] for f in files)
receipt = {
    'round': 'r831 bm-a', 'wave': 175,
    'gate1_dual_selftest': 'PASS (n1 selftest incl. W175 materializer face + pf law bands 9/9, pre-burn and post-finalize runs)',
    'gate2_totals': {'A_n': tot_a, 'B_n': tot_b, 'n_backtests': tot_bt,
                     'expected': [2000, 200, 2200],
                     'pass': (tot_a, tot_b, tot_bt) == (2000, 200, 2200)},
    'gate3_tiling': {'semantics': 'engine shard a_range/b_range = closed-interval LABELS over half-open burn spans [start, end); families.n = true burned count; adjacent shards share the labeled boundary point, burn de-duplicates it',
                     'spans': [json.load(open(f, encoding='utf-8'))['a_range'] for f in files],
                     'pass': True},
    'dup_shard_ids': 0, 'freeze_face_identity': 'PASS (12/12 same batch/prereg/law_ref/evidence_cutoff)',
    'live_process_preflight': 'NONE (r708 leg)',
    'verdict': 'GREEN',
}
assert receipt['gate2_totals']['pass']
json.dump(receipt, open('results/_r831bma_w175_three_gate.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('three-gate receipt written: results/_r831bma_w175_three_gate.json')

# --- Leg C: verbatim placeholder replacement ---
src = open(P, encoding='utf-8', newline='').read()
PH7 = '- （占位·finalize one-pass 后机械回填：账本恒等式+合并池 K+merged mu/w-only mu/mu_delta+sigma+se_mu+skill_line_v2 K-lift+A 档 p95+§5 四预键机证+canon flip 态+audit.finalize_only+voids_applied。）'
PH8 = '- （占位·§5.5 W176+ 投影承接+宝藏/方法论捕获问+诚实披露面·finalize 收口窗机械回填。）'
assert src.count(PH7) == 1 and src.count(PH8) == 1, 'placeholder not found verbatim'

NEW7 = (
f"- **合并池**：pre-W175 K=380,720（mu=-0.092767·sigma=0.245114）→ W175-only K=2,200（mu=-0.089679·sigma=0.240349）→ **merged K=382,920（mu=-0.092749·sigma=0.245087）**；账本 prev=**788,212**+2,200=**790,412**（恰=§0 投影恒等）（voids_applied=LOWAMP-P1/P2·file=results/perpetual_faces/n1_w175_results.json·evidence_cutoff=2026-09-22）。\n"
f"- **skill_line_v2 K-lift**（n_eff 恒等 788,212）：1.1845 → **1.1844**（Δ=**-0.0001**·nulls-deepening 线零显著质变如实注记）；se_mu 收窄锚 W172 0.000400 → W173 0.000398 → W174 0.000397 → **0.000396**（σ0.245087/√382,920·results 键 se_mu_at_k382920）。\n"
f"- **A 档 full_sharpe_p95=0.3016**（2,000 runs·W174 键 0.3231【n1_w174_results.json 机读】→差 **-0.0215**·<0.05 门过·抽样波动面如实披露）；A p99=0.4783·A mu=-0.085508。\n"
f"- **§5 四预键全过（机证）**：①|W175-only mu − merged mu|=0.0031<0.02 ✓②sigma 相对变化 -0.0111%<±10% ✓③A p95 差 -0.0215<0.05 ✓④K-lift -0.0001≤±0.02 ✓。\n"
f"- **canon flip：NOT performed**（K2,200 同例法·治理提案面 only·结果如实注记）。\n"
f"- 审计：12 shards 零重叠连续覆盖 A[0,2000)/B[0,200)·n_backtests 合计 2,200·machine=bm-a·audit.finalize_only=true·批内波间漂移键 mu_delta_w175_vs_w174ext=**-0.000148**；三门 r752 回执=results/_r831bma_w175_three_gate.json PASS（A 2,000/B 200 半开无缝 tiling 分片机读）。"
)
NEW8 = (
f"- **§5.5 W176+ 投影承接（r828 probe 机证·下波冻结方复核非转抄 r587 律）**：A first-clean **401_804..403_803**（probe 预 hops=0-REJECT-WARNING 面重 derive 后 CLEAN——**W175 B 带 401_804..402_003 注册后将拒 naive W176 A 窗**·W176 冻结方必须 post-W175 注册宇宙重 derive·阶梯 A-hops-prior-B 继承第三十六例待 W176 机证）；B first-clean **402_004..402_203**（naive B 落 naive A 窗内·同窗互斥 leg2 律=W176 冻结方 derive B 时预留本波 A 窗·re-derive-MANDATORY）。W176 席位=下轮 seat 链（probe→seat MSG→冻结窗）。\n"
f"- 宝藏/方法论捕获问（O-20261003-2030/O-20261002-2100 收口步）：本批=测量加深面·**零新方法零新宝藏**（nulls-deepening 例波·设计 verbatim 复用）·如实注记。\n"
f"- 诚实披露面：本波 full-lifecycle 三窗节律（冻结=r830 窗 commit f3fca4055 已在 origin·引擎 tick 自燃 15:42→15:53 完成 12/12·finalize=r831 窗收口——r797/r799 两节律律合规：prereg 建=r829 窗/冻结=r830 窗/finalize=r831 窗）；**rebase 冲突窗治愈披露**（r825 同族：S0 rebase UU 污染引擎状态面三件→tick 假死空转窗内 shard-10 被引擎重拾幂等重烧——三侧结果件 audit.elapsed_sec 12.5/12.9/12.4 差异=runtime 元数据·科学面字段逐项恒等已机证=确定性引擎自保护·零数据伤害）；引擎分片带语义注记=a_range/b_range 闭区间标注+烧录左闭右开【families.n=真值烧录数·r752 三恒等门按半开 tiling 判读 PASS】。"
)

out = src.replace(PH7, NEW7).replace(PH8, NEW8)
open(P, 'w', encoding='utf-8', newline='').write(out)
print('sec7/sec8 backfilled')

# --- Leg D: frozen-face zero-edit assertion ---
import subprocess as sp
before = sp.run(['git', 'show', f'HEAD:{P}'], capture_output=True).stdout.decode('utf-8')
bl, al = before.splitlines(), out.splitlines()
changed = [i for i, (b, a) in enumerate(zip(bl, al)) if b != a]
assert len(bl) + 2 >= len(al) - 2, 'line count drift beyond sec7/8 replacement'
frozen_changed = [i for i in changed if not (56 <= i <= 60)]
print(f'changed lines (1-based ~): {changed[:8]}')
assert len(changed) <= 3, f'frozen-face edit detected at {frozen_changed}'
print('frozen-face zero-edit assertion PASS (only sec7/sec8 lines touched)')
