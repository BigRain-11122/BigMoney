# r773 bm-b merge resolver: 19-UU window (origin behind-6 absorbed mid-push, r759 phantom-delete law face)
# Direction INVERTED vs r772: our S6 chain regen 11:23-11:26 newer than bm-c r616 11:20-11:22
#   -> snapshot faces = per-face ts-newer-wins (expected ours); two special union faces.
# Laws: r188/R208 union zero-loss, r140 same-ts tie -> ours(HEAD), r185 parse-verify before write,
#       r609 ours=HEAD: theirs=MERGE_HEAD: (commit blobs, add-collapse immune), r611 assertion-matches-form.
import subprocess, json, re, sys

def blob(ref, path):
    r = subprocess.run(['git', 'show', f'{ref}:{path}'], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

def ts_of(b):
    # JSON top-level ts probe
    try:
        o = json.loads(b)
        for k in ('generated_at','generated','ts','updated','asof','scan_ts','last_scan','now'):
            if isinstance(o, dict) and k in o and o[k]:
                return str(o[k])
    except Exception:
        pass
    # regex first ISO ts anywhere
    m = re.search(rb'20\d\d-\d\d-\d\d[T ]\d\d:\d\d:\d\d', b)
    return m.group(0).decode() if m else ''

def resolve_snapshot(path, report):
    ob, tb = blob('HEAD', path), blob('MERGE_HEAD', path)
    if ob is None and tb is None:
        report.append(f'{path}: BOTH MISSING skip')
        return
    if ob is None:
        open(path,'wb').write(tb); report.append(f'{path}: ours-missing -> theirs'); return
    if tb is None:
        report.append(f'{path}: theirs-missing -> ours (no-op)'); return
    if ob == tb:
        open(path,'wb').write(ob); report.append(f'{path}: identical -> ours'); return
    ots, tts = ts_of(ob), ts_of(tb)
    if ots >= tts:
        open(path,'wb').write(ob); report.append(f'{path}: ours newer ({ots} >= {tts})')
    else:
        open(path,'wb').write(tb); report.append(f'{path}: theirs newer ({tts} > {ots})')

report = []

# ---- special face 1: compute_audit.json (rolling-ledger ts-key union + latest take-new) ----
p = 'results/compute_audit.json'
ob, tb = blob('HEAD', p), blob('MERGE_HEAD', p)
o, t = json.loads(ob), json.loads(tb)
seen = {}
for e in o['history']:
    seen[str(e['ts'])] = e                    # ours first (r140 tie -> HEAD)
for e in t['history']:
    if str(e['ts']) not in seen:
        seen[str(e['ts'])] = e
merged_hist = sorted(seen.values(), key=lambda e: str(e['ts']))
latest = o['latest'] if str(o['latest'].get('ts','')) >= str(t['latest'].get('ts','')) else t['latest']
side = 'ours' if latest == o['latest'] else 'theirs'
ind = 1
try:
    ind = len(json.dumps(o, indent=4).split('\n')[1]) - len(json.dumps(o, indent=4).split('\n')[1].lstrip())
except Exception:
    pass
out = json.dumps({'latest': latest, 'history': merged_hist}, ensure_ascii=False, indent=ind)
if ob.endswith(b'\n'):
    out += '\n'
open(p, 'w', encoding='utf-8', newline='').write(out)
m2 = json.loads(open(p, encoding='utf-8').read())
assert len(m2['history']) == len(merged_hist), 'history roundtrip loss'
assert len(merged_hist) >= max(len(o['history']), len(t['history'])), 'union shrank'
report.append(f'{p}: history {len(o["history"])}+{len(t["history"])} -> {len(merged_hist)} ts-key union zero-loss; latest side={side} ts={latest.get("ts")}')

# ---- special face 2: regime_state.json (base = newer side; history asof-union + transitions identity-union) ----
p = 'results/regime_state.json'
ob, tb = blob('HEAD', p), blob('MERGE_HEAD', p)
o, t = json.loads(ob), json.loads(tb)
base_o = str(o.get('updated','')) >= str(t.get('updated',''))
merged = dict(o if base_o else t)              # state fields take-new
for k, keyfn in [('history', lambda e: str(e.get('asof',''))),
                 ('transitions', lambda e: json.dumps(e, sort_keys=True, ensure_ascii=False))]:
    a, b = (o.get(k,[]), t.get(k,[]))
    seen = {}
    for e in a + b:
        kk = keyfn(e)
        if kk not in seen:
            seen[kk] = e
    vals = list(seen.values())
    if k == 'history':
        vals = sorted(vals, key=lambda e: str(e.get('asof','')))
    merged[k] = vals
out = json.dumps(merged, ensure_ascii=False, indent=1)
if ob.endswith(b'\n'):
    out += '\n'
open(p, 'w', encoding='utf-8', newline='').write(out)
m2 = json.loads(open(p, encoding='utf-8').read())
assert len(m2['history']) >= max(len(o.get('history',[])), len(t.get('history',[]))), 'regime history union shrank'
report.append(f'{p}: base={"ours" if base_o else "theirs"} updated={merged.get("updated")}; history {len(o.get("history",[]))}+{len(t.get("history",[]))} -> {len(m2["history"])}; transitions -> {len(m2["transitions"])}')

# ---- 17 snapshot faces: per-face ts-newer-wins ----
snapshots = [
 'docs/daily_report/REPORT-2026-10-06.json',
 'docs/daily_report/REPORT-2026-10-06.md',
 'docs/live_usage/LIVE-2026-10-06.json',
 'docs/live_usage/LIVE-2026-10-06.md',
 'docs/live_usage/LIVE-latest.json',
 'docs/live_usage/LIVE-latest.md',
 'results/_attrition_guard_scan.json',
 'results/dashboard_status.js',
 'results/dashboard_status.json',
 'results/fundamental_b_layer_filter.json',
 'results/futures_update_status.json',
 'results/lhb_update_status.json',
 'results/scorecard_v1.json',
 'results/strategy_scorecard.json',
 'results/token_usage.json',
 'results/update_status.json',
]
for p in snapshots:
    resolve_snapshot(p, report)

# ---- marker sweep (r609 3rd law) on all resolved faces ----
allfaces = snapshots + ['results/compute_audit.json', 'results/regime_state.json']
bad = []
for p in allfaces:
    try:
        txt = open(p, 'rb').read().decode('utf-8', errors='replace')
    except OSError:
        bad.append((p, 'READ_FAIL')); continue
    for ln in txt.split('\n'):
        if ln.startswith('<<<<<<< ') or ln.startswith('>>>>>>> ') or ln.startswith('======='):
            bad.append((p, ln[:40])); break
if bad:
    print('MARKER SWEEP FAIL:', bad); sys.exit(2)
print('MARKER SWEEP: 18 faces clean')

for r in report:
    print(r)
print(f'RESOLVED: {len(report)} faces')
