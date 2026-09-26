# _r254bma_da_compare.py -- T-82 dA basis-swap adjudication: semantic row-level comparison
# bm-b originals (transfer/t80-da-basis, sha-verified) vs bm-a local re-run t22 dA cells.
# Question: does the dA input-basis difference materially change p_ret/derived faces,
# i.e. is my landed T-80 battery run (consumed local re-run files) semantically faithful
# to bm-b's originals?  Per MSG-20260926-1530: integrity cross-check only; landed run
# stays prereg-conformant (pinned-path+census+passive-gate basis).
# Output: results/_r254bma_da_compare/verdict.json (+ stdout summary). Exit 0 = completed.
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MINE = os.path.join(HERE, '_r254bma_da_compare')
BMB = 'results/t54'
PAIRS = [
    ('base', 'cells_deep_base_dA.jsonl', 'mine_cells_deep_base_dA.jsonl'),
    ('x2', 'cells_deep_x2_dA.jsonl', 'mine_cells_deep_x2_dA.jsonl'),
]
KEY_FIELDS = ('trader', 'pos', 'start')
# all measurable fields on a cell row (schema-verified identical both sides)
MEAS_FIELDS = ('ret_6m', 'ret_12m', 'ret_24m', 'p_ret_6m', 'p_ret_12m', 'p_ret_24m',
               'sharpe_6m', 'sharpe_12m', 'sharpe_24m', 'dd_6m', 'dd_12m', 'dd_24m',
               'beat_6m', 'beat_12m', 'beat_24m', 'trades_6m', 'trades_12m', 'trades_24m',
               'n_listed')
FLAG_FIELDS = ('face', 'regime', 'partial_12m', 'partial_24m')

def load(path):
    rows = {}
    dup = 0
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            k = tuple(r[f] for f in KEY_FIELDS)
            if k in rows:
                dup += 1
            rows[k] = r
    return rows, dup

def main():
    out = {'tool': '_r254bma_da_compare.py', 'faces': {}, 'verdict': None}
    for face, bmb_name, mine_name in PAIRS:
        bmb_rows, bmb_dup = load(os.path.join(BMB, bmb_name))
        mine_rows, mine_dup = load(os.path.join(os.path.dirname(os.path.abspath(__file__)), MINE, mine_name))
        kb, km = set(bmb_rows), set(mine_rows)
        only_bmb, only_mine = sorted(kb - km), sorted(km - kb)
        common = kb & km
        f = {'bmb_rows': len(bmb_rows), 'mine_rows': len(mine_rows),
             'bmb_dup_keys': bmb_dup, 'mine_dup_keys': mine_dup,
             'only_in_bmb': len(only_bmb), 'only_in_mine': len(only_mine),
             'common_keys': len(common),
             'rows_identical': 0, 'rows_differ': 0,
             'field_diff_counts': {}, 'max_abs_diff': {}, 'flag_mismatch': {},
             'sample_diffs': []}
        for k in common:
            b, m = bmb_rows[k], mine_rows[k]
            row_differs = False
            for fl in FLAG_FIELDS:
                if b.get(fl) != m.get(fl):
                    f['flag_mismatch'][fl] = f['flag_mismatch'].get(fl, 0) + 1
                    row_differs = True
            for fl in MEAS_FIELDS:
                bv, mv = b.get(fl), m.get(fl)
                if bv is None and mv is None:
                    continue
                if isinstance(bv, bool) or isinstance(mv, bool):
                    if bv != mv:
                        f['field_diff_counts'][fl] = f['field_diff_counts'].get(fl, 0) + 1
                        row_differs = True
                    continue
                if (bv is None) != (mv is None):
                    f['field_diff_counts'][fl + '(nullpattern)'] = f['field_diff_counts'].get(fl + '(nullpattern)', 0) + 1
                    row_differs = True
                    continue
                d = abs(bv - mv)
                if d > 0:
                    f['field_diff_counts'][fl] = f['field_diff_counts'].get(fl, 0) + 1
                    if fl in f['max_abs_diff']:
                        if d > f['max_abs_diff'][fl][0]:
                            f['max_abs_diff'][fl] = (d, k)
                    else:
                        f['max_abs_diff'][fl] = (d, k)
                    if fl.startswith('p_ret') and len(f['sample_diffs']) < 10:
                        f['sample_diffs'].append({'key': list(k), 'field': fl, 'bmb': bv, 'mine': mv})
                    row_differs = True
            if row_differs:
                f['rows_differ'] += 1
            else:
                f['rows_identical'] += 1
        # float-formatting noise probe: if all diffs < 1e-9 they are repr-level noise
        eps_rows = 0
        for k in common:
            b, m = bmb_rows[k], mine_rows[k]
            any_gt_eps = False
            for fl in MEAS_FIELDS:
                bv, mv = b.get(fl), m.get(fl)
                if isinstance(bv, (int, float)) and isinstance(mv, (int, float)) and not isinstance(bv, bool):
                    if abs(bv - mv) > 1e-9:
                        any_gt_eps = True
                        break
                elif b.get(fl) != m.get(fl):
                    any_gt_eps = True
                    break
            if any_gt_eps:
                eps_rows += 1
        f['rows_diff_gt_1e-9'] = eps_rows
        # serialize max diff tuples
        f['max_abs_diff'] = {fl: [v[0], list(v[1])] for fl, v in f['max_abs_diff'].items()}
        out['faces'][face] = f
    base_f, x2_f = out['faces']['base'], out['faces']['x2']
    identical = (base_f['rows_differ'] == 0 and x2_f['rows_differ'] == 0
                 and base_f['only_in_bmb'] == 0 and x2_f['only_in_bmb'] == 0
                 and base_f['only_in_mine'] == 0 and x2_f['only_in_mine'] == 0)
    if identical:
        out['verdict'] = 'SEMANTICALLY_IDENTICAL'
    else:
        eps_clean = (base_f['rows_diff_gt_1e-9'] == 0 and x2_f['rows_diff_gt_1e-9'] == 0
                     and base_f['only_in_bmb'] == 0 and x2_f['only_in_bmb'] == 0
                     and base_f['only_in_mine'] == 0 and x2_f['only_in_mine'] == 0)
        out['verdict'] = 'FLOAT_NOISE_ONLY' if eps_clean else 'MATERIAL_DIFFERENCE'
    with open(os.path.join(MINE, 'verdict.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False, sort_keys=True)
    print('verdict:', out['verdict'])
    for face in ('base', 'x2'):
        f = out['faces'][face]
        print(f"face={face} rows bmb/mine={f['bmb_rows']}/{f['mine_rows']} common={f['common_keys']} "
              f"only_bmb={f['only_in_bmb']} only_mine={f['only_in_mine']} "
              f"identical={f['rows_identical']} differ={f['rows_differ']} gt1e-9={f['rows_diff_gt_1e-9']}")
        if f['field_diff_counts']:
            print('  field_diff_counts:', f['field_diff_counts'])
        for fl, (d, k) in sorted(f['max_abs_diff'].items(), key=lambda x: -x[1][0])[:8]:
            print(f"  max|d| {fl} = {d:.3e} @ {k}")
        if f['flag_mismatch']:
            print('  flag_mismatch:', f['flag_mismatch'])
    return 0

if __name__ == '__main__':
    sys.exit(main())
