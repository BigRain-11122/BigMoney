# r92 bm-c: rebase multi-UU resolver vs bm-a r339 (same-window S6 shared faces)
# Doctrine: during rebase :2:=ours=upstream(bm-a r339), :3:=theirs=replayed commit (bm-c r92, later 17:34 run).
#   (a) same-day regenerable derived faces -> take :3: byte-faithful (r85 take-new doctrine)
#   (b) rolling ledgers (autofill launches, compute_audit history) -> entry-level union, ts sort, take-new last_tick
#   (c) update_status.json aggregate -> ts-aware key-level merge (both machines' lane states kept, newer per entry)
# Stage blobs :2:/:3: die after git add of that path (r90/r91 law) -> all reads BEFORE any add.
import json, subprocess, sys

def stage(side, path):
    p = subprocess.run(['git', 'show', f':{side}:{path}'], capture_output=True)
    if p.returncode != 0:
        print(f'FATAL git show :{side}:{path} rc={p.returncode}'); sys.exit(2)
    return p.stdout.decode('utf-8')

TAKE_MINE = [
    'docs/daily_report/REPORT-2026-09-27.json',
    'docs/daily_report/REPORT-2026-09-27.md',
    'results/dashboard_status.js',
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/heat_update_status.json',
    'results/lhb_update_status.json',
    'results/regime_state.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/token_usage.json',
]

for p in TAKE_MINE:
    txt = stage(3, p)
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(txt)
    print(f'take-3(mine-newer): {p} {len(txt)}B')

# --- autofill_state.json: launches union + last_tick take-new (r91 canon, stage-blob sides) ---
p = 'results/autofill_state.json'
a, b = json.loads(stage(2, p)), json.loads(stage(3, p))
la, lb = a.get('launches', []), b.get('launches', [])
canon = lambda e: json.dumps(e, sort_keys=True, ensure_ascii=False)
seen, union = set(), []
for e in la + lb:
    k = canon(e)
    if k not in seen:
        seen.add(k); union.append(e)
union.sort(key=lambda e: str(e.get('ts', '')))
cap = max(len(la), len(lb), 48)
trimmed = union[-cap:] if len(union) > cap else union
ta, tb = a.get('last_tick'), b.get('last_tick')
ts_of = lambda x: str(x.get('ts', '')) if isinstance(x, dict) else str(x or '')
last_tick = ta if ts_of(ta) >= ts_of(tb) else tb
with open(p, 'w', encoding='utf-8', newline='') as f:
    json.dump({'launches': trimmed, 'last_tick': last_tick}, f, ensure_ascii=False, indent=1); f.write('\n')
print(f'autofill: {len(la)}|{len(lb)} union={len(union)} kept={len(trimmed)} last_tick={ts_of(last_tick)}')

# --- compute_audit.json: history entry union (canonical dedup, ts sort) ---
p = 'results/compute_audit.json'
a, b = json.loads(stage(2, p)), json.loads(stage(3, p))
ha, hb = a.get('history', []), b.get('history', [])
seen, union = set(), []
for e in ha + hb:
    k = canon(e)
    if k not in seen:
        seen.add(k); union.append(e)
union.sort(key=lambda e: str(e.get('ts', e.get('asof', ''))))
out = dict(a); out['history'] = union
for k in b:
    if k not in out and k != 'history':
        out[k] = b[k]
with open(p, 'w', encoding='utf-8', newline='') as f:
    json.dump(out, f, ensure_ascii=False, indent=1); f.write('\n')
print(f'compute_audit: {len(ha)}|{len(hb)} -> {len(union)}')

# --- update_status.json: ts-aware key-level merge (no lane-state loss) ---
p = 'results/update_status.json'
a, b = json.loads(stage(2, p)), json.loads(stage(3, p))
def ts_of_v(v):
    if isinstance(v, dict):
        for k in ('ts', 'asof', 'updated', 'updated_at', 'time'):
            if k in v and v[k] is not None:
                return str(v[k])
    return ''
def merge(x, y):
    if isinstance(x, dict) and isinstance(y, dict):
        out = dict(x)
        for k, v in y.items():
            out[k] = merge(x[k], v) if k in x else v
        return out
    if isinstance(x, list) and isinstance(y, list):
        seen2, u = set(), []
        for e in x + y:
            kk = canon(e)
            if kk not in seen2:
                seen2.add(kk); u.append(e)
        return u
    tx, ty = ts_of_v(x), ts_of_v(y)
    if tx and ty:
        return y if ty >= tx else x
    return y if ty else (x if tx else y)
m = merge(a, b)
with open(p, 'w', encoding='utf-8', newline='') as f:
    json.dump(m, f, ensure_ascii=False, indent=1); f.write('\n')
print(f'update_status: merged keys={len(m)}')
print('ALL RESOLVED')
