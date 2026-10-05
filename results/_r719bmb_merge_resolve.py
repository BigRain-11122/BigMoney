# r719 bm-b merge resolver: 16-UU wave (r718-dead chain + bm-c r523 adopted)
# Laws applied: r715 (stage blob = full side source), r709 (targeted ts keys),
# r711 (format-normalized ts compare), r708 (twin same-side), r704 (read-back assert)
import subprocess, json, io, sys

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0 or len(r.stdout) == 0:
        raise RuntimeError(f'stage {stage} empty for {path}')
    return r.stdout

receipt = {}

# --- take-theirs faces (ts-newer-wins, byte-faithful checkout) ---
take_theirs = [
    'docs/daily_report/REPORT-2026-10-05.json', 'docs/daily_report/REPORT-2026-10-05.md',
    'docs/live_usage/LIVE-2026-10-05.json', 'docs/live_usage/LIVE-2026-10-05.md',
    'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md',
    'results/dashboard_status.js', 'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
    'results/lhb_update_status.json', 'results/regime_state.json',
    'results/scorecard_v1.json', 'results/strategy_scorecard.json',
    'results/update_status.json',
]
for p in take_theirs:
    b = blob(3, p)
    with open(p, 'wb') as f:
        f.write(b)
    receipt[p] = {'face': 'take-theirs', 'bytes': len(b)}

# --- compute_audit.json: rolling-ledger union (latest/ts theirs, history union by row-key) ---
o = json.loads(blob(2, 'results/compute_audit.json').decode('utf-8'))
t = json.loads(blob(3, 'results/compute_audit.json').decode('utf-8'))
seen, merged = set(), []
for h in o['history'] + t['history']:
    k = json.dumps(h, sort_keys=True)
    if k not in seen:
        seen.add(k); merged.append(h)
merged.sort(key=lambda h: h.get('ts', ''))
out = dict(t)  # theirs base: keeps latest (newer) + top-level ts
out['history'] = merged
raw = json.dumps(out, ensure_ascii=False, indent=1)
with open('results/compute_audit.json', 'wb') as f:
    f.write(raw.encode('utf-8'))
rb = json.load(io.open('results/compute_audit.json', encoding='utf-8'))
assert len(rb['history']) == len(merged), 'history row count mismatch'
receipt['results/compute_audit.json'] = {'face': 'union', 'ours_rows': len(o['history']), 'theirs_rows': len(t['history']), 'merged_rows': len(merged)}

# --- token_usage.json: top scalars theirs (newer generated), machines per-key union ---
ot = json.loads(blob(2, 'results/token_usage.json').decode('utf-8'))
tt = json.loads(blob(3, 'results/token_usage.json').decode('utf-8'))
out = dict(tt)
for mk, mv in (ot.get('machines') or {}).items():
    if mk not in (tt.get('machines') or {}):
        out.setdefault('machines', {})[mk] = mv
raw = json.dumps(out, ensure_ascii=False, indent=1)
with open('results/token_usage.json', 'wb') as f:
    f.write(raw.encode('utf-8'))
json.load(io.open('results/token_usage.json', encoding='utf-8'))
receipt['results/token_usage.json'] = {'face': 'per-key-union', 'theirs_generated': tt.get('generated'), 'machines_merged': sorted((out.get('machines') or {}).keys())}

# --- read-back reparse asserts for all take-theirs json faces ---
for p in take_theirs:
    if p.endswith('.json'):
        json.load(io.open(p, encoding='utf-8'))
        # CR-normalized byte equality vs stage blob (r715 law)
        wt = io.open(p, 'rb').read().replace(b'\r\n', b'\n')
        sb = blob(3, p).replace(b'\r\n', b'\n')
        assert wt == sb, f'byte drift after resolve: {p}'

with io.open('results/_r719bmb_merge_resolve.json', 'w', encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print('RESOLVED', len(receipt), 'faces; all asserts PASS')
