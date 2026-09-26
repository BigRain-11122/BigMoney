# -*- coding: utf-8 -*-
# R264 (bm-a): T-73 s3 five-model verdict consolidation extractor
# Reads the five CN combo-model batch artifacts and prints a verdict matrix
# for the O-20260926-0926 CEO-facing consolidation ledger. Read-only.
import json
import sys

FILES = {
    'CN-REV-TILT': 'results/cn_rev_tilt/p1_results.json',
    'CN-DIV-LOWVOL-ROT': 'results/cn_div_lowvol_rot/p1_results.json',
    'CN-REGIME-POLICY': 'results/cn_regime_policy/p1_results.json',
    'CN-CORE-SATELLITE': 'results/cn_core_satellite/p1_results.json',
    'CN-CORE-DDCTL': 'results/cn_core_ddctl/p1_results.json',
}

out = {}
for name, f in FILES.items():
    d = json.load(open(f, encoding='utf-8-sig'))
    g1 = d.get('g1_prime_v2', {})
    g2 = d.get('g2_registration_v2', {})
    row = {'evidence_cutoff': d.get('evidence_cutoff'), 'cells': {}, 'baselines': {}}
    for cell in g1:
        a = g1[cell]
        b = g2.get(cell, {})
        sl = a.get('skill_line') or {}
        ci = a.get('bootstrap_ci') or {}
        tg = a.get('trade_gate') or {}
        x1 = (d.get('cells', {}).get(cell) or {}).get('x1') or {}
        yr = x1.get('yearly') or {}
        pos_years = sum(1 for v in yr.values() if isinstance(v, (int, float)) and v > 0)
        row['cells'][cell] = {
            'sharpe_full': a.get('sharpe_full'),
            'line': sl.get('line'),
            'line_ok': a.get('line_ok'),
            'pass_v2': a.get('pass_v2'),
            'ci95_low': ci.get('ci95_low'),
            'ci_lower_bound_positive': a.get('ci_lower_bound_positive'),
            'n_trades': tg.get('n_trades'),
            'dsr_ok': b.get('dsr_ok'),
            'family_pbo': b.get('family_pbo'),
            'pbo_ok': b.get('pbo_ok'),
            # allocation-lane reference reads (x1 cost face; NOT the frozen gate)
            'x1_ann_ret': x1.get('ann_ret'),
            'x1_max_dd': x1.get('max_dd'),
            'x1_calmar': (round(x1['ann_ret'] / abs(x1['max_dd']), 4)
                          if x1.get('ann_ret') is not None and x1.get('max_dd') not in (None, 0)
                          else None),
            'x1_pos_year_frac': (round(pos_years / len(yr), 3) if yr else None),
            'x1_oos_sharpe': (x1.get('oos') or {}).get('sharpe'),
        }
    for bn, bv in (d.get('baselines') or {}).items():
        row['baselines'][bn] = {
            k: bv.get(k) for k in ('sharpe', 'ann_ret', 'max_dd', 'n_trades')
            if isinstance(bv, dict) and k in bv
        }
    out[name] = row

print(json.dumps(out, ensure_ascii=False, indent=1))

# Direct file write (never via PS redirect -- R255 law: PS '>' re-encodes UTF-16)
if len(sys.argv) > 1 and sys.argv[1] == '--write':
    with open('results/_r264bma_cn_verdict_matrix.json', 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
        fh.write('\n')
    print('written: results/_r264bma_cn_verdict_matrix.json')
