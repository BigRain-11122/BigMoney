import json
import subprocess

def stage(side, path):
    out = subprocess.run(['git', 'show', f':{side}:{path}'], capture_output=True)
    if out.returncode != 0:
        raise RuntimeError(f'stage {side} {path}: {out.stderr[:200]}')
    return out.stdout

def write_json(path, obj):
    txt = json.dumps(obj, ensure_ascii=False, indent=1) + '\n'
    json.loads(txt)  # r185: parse-validate before write-back
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(txt)

resolved = []
log = []

# ---------- 1) rolling-ledger: compute_audit.json (history union by (ts,machine)) ----------
p = 'results/compute_audit.json'
ours = json.loads(stage(2, p))
theirs = json.loads(stage(3, p))
h_ours = ours.get('history', [])
h_theirs = theirs.get('history', [])
merged = {}
for row in h_ours + h_theirs:
    key = (row.get('ts'), row.get('machine'))
    if key not in merged:
        merged[key] = row
union_rows = sorted(merged.values(), key=lambda r: r.get('ts', ''))
newest = union_rows[-1]
out = dict(theirs)  # snapshot fields = take-new (mine, 08:48:34 newest probe)
out['history'] = union_rows
write_json(p, out)
log.append(f'{p}: history union {len(h_ours)}+{len(h_theirs)} -> {len(union_rows)} (key (ts,machine), zero-loss); snapshot fields take-new theirs 08:48:34')
resolved.append(p)

# ---------- 2) rolling-ledger: regime_state.json (history union by asof; state take-new) ----------
p = 'results/regime_state.json'
ours = json.loads(stage(2, p))
theirs = json.loads(stage(3, p))
hm = {}
for row in ours.get('history', []) + theirs.get('history', []):
    hm[row.get('asof')] = row
tr = {}
for row in ours.get('transitions', []) + theirs.get('transitions', []):
    tr[row.get('asof', json.dumps(row, sort_keys=True))] = row
out = dict(theirs)  # take-new state fields (updated 08:48:42 newer)
out['history'] = sorted(hm.values(), key=lambda r: r.get('asof', ''))
out['transitions'] = sorted(tr.values(), key=lambda r: str(r.get('asof', '')))
write_json(p, out)
log.append(f'{p}: history union -> {len(out["history"])} rows, transitions union -> {len(out["transitions"])}; state fields take-new theirs 08:48:42')
resolved.append(p)

# ---------- 3) runnable_pool.json: entries union by id; same updated_at -> per-entry diff disclosed ----------
p = 'results/runnable_pool.json'
ours = json.loads(stage(2, p))
theirs = json.loads(stage(3, p))
e_ours = {e['id']: e for e in ours.get('entries', [])}
e_theirs = {e['id']: e for e in theirs.get('entries', [])}
diff_ids = [k for k in e_ours if k in e_theirs and e_ours[k] != e_theirs[k]]
only_ours = [k for k in e_ours if k not in e_theirs]
only_theirs = [k for k in e_theirs if k not in e_ours]
log.append(f'{p}: entries ours={len(e_ours)} theirs={len(e_theirs)} content-diff ids={diff_ids} only-ours={only_ours} only-theirs={only_theirs}')
merged_entries = {}
for eid in set(e_ours) | set(e_theirs):
    a, b = e_ours.get(eid), e_theirs.get(eid)
    if a is None:
        merged_entries[eid] = b
    elif b is None:
        merged_entries[eid] = a
    else:
        # same-second tie -> HEAD (ours=bm-c r206) per r140; but prefer done-flip owner content if only one is done
        if a.get('status') == 'done' and b.get('status') != 'done':
            merged_entries[eid] = a
        elif b.get('status') == 'done' and a.get('status') != 'done':
            merged_entries[eid] = b
        else:
            merged_entries[eid] = a  # r140 same-ts tie -> HEAD side
# preserve original entry order from theirs then append extras
order = [e['id'] for e in theirs.get('entries', [])] + [i for i in e_ours if i not in e_theirs]
out = dict(theirs)
out['entries'] = [merged_entries[i] for i in order if i in merged_entries]
out['updated_at'] = theirs.get('updated_at') or ours.get('updated_at')
write_json(p, out)
log.append(f'{p}: entries union -> {len(out["entries"])}; updated_at={out["updated_at"]}')
resolved.append(p)

# ---------- 4) snapshots: take-new (theirs newer on every probe) ----------
snapshots = {
    'results/scorecard_v1.json': ('generated',),
    'results/strategy_scorecard.json': ('generated',),
    'results/token_usage.json': ('generated',),
    'results/update_status.json': ('updated',),
    'results/futures_update_status.json': ('ts',),
    'results/lhb_update_status.json': ('updated',),
    'results/fundamental_b_layer_filter.json': ('updated',),
    'results/dashboard_status.json': (('meta', 'generated_at'),),
}
for p, keys in snapshots.items():
    o = json.loads(stage(2, p))
    t = json.loads(stage(3, p))
    def get(d, k):
        if isinstance(k, tuple):
            cur = d
            for kk in k:
                cur = cur.get(kk, {}) if isinstance(cur, dict) else {}
            return cur if cur else ''
        return d.get(k, '')
    vo = get(o, keys[0]); vt = get(t, keys[0])
    pick = t if str(vt) >= str(vo) else o
    side = 'theirs' if pick is t else 'ours'
    write_json(p, pick)
    log.append(f'{p}: take-new {side} (probe {vo} vs {vt})')
    resolved.append(p)

# ---------- 5) twin pairs: json probe take-side + same-side md byte copy ----------
twins = [
    ('docs/daily_report/REPORT-2026-09-29.json', 'docs/daily_report/REPORT-2026-09-29.md', 'generated_at'),
    ('docs/live_usage/LIVE-2026-09-29.json', 'docs/live_usage/LIVE-2026-09-29.md', 'generated'),
    ('docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md', 'generated'),
]
for jp, mp, key in twins:
    o = json.loads(stage(2, jp))
    t = json.loads(stage(3, jp))
    vo, vt = str(o.get(key, '')), str(t.get(key, ''))
    side = 3 if vt >= vo else 2
    write_json(jp, t if side == 3 else o)
    raw = stage(side, mp)
    with open(mp, 'wb') as f:
        f.write(raw)
    log.append(f'{jp}+{mp}: twin take {"theirs(bm-b)" if side == 3 else "ours(bm-c)"} (probe {vo} vs {vt}); md same-side byte-copy')
    resolved.append(jp)
    resolved.append(mp)

# ---------- 6) dashboard_status.js: whole-byte take-side by embedded generated_at ----------
p = 'results/dashboard_status.js'
ro, rt = stage(2, p), stage(3, p)
import re
def js_ts(b):
    m = re.search(rb'generated_at"?\s*:\s*"([^"]+)"', b)
    return m.group(1).decode() if m else ''
to, tt = js_ts(ro), js_ts(rt)
side = rt if tt >= to else ro
with open(p, 'wb') as f:
    f.write(side)
log.append(f'{p}: whole-byte take {"theirs(bm-b)" if side is rt else "ours(bm-c)"} (embedded {to} vs {tt})')
resolved.append(p)

print('=== RESOLVER LOG ===')
for l in log:
    print(l)
print('resolved files:', len(resolved))
for r in resolved:
    print(' -', r)
