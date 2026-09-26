# -*- coding: utf-8 -*-
"""R280 bm-a S7 final rebase resolver: 14 UU double-close collision.

bm-b r282 close (da63dae1, S6 chain @00:23-25) vs my round close caacc85b
(S6 chain @00:27-29 = newer regeneration, all 12 snapshot faces MINE-win on
inner ts). Recipes per skill: rolling-ledger (compute_audit, regime_state) =
union history entries zero-loss + take-new state fields; everything else
(js-wrapper twin, snapshots, daily_report twin) = take-side whole bytes
(checkout --theirs = my side = newer), byte-exact per r280 blob law.
"""
import subprocess, json, io

def blob(rev, path):
    return subprocess.run(['git','show', f'{rev}:{path}'],
                          capture_output=True, check=True).stdout

LEDGERS = {
    'results/compute_audit.json': 'history',
    'results/regime_state.json': 'transitions',
}

for path, key in LEDGERS.items():
    raw_o = blob('HEAD', path)          # origin side (bm-b r282)
    raw_m = blob('REBASE_HEAD', path)   # my side (newer)
    o = json.loads(raw_o.decode('utf-8-sig'))
    m = json.loads(raw_m.decode('utf-8-sig'))
    lo, lm = o.get(key, []), m.get(key, [])
    seen, merged = set(), []
    for e in lm + lo:                    # mine first (newer), origin fills gaps
        k = json.dumps(e, sort_keys=True, ensure_ascii=False)
        if k not in seen:
            seen.add(k)
            merged.append(e)
    if len(merged) == len(set(json.dumps(e, sort_keys=True, ensure_ascii=False) for e in merged)):
        pass
    # order: preserve list-semantic (both producers append chronologically);
    # mine entries are later -> final order = origin entries then mine entries
    mo = {json.dumps(e, sort_keys=True, ensure_ascii=False) for e in lm}
    oo = {json.dumps(e, sort_keys=True, ensure_ascii=False) for e in lo}
    ordered = [e for e in lo if json.dumps(e, sort_keys=True, ensure_ascii=False) in oo - mo] + \
              [e for e in lm]
    # zero-loss check: merged set == union set
    assert {json.dumps(e, sort_keys=True, ensure_ascii=False) for e in ordered} == mo | oo, 'zero-loss'
    out = dict(m)                        # newer top-level state = mine
    out[key] = ordered
    s = json.dumps(out, ensure_ascii=False, indent=1)
    eol = '\r\n' if b'\r\n' in raw_m else '\n'
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(s.replace('\n', eol) if eol == '\r\n' else s)
    if raw_m.endswith(b'\n') and not s.endswith('\n'):
        pass
    chk = json.loads(io.open(path, encoding='utf-8-sig').read())
    print(path, '|', key, ': origin', len(lo), '+ mine', len(lm),
          '-> union', len(chk[key]))

# snapshots + twins: byte-exact take-side (mine = newer ts, verified above)
SNAP = [
    'results/dashboard_status.json', 'results/dashboard_status.js',
    'results/strategy_scorecard.json', 'results/scorecard_v1.json',
    'results/token_usage.json', 'results/update_status.json',
    'results/futures_update_status.json', 'results/heat_update_status.json',
    'results/lhb_update_status.json', 'results/fundamental_b_layer_filter.json',
    'docs/daily_report/REPORT-2026-09-27.json', 'docs/daily_report/REPORT-2026-09-27.md',
]
for p in SNAP:
    r = subprocess.run(['git', 'checkout', '--theirs', p], capture_output=True)
    assert r.returncode == 0, (p, r.stderr.decode()[:200])
    print('take-side(mine):', p)
