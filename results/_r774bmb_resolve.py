# r774 bm-b rebase resolver: 18-UU window (dead-session recovery churn-absorb replayed onto
# origin tip where another machine's rebase rewrote the dead session's pushed r774 commits).
# Rebase stage semantics (vs r773 merge-mode): :2: = ours = rebase base = ORIGIN side (other machine),
#   :3: = theirs = MY replayed commit (bm-b chain faces 12:04:49 + QA). r764: raw stage segment ':2'/'%s:%s'.
# Tie rule (r140 rebase adaptation): exact ts tie -> stage-2 (already-landed base side).
# Laws: r188/R208 union zero-loss, r185 parse-verify before write, r100/R350 hardened probe
#   (normalized keys, ts-shaped values WITH time-of-day only, deep nested scan, staged blob probe),
#   r756 mixed-separator ts normalization (space->T, strptime numeric compare),
#   r98/r99/r100 twins take SAME side (group probe), R209 js-wrapper = whole-byte take-side.
import subprocess, json, re, sys
from datetime import datetime

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

def norm_ts(v):
    # r756: normalize space->T separator, strptime numeric compare
    s = str(v).strip().replace(' ', 'T', 1) if ' ' in str(v) else str(v)
    m = re.match(r'^(20\d\d-\d\d-\d\d)T(\d\d:\d\d)(?::(\d\d))?', s)
    if not m:
        return None
    try:
        return datetime.strptime(f"{m.group(1)}T{m.group(2)}:{m.group(3) or '00'}", '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        return None

def collect_ts(obj, out):
    # r311 deep-scan + r100 key normalization + R350 value-shape gate (time-of-day required)
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = str(k).replace('_', '').replace('-', '').lower()
            if isinstance(v, str) and any(nk.startswith(p) for p in ('generated', 'updated', 'scan', 'lastrun', 'lastscan', 'asof', 'now')):
                t = norm_ts(v)
                if t:
                    out.append(t)
            collect_ts(v, out)
    elif isinstance(obj, list):
        for e in obj:
            collect_ts(e, out)

def ts_of(b):
    cands = []
    try:
        collect_ts(json.loads(b), cands)
    except Exception:
        pass
    m = re.search(rb'20\d\d-\d\d-\d\d[T ]\d\d:\d\d:\d\d', b)
    if m:
        t = norm_ts(m.group(0).decode())
        if t:
            cands.append(t)
    return max(cands) if cands else None

def take(stage, path):
    b = blob(stage, path)
    open(path, 'wb').write(b)
    return b

report = []

def resolve_group(paths, probe_path, label):
    ob, tb = blob(2, probe_path), blob(3, probe_path)
    if ob is None and tb is None:
        report.append(f'{label}: BOTH MISSING skip'); return
    if ob is None:
        for p in paths: take(3, p)
        report.append(f'{label}: base-missing -> mine'); return
    if tb is None:
        report.append(f'{label}: mine-missing -> base (no-op)'); return
    ots, tts = ts_of(ob), ts_of(tb)
    if ots is None and tts is None:
        side = 2  # unprobeable: r140 tie -> base
    elif tts is None:
        side = 2
    elif ots is None:
        side = 3
    else:
        side = 3 if tts > ots else 2  # tie -> base (stage-2, already landed)
    for p in paths:
        b = take(side, p)
        if p.endswith('.json'):
            json.loads(b)  # r185 parse-verify
    report.append(f'{label}: side={"MINE(12:04:49 chain)" if side==3 else "ORIGIN-base"} ts_base={ots} ts_mine={tts}')

# ---- twin groups (r98/r99/r100: same side for all twins) ----
resolve_group(['docs/daily_report/REPORT-2026-10-06.json', 'docs/daily_report/REPORT-2026-10-06.md'],
              'docs/daily_report/REPORT-2026-10-06.json', 'REPORT-2026-10-06 twins')
resolve_group(['docs/live_usage/LIVE-2026-10-06.json', 'docs/live_usage/LIVE-2026-10-06.md',
               'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md'],
              'docs/live_usage/LIVE-2026-10-06.json', 'LIVE-* 4 twins')

# ---- single snapshot faces (incl. UNKNOWN _attrition_guard_scan.json = per-run evidence, newest scan wins) ----
for p in ['results/dashboard_status.js', 'results/dashboard_status.json',
          'results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
          'results/lhb_update_status.json', 'results/scorecard_v1.json',
          'results/strategy_scorecard.json', 'results/token_usage.json',
          'results/update_status.json', 'results/_attrition_guard_scan.json']:
    resolve_group([p], p, p)

# ---- union face 1: compute_audit.json (history ts-key union zero-loss + latest take-new) ----
p = 'results/compute_audit.json'
ob, tb = blob(2, p), blob(3, p)
o, t = json.loads(ob), json.loads(tb)
seen = {}
for e in o['history']:
    seen[str(e['ts'])] = e                    # base first (tie -> base)
for e in t['history']:
    if str(e['ts']) not in seen:
        seen[str(e['ts'])] = e
merged_hist = sorted(seen.values(), key=lambda e: str(e['ts']))
ol, tl = o['latest'], t['latest']
latest, side = (ol, 'base') if norm_ts(ol.get('ts', '')) >= norm_ts(tl.get('ts', '')) else (tl, 'mine')
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

# ---- union face 2: regime_state.json (state take-new by updated; history asof-union; transitions identity-union) ----
p = 'results/regime_state.json'
ob, tb = blob(2, p), blob(3, p)
o, t = json.loads(ob), json.loads(tb)
base_is_2 = norm_ts(o.get('updated', '')) >= norm_ts(t.get('updated', ''))
merged = dict(o if base_is_2 else t)
for k, keyfn in [('history', lambda e: str(e.get('asof', ''))),
                 ('transitions', lambda e: json.dumps(e, sort_keys=True, ensure_ascii=False))]:
    seen = {}
    for e in (o.get(k, []) + t.get(k, [])):
        kk = keyfn(e)
        if kk not in seen:
            seen[kk] = e
    vals = list(seen.values())
    if k == 'history':
        vals = sorted(vals, key=lambda e: str(e.get('asof', '')))
    merged[k] = vals
out = json.dumps(merged, ensure_ascii=False, indent=1)
if ob.endswith(b'\n'):
    out += '\n'
open(p, 'w', encoding='utf-8', newline='').write(out)
m2 = json.loads(open(p, encoding='utf-8').read())
assert len(m2['history']) >= max(len(o.get('history', [])), len(t.get('history', []))), 'regime history union shrank'
report.append(f'{p}: base={"ORIGIN" if base_is_2 else "MINE"} updated={merged.get("updated")}; history {len(o.get("history", []))}+{len(t.get("history", []))} -> {len(m2["history"])}; transitions -> {len(m2["transitions"])}')

# ---- marker sweep (r609 3rd law) over all 18 resolved faces ----
allfaces = ['docs/daily_report/REPORT-2026-10-06.json', 'docs/daily_report/REPORT-2026-10-06.md',
            'docs/live_usage/LIVE-2026-10-06.json', 'docs/live_usage/LIVE-2026-10-06.md',
            'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md',
            'results/dashboard_status.js', 'results/dashboard_status.json',
            'results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
            'results/lhb_update_status.json', 'results/scorecard_v1.json',
            'results/strategy_scorecard.json', 'results/token_usage.json',
            'results/update_status.json', 'results/_attrition_guard_scan.json',
            'results/compute_audit.json', 'results/regime_state.json']
bad = []
for p in allfaces:
    txt = open(p, 'rb').read().decode('utf-8', errors='replace')
    for ln in txt.split('\n'):
        if ln.startswith('<<<<<<< ') or ln.startswith('>>>>>>> ') or ln.startswith('======='):
            bad.append((p, ln[:40])); break
if bad:
    print('MARKER SWEEP FAIL:', bad); sys.exit(2)
print('MARKER SWEEP: 18 faces clean')

for r in report:
    print(r)
print(f'RESOLVED: {len(report)} faces')
